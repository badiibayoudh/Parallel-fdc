#############################################################
# Orchestration of FileDownloadClient (FDC)
#############################################################
# History
# -----------------------------------------------------------
# 29.07.2024    Badii Bayoudh   Initial Creation
# 19.08.2024    Juergen Marat   German -> English, Logfile renamed, New Jar fdc_v7_07_08_2024.jar
# 06.09.2024    Badii Bayoudh Adjust copy of plxml file + set the env variable for  FDC user log file path
# 17.09.2024    Badii Add Monitoring and retry when error
# 15.11.2024    Badii fdc execution is following alpabetical order of config file name
# 19.11.2024    Badii use yml + send mail + check sucess.xml & physical.xml + use env variables
#############################################################


import os
import sys
import glob

from subprocess import Popen, PIPE
import subprocess
from multiprocessing.pool import ThreadPool

from datetime import datetime
import time

import logging
from logging.handlers import TimedRotatingFileHandler

import config

import shutil

import reporter
import cleaner

settings = None
ERROR='error'
SUCCESS= 'Success'
result = []
result_retry = []
logger = logging.getLogger('fdc_Manager')

def execute_shell_script(script_path, config_name, log_path, mailing_list):
    """
    FÃƒÂ¼hrt ein Shell-Skript mit den angegebenen Argumenten aus.
    
    :param script_path: Pfad zum Shell-Skript
    :param config_name: Name der Konfiguration (als Argument fÃƒÂ¼r das Skript)
    :param log_path: Pfad zur Logdatei (als Argument fÃƒÂ¼r das Skript)
    :return: tuple (stdout, stderr, returncode)
    """
    command = ["bash", script_path, "--fdc_config", config_name, "--fdc_log", log_path, "--mail", mailing_list]
    logger.debug("Run mail command: {}".format(command))
    
    try:
        result = subprocess.run(
            command,
            check=False
        )
        return result.stdout, result.stderr, result.returncode
    except FileNotFoundError:
        raise Exception(f"Das Shell-Skript {script_path} wurde nicht gefunden.")
    except Exception as e:
        raise Exception(f"Fehler beim AusfÃƒÂ¼hren des Shell-Skripts: {str(e)}")
    
def sendMail(configFileName):
    if not settings["workflow"]["mailing"]["mail"]:
        logger.debug("Mailing is in the configuration disabled")
        exit

    configName, logFilePath = defineLogPath(configFileName)
    logger.debug('log File folder path: {}'.format(logFilePath))
    last_log = getLatestLog(logFilePath)
    logger.debug('last log to be sent in email: {}'.format(last_log))

    fdcLogFilePath = os.path.join(logFilePath, 'FDCUserLog.txt')
    #environment = settings["fdc"]["environment_to_connect"]

    if not os.path.isfile(last_log):
        logger.error('Path of FDC User log file is not found: {}'.format(last_log))
        exit

    stdout, stderr, returncode = execute_shell_script("send_fdc_mail.sh", configName, last_log, settings["workflow"]["mailing"]["mailing_list"])

    if returncode == 0:
        logger.debug("Email script successfully executed!")
        logger.debug("Output: {}".format(stdout))
    else:
        logger.error("Email script failed!")
        logger.error("Error output :".format(stderr))
        logger.error("Return code:".format(returncode))

# Collect the returned result when running the client
def collect_result(val):
    if val[1] == ERROR or not isPLMXMLSucessfullyDownloaded(val[0]) or not isJTsSucessfullyDownloaded(val[0]):
        return result.append((val[0], ERROR))
    return result.append(val)

# Collect the returned retry result when running the client
def collect_result_retry(val):
    if val[1] == ERROR or not isPLMXMLSucessfullyDownloaded(val[0]) or not isJTsSucessfullyDownloaded(val[0]):
        return result_retry.append((val[0], ERROR))
    return result.append(val)

def isPLMXMLSucessfullyDownloaded(configFileName):
    logger.info('Check Plmxml status file for configuration: {}'.format(configFileName))
    
    configName, logFilePath = defineLogPath(configFileName)
    plmxmlStatusFilePath = os.path.join(logFilePath, 'FDC.PLMXML.SUCCESS')
    
    ret = os.path.isfile(plmxmlStatusFilePath)
    if ret:
        logger.info('Plmxml status file exists : {}'.format(plmxmlStatusFilePath))
    else:
        logger.info('Plmxml status file not exists : {}'.format(plmxmlStatusFilePath))
    
    return ret
    
    
