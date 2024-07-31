import os
import sys
import glob

from subprocess import Popen, PIPE
import subprocess
#from multiprocessing import Pool
from multiprocessing.pool import ThreadPool

from datetime import datetime
import time

import logging
from logging.handlers import TimedRotatingFileHandler

###### Please configure the client by entering the settings below.. ##########

XML_INPUT_DIRECTORY = '/applications/asplm/asplmt3/cust_root_dir/cdm_importer/fdc/configs/'
FILE_DOWNLOAD_CLIENT_HOME = '/applications/asplm/asplmt3/cust_root_dir/cdm_importer/fdc/'
Log_OUTPUT = '/applications/asplm/asplmt3/cust_root_dir/cdm_importer/fdc/logs/'
JAVA_PATH='/applications/asplm/asplmt3/cust_root_dir/cdm_importer/fdc/java/jdk-17.0.11/bin/'
CREDENTIALS='/applications/asplm/asplmt3/cust_root_dir/cdm_importer/fdc/EncryptedCred_PROD.txt'

#XML_INPUT_DIRECTORY = 'D:/git/Parallel-fdc/configs/'
#FILE_DOWNLOAD_CLIENT_HOME = 'D:/git/Parallel-fdc/'
#Log_OUTPUT = 'D:/git/Parallel-fdc/logs/'
#JAVA_PATH='D:/Apps/Java/jdk-17/jdk-17.0.7/bin/'


#XML_INPUT_DIRECTORY = 'C:/ASPLM/FileDownloadClient/test/FDC-Konfigs/tmp_Badii_FDC_xml/'
#FILE_DOWNLOAD_CLIENT_HOME = 'C:/ASPLM/FileDownloadClient/test/FDC-Konfigs/'
#Log_OUTPUT = 'C:/ASPLM/FileDownloadClient/test/FDC-Konfigs/logs/'
#JAVA_PATH='C:/apps/java/java17/bin/'

ENVIRONMENT_TO_CONNECT='PROD'
USERPID='pid5457'
STATUS_CHECK_INTERVAL=5

MAX_Processes=5
waitTimeBeforeClose=30

# Thanks.
################################################################################

ERROR='error'
result = []
logger = logging.getLogger('app')

def sendMail(cfg, logFile):
    logger.info("Mail sent ..")

# Collect the returned result when running the client
def collect_result(val):
    return result.append(val)

def runClientInt(configFileName):
    # get config name from the config file name
    configName = os.path.splitext(configFileName)[0]
    logger.debug('Name der Konfig:  {}'.format(configName))
    
    product = configName.split('_')[1]
    logger.debug('Name der Baureihe:  {}'.format(product))
    
    logFilePath = os.path.join(Log_OUTPUT, product, configName)
    logger.debug('Path der Logdatei:  {}'.format(logFilePath))
    
    myenv = os.environ.copy()
    myenv['LOG_FILE_PATH'] = logFilePath
    myenv['LOGGING_FILE_NAME'] = configName
    myenv['FDC_RUN_STATUS_PATH'] = logFilePath
    
    myenv['ENVIRONMENT_TO_CONNECT'] = ENVIRONMENT_TO_CONNECT
    myenv['USERPID'] = USERPID
    
    myenv['FILE_DOWNLOAD_CLIENT_HOME'] = FILE_DOWNLOAD_CLIENT_HOME

    if not os.path.exists(logFilePath):
        os.makedirs(logFilePath)

    credentialsPath = CREDENTIALS
    configFilePath =  os.path.join(XML_INPUT_DIRECTORY, configFileName)
    #downloadArgs ='--encryptedCredLocation="' + credentialsPath + '"' + ' --inputFileLocation="' + configFilePath +'"'
    downloadArgs1 ="--encryptedCredLocation=" + credentialsPath 
    downloadArgs2 ="--inputFileLocation=" + configFilePath
    #logger.info('downloadArgs:  {} \n'.format(downloadArgs))
    
    javaCmd = os.path.join(JAVA_PATH, 'java')
    fdcClientPath = os.path.join(FILE_DOWNLOAD_CLIENT_HOME, 'fdc_v6_26_06_2024.jar')
    
    # C:"\apps\java\java17\bin\java" -Dfile.encoding=UTF-8 -jar "%FILE_DOWNLOAD_CLIENT_HOME%fdc_v6_26_06_2024.jar" %MODE% %DOWNLOAD_ARGS%
    command = [javaCmd, '-Dfile.encoding=UTF-8', '-jar', fdcClientPath, 'download_mode', downloadArgs1, downloadArgs2]
    logger.info("Befehl wird durchgefuhrt: {}".format(command))
    
    try:
        complPr = subprocess.run(command, env=myenv, check=True)
        print(complPr.returncode)
        
        #subprocess.run(command, env=myenv, check=True, capture_output=True)
        #subprocess.Popen(command, env=myenv, check=True, capture_output=True)
        #print('...')
        
        #process = Popen(command, env=myenv)
        #retCode = process.wait()
        #print(retCode)
        #stdout, stderr = process.communicate()

    except:
        logger.exception("Befehl hat nicht funktioniert: {}".format(command))
        return (configFileName, ERROR)
    
    ## check result

    logFile = getLatestLog(logFilePath) #os.path.join(logFilePath, configName+".log")
    logger.debug('Das letzte Logdatei :  {} \n'.format(logFile))
    action = "Success"
    if os.path.exists(logFile):
        with open(logFile, 'r') as fp:
            for l_no, line in enumerate(fp):
                if 'FailedException' in line or 'Caused by:' in line:
                    logger.error('Fin Fehler in mit der Konfigdatei {} laufende FDC: {} \n'.format(configFileName, line))
                    logger.debug('Zeilenumer: {}'.format( l_no))
                    logger.debug('Zeile: {}'.format( line))
                    sendMail(configFileName, logFile)
                    action = "error"
                    # don't look for next lines
                    break
    
    return (configFileName, action)


