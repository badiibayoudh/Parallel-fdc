import os
import time
import tarfile
from datetime import datetime

import logging
logger = logging.getLogger('fdc_Manager')

def deleteFiles(verzeichnis, alter_in_tagen=30):
    jetzt = time.time()
    alter_in_sekunden = alter_in_tagen * 86400  # 86400 Sekunden pro Tag

    for wurzel, _, dateien in os.walk(verzeichnis):
        for datei in dateien:
            dateipfad = os.path.join(wurzel, datei)
            # Zeit der letzten Änderung der Datei
            letzte_aenderung = os.path.getmtime(dateipfad)

            # Datei löschen, wenn älter als das angegebene Alter
            if jetzt - letzte_aenderung > alter_in_sekunden:
                os.remove(dateipfad)
                logger.info(f"Deleted '{dateipfad}' ")
                
def dateien_auflisten(folder_path):
     file_paths = []
     for root, _, files in os.walk(folder_path):
         for f in files:
             file_paths.append(os.path.join(root, f))
 
     return file_paths

def direkt_dateien_auflisten(folder_path):
    file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                  if os.path.isfile(os.path.join(folder_path, f))]
    
    return file_paths

def archive_and_cleanup(directory, archive_dir, days_to_archive=30, days_to_delete=120, isRecursive=False, onlyLog=False):
    logger.info('Archiving and cleanup vom : {}'.format(directory))
    
    """
    Archiviert Dateien, die älter als 'days_to_archive' Tage sind, in einer TAR.GZ-Datei,
    und löscht TAR.GZ-Archive, die älter als 'days_to_delete' Tage sind.
    
    :param directory: Das Verzeichnis, in dem nach Dateien gesucht wird.
    :param archive_dir: Das Verzeichnis, in das Dateien archiviert werden.
    :param days_to_archive: Die Anzahl der Tage, nach denen Dateien archiviert werden.
    :param days_to_delete: Die Anzahl der Tage, nach denen archivierte TAR.GZ-Dateien gelöscht werden.
    """
    
    if not os.path.exists(directory):
        logger.error(f"Folder is not existing: {directory}")
        return
     
    try:
        # Prüfen, ob das Verzeichnis bereits existiert
        if not os.path.exists(archive_dir):
            # Erstellen des Verzeichnisses
            os.makedirs(archive_dir)
            logger.debug(f"Directory '{archive_dir}' created successfully.")
        else:
            logger.debug(f"Directory '{archive_dir}' already exists.")
    except Exception as e:
        logger.error(f"Error creating directory: {e}. Cleanup & Archiving could not be started")
        return

    # Aktuelle Zeit
    now = time.time()

    # Erstelle eine TAR.GZ-Datei mit einem Zeitstempel im Namen
    archive_name = os.path.join(archive_dir, f"monitoring_fdc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz")
    fileFound = False
    
    if isRecursive:
        logger.debug(f"Recursive listing '{isRecursive}'")
        files = dateien_auflisten(directory)
    else:
        logger.debug(f"Not recursive listing '{isRecursive}'")
        files = direkt_dateien_auflisten(directory)

    logger.debug(f"Files to be checked: {files}")

    with tarfile.open(archive_name, "w:gz") as archive:
        # Archivierung: Dateien älter als days_to_archive Tage packen
        #for filename in os.listdir(directory):
        for file_path in files:
            if onlyLog:
                if not (file_path.endswith('.log') or file_path.startswith('fdc_manager.log')):
                    continue
                    
            #file_path = os.path.join(directory, filename)

            if os.path.isfile(file_path):
                # Dateialter berechnen
                file_age = (now - os.path.getmtime(file_path)) / (24 * 3600)

                # Archivieren, wenn älter als days_to_archive
                if file_age > days_to_archive:
                    archive.add(file_path, arcname=os.path.basename(file_path))
                    os.remove(file_path)
                    fileFound = True
                    logger.info(f"Archived and deleted: {file_path}")

    if not fileFound:
        os.remove(archive_name)


    # Löschen: TAR.GZ-Archive, die älter als days_to_delete Tage sind, entfernen
    for archived_file in os.listdir(archive_dir):
        archived_file_path = os.path.join(archive_dir, archived_file)

        if os.path.isfile(archived_file_path):
            # Dateialter berechnen
            archived_file_age = (now - os.path.getmtime(archived_file_path)) / (24 * 3600)

            # Löschen, wenn älter als days_to_delete
            if archived_file_age > days_to_delete:
                os.remove(archived_file_path)
                logger.info(f"Deleted: {archived_file}")