def isJTsSucessfullyDownloaded(configFileName):
    logger.info('Check Jt status file for configuration: {}'.format(configFileName))
    
    configName, logFilePath = defineLogPath(configFileName)
    jtStatusFilePath = os.path.join(logFilePath, 'FDC.PHYSICAL_FILES.SUCCESS')
    
    ret = os.path.isfile(jtStatusFilePath)
    if ret:
        logger.info('Jt status file exists : {}'.format(jtStatusFilePath))
    else:
        logger.info('JT status file not exists : {}'.format(jtStatusFilePath))
        
    return ret

    
def runClientInt(configFileName):
    if settings["workflow"]["simulate"]:
        return (configFileName, SUCCESS)
        
    configName, logFilePath = defineLogPath(configFileName)
    
    fdcLogFilePath = os.path.join(logFilePath, 'FDCUserLog.txt')
    logger.debug('Path FDC User log file: {}'.format(fdcLogFilePath))
    
    if os.path.isfile(fdcLogFilePath):
        os.remove(fdcLogFilePath)
        logger.info('Log file deleted: {}'.format(fdcLogFilePath))
    
    myenv = os.environ.copy()
    myenv['LOG_FILE_PATH'] = logFilePath
    myenv['LOGGING_FILE_NAME'] = configName
    myenv['FDC_RUN_STATUS_PATH'] = logFilePath
    myenv['USER_LOG_PATH'] = fdcLogFilePath
    
    myenv['ENVIRONMENT_TO_CONNECT'] = settings["fdc"]["environment_to_connect"]
    myenv['USERPID'] = settings["fdc"]["userpid"]
    
    myenv['FILE_DOWNLOAD_CLIENT_HOME'] = settings["fdc"]["file_download_client_home"]
    myenv['STATUS_CHECK_INTERVAL'] = str(settings["fdc"]["status_check_interval"])

    if not os.path.exists(logFilePath):
        os.makedirs(logFilePath)

    credentialsPath = settings["fdc"]["credentials"]
    configFilePath =  os.path.join(settings["fdc"]["xml_input_directory"], configFileName)
    downloadArgs1 ='--encryptedCredLocation=' + credentialsPath
    downloadArgs2 ='--inputFileLocation=' + configFilePath
    logger.info('downloadArgs:  {} , {} \n'.format(downloadArgs1, downloadArgs2))
    
    javaCmd = os.path.join(settings["fdc"]["java_path"], 'bin', 'java')
    fdcClientPath = os.path.join(settings["fdc"]["file_download_client_home"], 'fdc.jar')
    
    command = [javaCmd, '-Dfile.encoding=UTF-8', '-jar', fdcClientPath, 'download_mode', downloadArgs1, downloadArgs2]
    
    #command = [javaCmd, '-Dfile.encoding=UTF-8', '-jar', fdcClientPath, 'download_mode', downloadArgs1, downloadArgs2]
    # command = ['/applications/asplm/asplmint/cust_root_dir/cdm_importer/fdc/java/jdk-17.0.11/bin/javax', '-Dfile.encoding=UTF-8', '-jar', '/applications/asplm/asplmint/cust_root_dir/cdm_importer/fdc/fdc_v6_26_06_2024x.jar', 'download_mode', '--encryptedCredLocation=/applications/asplm/asplmint/cust_root_dir/cdm_importer/fdc/secure/EncryptedCred_PRODx.txt', '--inputFileLocation=/applications/asplm/asplmint/cust_root_dir/cdm_importer/fdc/configsPrd/AS_C223_FV_L_FDCx.xml']
    #command = ['ls']
    logger.info("Execute command: {}".format(command))
    
    try:
        complPr = subprocess.run(command, env=myenv, check=True)
        print(complPr.returncode)

    except:
         logger.exception("Exception while calling command: {}".format(command))
         return (configFileName, ERROR)
    
    ## check result with log
    logFile = getLatestLog(logFilePath)
    logger.debug('Last log file :  {} \n'.format(logFile))
    action = SUCCESS
    if os.path.exists(logFile):
        with open(logFile, 'r') as fp:
            for l_no, line in enumerate(fp):
                if 'FailedException' in line or 'Caused by:' in line:
                    logger.error('Failed exception in input config {} within FDC: {} \n'.format(configFileName, line))
                    logger.debug('Line Number: {}'.format( l_no))
                    logger.debug('Line: {}'.format( line))
                    # sendMail(configFileName, logFile)
                    action = ERROR
                    # don't look for next lines
                    return (configFileName, action)
    
 
    # Move plmxml in order to be imported
    # Annahme: plmml has same name as the configuration file
    if settings["workflow"]["plmxml"]["move"]:
        plmxmlfileName=configName+'.plmxml'
        plmxmlfileFrom= os.path.join(settings["workflow"]["plmxml"]["move_from"], plmxmlfileName)
        if os.path.exists(plmxmlfileFrom):
            #productTo= os.path.join(settings["workflow"]["plmxml"]["move_to"], 'fdc_'+product)
            #if not os.path.exists(productTo):
            #    os.makedirs(productTo)
            try:
                plmxmlfileTo= os.path.join(settings["workflow"]["plmxml"]["move_to"], plmxmlfileName)
                plmxmlfileToTemp= os.path.join(settings["workflow"]["plmxml"]["move_to"], plmxmlfileName + "_tmp")
                shutil.copy2(plmxmlfileFrom, plmxmlfileToTemp)
            
                os.replace(plmxmlfileToTemp, plmxmlfileTo)
                logger.info('Copy plmxml from: {} to: {}]'.format( plmxmlfileFrom, plmxmlfileTo))
            except:
                return (configFileName, ERROR)
    
    return (configFileName, action)