def runClient(configFileName):
    try:
        logger.info('>> Start einer Instanz von FDC-Client mit der Konfigdatei: {}\n'.format(configFileName))
        return runClientInt(configFileName)
    except:
        logger.exception('Fehler in FDC-Client mit der Konfigdatei: {}'.format(configFileName))
        return (configFileName, ERROR)
    finally:
        logger.info('<< Ende einer Instanz von FDC-Client mit der Konfigdatei: {} \n'.format(configFileName))


def getLatestLog(logFolder):
    logPattern = os.path.join(logFolder, '*')
    list_of_files = glob.glob(logPattern) # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def main():
    
    result_f = ''
    result_final=[]

    pool = ThreadPool(processes=MAX_Processes)
    
    for filename in os.listdir(XML_INPUT_DIRECTORY):
        f = os.path.join(XML_INPUT_DIRECTORY, filename)
        # checking if it is a file
        if os.path.isfile(f):
            result_f = pool.apply_async(runClient, args=(filename,), callback=collect_result)
            result_final.append(result_f)

    pool.close()
    # wait that all subropresses are finished
    pool.join()
    
    logger.info("############################################")
    logger.info("# Report:")
    # for f_res in result_final:
    #    r = f_res.get(timeout=10)
    #    print(r)
    for r in result:
        logger.info(r)

def printConfig():
    logger.info('Konfiguration:')
    logger.info('  - XML_INPUT_DIRECTORY: {}'.format(XML_INPUT_DIRECTORY))
    logger.info('  - FILE_DOWNLOAD_CLIENT_HOME: {}'.format(FILE_DOWNLOAD_CLIENT_HOME))
    logger.info('  - Log_OUTPUT: {}'.format(Log_OUTPUT))
    #logger.info('  - JAVA_PATH: {}'.format(JAVA_PATH))
    logger.info('  - USERPID: {}'.format(USERPID))
    logger.info('  - MAX_Processes: {}'.format(MAX_Processes))
    logger.info('\n')
 
def initLog():
    fdcMnglogDir = os.path.join(Log_OUTPUT, "fdc_manager")
    if not os.path.exists(fdcMnglogDir):
        os.makedirs(fdcMnglogDir)
    fdcMnglogFile = os.path.normpath(os.path.join(fdcMnglogDir, 'fdc_manager_log'))
    logger.debug('fdcManager log file path:  {} \n'.format(fdcMnglogFile))
    
    # format the log entries
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(threadName)s %(message)s')
    handler = TimedRotatingFileHandler(fdcMnglogFile, when= 'D', atTime= datetime(2024, 7, 30, 10, 8), backupCount=21)
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
            
if __name__ == '__main__':
    # 1 Initialize log
    initLog()
    
    startTime = datetime.now()
    logger.info("\n")
    logger.info("############################################")
    logger.info("# Startzeit: {}".format(startTime))
    logger.info("############################################\n")
    
    # 2 Print configuration
    printConfig()
    
    # 3 process ..
    main()
    
    endTime = datetime.now()
    
    logger.info("# Endzeit: {}".format(endTime))
    logger.info("# Das Herunterladen dauerte:" + str((endTime - startTime).total_seconds()))
    logger.info("############################################\n")
