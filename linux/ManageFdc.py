#############################################################
# Orchestration of FileDownloadClient (FDC)
#############################################################
# History
# -----------------------------------------------------------
# 29.07.2024    Badii Bayoudh   Initial Creation
# 19.08.2024    Juergen Marat   German -> English, Logfile renamed, New Jar fdc_v7_07_08_2024.jar
# 06.09.2024    Adjust copy of plxml file + set the env variable for  FDC user log file path
# 17.09.2024    Badii Add Monitoring and retry when error
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

ERROR='error'
SUCCESS= 'Success'
result = []
result_retry = []
logger = logging.getLogger('fdc_Manager')

def sendMail(cfg, logFile):
    logger.debug("Mail sent .. (not implemented yet)")
    # TO BE DONE AS SOON AS POSSIBLE

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
    
    myenv['ENVIRONMENT_TO_CONNECT'] = config.ENVIRONMENT_TO_CONNECT
    myenv['USERPID'] = config.USERPID
    
    myenv['FILE_DOWNLOAD_CLIENT_HOME'] = config.FILE_DOWNLOAD_CLIENT_HOME
    myenv['STATUS_CHECK_INTERVAL'] = str(config.STATUS_CHECK_INTERVAL)

    if not os.path.exists(logFilePath):
        os.makedirs(logFilePath)

    credentialsPath = config.CREDENTIALS
    configFilePath =  os.path.join(config.XML_INPUT_DIRECTORY, configFileName)
    downloadArgs1 ='--encryptedCredLocation=' + credentialsPath
    downloadArgs2 ='--inputFileLocation=' + configFilePath
    logger.info('downloadArgs:  {} , {} \n'.format(downloadArgs1, downloadArgs2))
    
    javaCmd = os.path.join(config.JAVA_PATH, 'java')
    fdcClientPath = os.path.join(config.FILE_DOWNLOAD_CLIENT_HOME, 'fdc.jar')
    
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
    
    ## check result
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
                    sendMail(configFileName, logFile)
                    action = ERROR
                    # don't look for next lines
                    return (configFileName, action)
    

    # Move plmxml in order to be imported
    # Annahme: plmml has same name as the configuration file
    if config.MOVE_PLMXML:
        plmxmlfileName=configName+'.plmxml'
        plmxmlfileFrom= os.path.join(config.Move_PLMXML_FROM, plmxmlfileName)
        if os.path.exists(plmxmlfileFrom):
            #productTo= os.path.join(config.Move_PLMXML_TO, 'fdc_'+product)
            #if not os.path.exists(productTo):
            #    os.makedirs(productTo)
            try:
                plmxmlfileTo= os.path.join(config.Move_PLMXML_TO, plmxmlfileName)
                plmxmlfileToTemp= os.path.join(config.Move_PLMXML_TO, plmxmlfileName + "_tmp")
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
    
    logFilePath = os.path.join(config.Log_OUTPUT, product, configName)
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

def main():
    
    result_f = ''
    result_final=[]

    pool = ThreadPool(processes=config.MAX_Processes)
    
    for filename in os.listdir(config.XML_INPUT_DIRECTORY):
        f = os.path.join(config.XML_INPUT_DIRECTORY, filename)
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
    pool = ThreadPool(processes=config.MAX_Processes)
    for r in result:
        if r[1] != ERROR:
            continue
        filename = r[0]
        logger.info('\n -- Retry for the configuration: {} --'.format(filename))
        f = os.path.join(config.XML_INPUT_DIRECTORY, filename)
        # checking if it is a file
        if os.path.isfile(f):
            result_f = pool.apply_async(runClient, args=(filename,), callback=collect_result_retry)
            result_final.append(result_f)
    
    pool.close()
    # wait that all subropresses are finished
    pool.join()    
    
    logger.info("############################################")
    logger.info("# Retry execution Report:")
    for r in result_retry:
        logger.info(r)
    logger.info("############################################")
    

    logger.info("\n-- Generate monitoring Report:")
    if createDirectory(config.MONITORING_PATH):
        fdcRuntimeFilePath = os.path.join(config.MONITORING_PATH, f"FDC-Runtime_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        fdcRunningJobFilePath = os.path.join(config.MONITORING_PATH, f"FDC-RunningJobCount_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        reporter.generateReport(config.Log_OUTPUT, fdcRuntimeFilePath, fdcRunningJobFilePath)
    else:
        logger.error(f"Monitorng Report could not be generated because of missing target folder")
    
    logger.info("\n-- Archiving & Cleanup")
    cleaner.archive_and_cleanup(config.MONITORING_PATH, config.ARCHIVE_PATH)

def createDirectory(pfad):
    try:
        # Prüfen, ob das Verzeichnis bereits existiert
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
    logger.info('  - XML_INPUT_DIRECTORY: {}'.format(config.XML_INPUT_DIRECTORY))
    logger.info('  - FILE_DOWNLOAD_CLIENT_HOME: {}'.format(config.FILE_DOWNLOAD_CLIENT_HOME))
    logger.info('  - Log_OUTPUT: {}'.format(config.Log_OUTPUT))
    logger.info('  - JAVA_PATH: {}'.format(config.JAVA_PATH))
    logger.info('  - USERPID: {}'.format(config.USERPID))
    logger.info('  - MAX_Processes: {}'.format(config.MAX_Processes))
    logger.info('\n')
 
def initLog():
    fdcMnglogDir = os.path.join(config.Log_OUTPUT, "fdc_manager")
    if not os.path.exists(fdcMnglogDir):
        os.makedirs(fdcMnglogDir)
    fdcMnglogFile = os.path.normpath(os.path.join(fdcMnglogDir, 'fdc_manager.log'))
    
    
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
    # 1 Initialize log
    initLog()
    
    startTime = datetime.now()
    logger.info("\n")
    logger.info("############################################")
    logger.info("# START: {}".format(startTime))
    logger.info("############################################\n")
    
    # 2 Print configuration
    printConfig()
    
    # 3 process ..
    main()
    
    endTime = datetime.now()
    
    logger.info("# END: {}".format(endTime))
    logger.info("# Download took time:" + str((endTime - startTime).total_seconds()))
    logger.info("############################################\n")