def defineLogPath(configFileName):
    # Get config name from the config file name
    configName = os.path.splitext(configFileName)[0]
    logger.debug('Name of input config: {}'.format(configName))
    
    product = configName.split('_')[1]
    logger.debug('Name of carline or powertrain: {}'.format(product))
    
    logFilePath = os.path.join(settings["log_output"], product, configName)
    logger.debug('Path log file: {}'.format(logFilePath))
    return configName,logFilePath


def runClient(configFileName):
    try:
        logger.info('>> Start of instance of FDC-Client with input config: {}\n'.format(configFileName))
        return runClientInt(configFileName)
    except:
        logger.exception('Error in FDC-Client with input config: {}'.format(configFileName))
        return (configFileName, ERROR)
    finally:
        logger.info('<< End of instance of FDC-Client with input config: {} \n'.format(configFileName))


def getLatestLog(logFolder):
    logPattern = os.path.join(logFolder, '*')
    list_of_files = glob.glob(logPattern) # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def list_xml_files_sorted(directory):
    try:
        # Liste aller XML-Dateien im angegebenen Pfad abrufen und nach Namen sortieren
        xml_files = sorted(
            [f for f in os.listdir(directory) if f.endswith('.xml') and os.path.isfile(os.path.join(directory, f))]
        )
        return xml_files
    except FileNotFoundError:
        logger.info(f"The directory '{directory}' was not found.")
        return []
    except PermissionError:
        logger.info(f"Access to directory '{directory}' is not allowed.")
        return []

def xml_dateinamen_auflisten(verzeichnis):
    """Listet die Namen aller .xml-Dateien ohne Extension in einem Verzeichnis auf."""
    dateinamen = [os.path.splitext(datei)[0] for datei in os.listdir(verzeichnis) if datei.endswith('.xml')]
    return dateinamen
    
