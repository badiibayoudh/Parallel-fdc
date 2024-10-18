import os
import time
import tarfile
from datetime import datetime

import logging
logger = logging.getLogger('fdc_Manager')

def archive_and_cleanup(directory, archive_dir, days_to_archive=30, days_to_delete=120):
    logger.info('Archiving and cleanup vom : {}'.format(directory))
    
    """
    Archiviert Dateien, die älter als 'days_to_archive' Tage sind, in einer TAR.GZ-Datei,
    und löscht TAR.GZ-Archive, die älter als 'days_to_delete' Tage sind.
    
    :param directory: Das Verzeichnis, in dem nach Dateien gesucht wird.
    :param archive_dir: Das Verzeichnis, in das Dateien archiviert werden.
    :param days_to_archive: Die Anzahl der Tage, nach denen Dateien archiviert werden.
    :param days_to_delete: Die Anzahl der Tage, nach denen archivierte TAR.GZ-Dateien gelöscht werden.
    """
    # Stelle sicher, dass das Archivverzeichnis existiert
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    # Aktuelle Zeit
    now = time.time()

    # Erstelle eine TAR.GZ-Datei mit einem Zeitstempel im Namen
    archive_name = os.path.join(archive_dir, f"monitoring_fdc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz")

    with tarfile.open(archive_name, "w:gz") as archive:
        # Archivierung: Dateien älter als days_to_archive Tage packen
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)

            if os.path.isfile(file_path):
                # Dateialter berechnen
                file_age = (now - os.path.getmtime(file_path)) / (24 * 3600)

                # Archivieren, wenn älter als days_to_archive
                if file_age > days_to_archive:
                    archive.add(file_path, arcname=os.path.basename(file_path))
                    os.remove(file_path)
                    logger.info(f"Archiviert und gelöscht: {filename}")

    # Löschen: TAR.GZ-Archive, die älter als days_to_delete Tage sind, entfernen
    for archived_file in os.listdir(archive_dir):
        archived_file_path = os.path.join(archive_dir, archived_file)

        if os.path.isfile(archived_file_path):
            # Dateialter berechnen
            archived_file_age = (now - os.path.getmtime(archived_file_path)) / (24 * 3600)

            # Löschen, wenn älter als days_to_delete
            if archived_file_age > days_to_delete:
                os.remove(archived_file_path)
                logger.info(f"Gelöscht: {archived_file}")

# Beispiel: Verwendung der Funktion
directory_to_monitor = 'D:/git/Parallel-fdc/Testdaten/Monitoring'
archive_directory = 'D:/git/Parallel-fdc/Testdaten/Archive'

#archive_and_cleanup(directory_to_monitor, archive_directory)
