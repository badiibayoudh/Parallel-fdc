#############################################################
# Orchestration of FileDownloadClient (FDC)
#############################################################
# History
# -----------------------------------------------------------
# 29.07.2024    Badii Bayoudh   Initial Creation
# 19.08.2024    Juergen Marat   German -> English, Logfile renamed, New Jar fdc_v7_07_08_2024.jar
# 06.09.2024    Adjust copy of plxml file + set the env variable for  FDC user log file path
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

ERROR='error'
result = []
logger = logging.getLogger('app')

def sendMail(cfg, logFile):
    logger.debug("Mail sent .. (not implemented yet)")
    # TO BE DONE AS SOON AS POSSIBLE

# Collect the returned result when running the client
def collect_result(val):
    return result.append(val)

def runClientInt(configFileName):
    # Get config name from the config file name
    configName = os.path.splitext(configFileName)[0]
    logger.debug('Name of input config:  {}'.format(configName))
    
    product = configName.split('_')[1]
    logger.debug('Name of carline or powertrain:  {}'.format(product))
    
    logFilePath = os.path.join(config.Log_OUTPUT, product, configName)
    logger.debug('Path log file:  {}'.format(logFilePath))
    
    fdcLogFilePath = os.path.join(logFilePath, 'FDCUserLog.txt')
    logger.debug('Path FDC User log file:  {}'.format(fdcLogFilePath))
    
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
    fdcClientPath = os.path.join(config.FILE_DOWNLOAD_CLIENT_HOME, 'fdc_v7_07_08_2024.jar')
    
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
    action = "Success"
    if os.path.exists(logFile):
        with open(logFile, 'r') as fp:
            for l_no, line in enumerate(fp):
                if 'FailedException' in line or 'Caused by:' in line:
                    logger.error('Failed exception in input config {} within FDC: {} \n'.format(configFileName, line))
                    logger.debug('Line Number: {}'.format( l_no))
                    logger.debug('Line: {}'.format( line))
                    sendMail(configFileName, logFile)
                    action = "error"
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
    logger.info(f"# Report:")
    # for f_res in result_final:
    #    r = f_res.get(timeout=10)
    #    print(r)
    for r in result:
        logger.info(r)

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