def main():
    
    result_f = ''
    result_final=[]

    pool = ThreadPool(processes=settings["workflow"]["max_processes"])
   
    d = settings["fdc"]["xml_input_directory"]
    l= list_xml_files_sorted(settings["fdc"]["xml_input_directory"])

    logger.debug(f"Sorted xml files in directory '{d}' are '{l}'.")
    
    # SMA-291 Das Starten der FDC-Jobs soll anhand der Namen sortiert nach A-Z erfolgen.
    for filename in list_xml_files_sorted(settings["fdc"]["xml_input_directory"]):
        logger.debug(f"The import with config '{filename}' is added to pool.")
        f = os.path.join(settings["fdc"]["xml_input_directory"], filename)
        # checking if it is a file
        if os.path.isfile(f):
            result_f = pool.apply_async(runClient, args=(filename,), callback=collect_result)
            result_final.append(result_f)

    pool.close()
    # wait that all subropresses are finished
    pool.join()
    
    logger.info("############################################")
    logger.info("# Execution Report:")
    # for f_res in result_final:
    #    r = f_res.get(timeout=10)
    #    print(r)
    for r in result:
        logger.info(r)
    logger.info("############################################")
         
    # Second chance for failed executions
    result_f = ''
    result_final=[]
    pool = ThreadPool(processes=settings["workflow"]["max_processes"])
    for r in result:
        if r[1] != ERROR:
            continue
        filename = r[0]
        logger.info('\n -- Retry for the configuration: {} --'.format(filename))
        f = os.path.join(settings["fdc"]["xml_input_directory"], filename)
        # checking if it is a file
        if os.path.isfile(f):
            result_f = pool.apply_async(runClient, args=(filename,), callback=collect_result_retry)
            result_final.append(result_f)
    
    pool.close()
    # wait that all subropresses are finished
    pool.join()    
    
    #if settings["workflow"]["simulate"]:
    #    sys.exit()
        
    logger.info("############################################")
    logger.info("# Retry execution Report:")
    for r in result_retry:
        logger.info(r)
    logger.info("############################################")
    
    for r in result_retry:
        if r[1] != ERROR:
            continue
        filename = r[0]
        logger.info('\n -- Send mail because of failed import with the configuration: {} --'.format(filename))
        sendMail(filename)

    logger.info("\n-- Archiving & Cleanup")
    
    # archive Folder without logs
    cleaner.archive_leaf_directories(settings["log_output"], xml_dateinamen_auflisten(settings["fdc"]["xml_input_directory"]) ,settings["workflow"]["archive_path"])
    
    # clean & archive monitoring reports
    cleaner.archive_and_cleanup(settings["workflow"]["monitoring_path"], settings["workflow"]["archive_path"])
    # clean & archive fdc logs
    cleaner.archive_and_cleanup(settings["log_output"], settings["workflow"]["archive_path"], 30, 120, True, True)
    # clean & archive cronjob logs
    cleaner.archive_and_cleanup(settings["log_output"], settings["workflow"]["archive_path"], 3, 7, False, True)
    
    # SMA-291: Bereinigung des Staging-Verzeichnisses von FDC-PLMXMLsL:  ÃƒÂ¤ltere FDC PLMXML-Dateien die ÃƒÂ¤lter als 30-Tage sind werden im FDC-PLMXML Downloadverzeichnis gelÃƒÂ¶scht (/mounts/import/cdm/VISVIEW/AS-PLM_fdc)
    # clean old plmxml
    cleaner.deleteFiles(settings["workflow"]["plmxml"]["move_from"])
    # clean old FDC map
    cleaner.deleteFiles(settings["fdc"]["fdc_map"])
    
    logger.info("\n-- Generate monitoring Report:")
    if createDirectory(settings["workflow"]["monitoring_path"]):
        fdcRuntimeFilePath = os.path.join(settings["workflow"]["monitoring_path"], f"FDC-Runtime_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        fdcRunningJobFilePath = os.path.join(settings["workflow"]["monitoring_path"], f"FDC-RunningJobCount_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        reporter.generateReport(settings["log_output"], fdcRuntimeFilePath, fdcRunningJobFilePath, settings["fdc"]["xml_input_directory"])
    else:
        logger.error(f"Monitorng Report could not be generated because of missing target folder")

def createDirectory(pfad):
    try:
        # PrÃƒÂ¼fen, ob das Verzeichnis bereits existiert
        if not os.path.exists(pfad):
            # Erstellen des Verzeichnisses
            os.makedirs(pfad)
            logger.info(f"Directory '{pfad}' created successfully.")
        else:
            logger.info(f"Directory '{pfad}' already exists.")
    except Exception as e:
        logger.error(f"Error creating directory: {e}.")
        return False
    
    return True
        
def printConfig():
    logger.info('Konfiguration:')
    logger.info('  - XML_INPUT_DIRECTORY: {}'.format(settings["fdc"]["xml_input_directory"]))
    logger.info('  - FILE_DOWNLOAD_CLIENT_HOME: {}'.format(settings["fdc"]["file_download_client_home"]))
    logger.info('  - Log_OUTPUT: {}'.format(settings["log_output"]))
    logger.info('  - JAVA_PATH: {}'.format(settings["fdc"]["java_path"]))
    logger.info('  - USERPID: {}'.format(settings["fdc"]["userpid"]))
    logger.info('  - MAX_Processes: {}'.format(settings["workflow"]["max_processes"]))
    logger.info('\n')

def loadConfig():
    global settings
    settings = config.load_config_with_env_required("application.yml")
    
    #test
    #print(settings)
     
def initLog():
    fdcMnglogDir = os.path.join(settings["log_output"], "fdc_manager")
    if not os.path.exists(fdcMnglogDir):
        os.makedirs(fdcMnglogDir)
        
    fdcMnglogFile = os.path.normpath(os.path.join(fdcMnglogDir, 'fdc_manager.log'))
    
    if settings["workflow"]["simulate"]:
        fdcMnglogFile = os.path.normpath(os.path.join(fdcMnglogDir, 'fdc_manager_simulation.log'))
    
    logger.debug('FDC-Manager log file path:  {} \n'.format(fdcMnglogFile))
    
    # format the log entries
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(threadName)s %(message)s')
    handler = TimedRotatingFileHandler(fdcMnglogFile, 
                                   when= 'D', atTime= datetime(2024, 7, 30, 10, 8) , #'midnight',
                                   backupCount=21)
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
            
if __name__ == '__main__':
    # Load Config
    loadConfig()
    
    # Initialize log
    initLog()
    
    startTime = datetime.now()
    logger.info("\n")
    logger.info("############################################")
    logger.info("# START: {}".format(startTime))
    logger.info("############################################\n")
    
    # Print configuration
    printConfig()
    
    # process ..
    main()
    
    endTime = datetime.now()
    
    logger.info("# END: {}".format(endTime))
    logger.info("# Download took time:" + str((endTime - startTime).total_seconds()))
    logger.info("############################################\n")

