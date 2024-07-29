import os
import subprocess
import sys

from datetime import datetime
from multiprocessing import Pool
import time

import re

import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)

###### Please configure the client by entering the settings below ##########
XML_INPUT_DIRECTORY = 'C:/ASPLM/FileDownloadClient/test/FDC-Konfigs/tmp_Badii_FDC_xml/'
FILE_DOWNLOAD_CLIENT_HOME = 'C:/ASPLM/FileDownloadClient/test/FDC-Konfigs/'
Log_OUTPUT = 'C:/ASPLM/FileDownloadClient/test/FDC-Konfigs/logs/'
JAVA_PATH='C:/apps/java/java17/bin/'
ENVIRONMENT_TO_CONNECT='PROD'
USERPID='pid5457'
STATUS_CHECK_INTERVAL=5

MAX_Processes=5
waitTimeBeforeClose=30

# Thanks
################################################


lst = [(2, 2),  (4, 4), (5, 5),(6,6),(3, 3),]
result = []

def sendMail(cfg):
    print("Mail sent ..")

def collect_result(configFileName):
    configName = os.path.splitext(configFileName)[0]
    product = configName.split('_')[2]
    logFile = os.path.join(Log_OUTPUT, product, configName, configName, ".log")
    action = "Success"
    if os.path.exists(logFile):
        textfile = open(logFile, 'r')
        matches = []
        reg = re.compile("(<(\d{4,5})>)?")
        for line in textfile:
            errFound = reg.findall(line)
            if errFound:
                print('Error with FDC running with config {}: {} \n'.format(configFileName, errFound))
                sendMail(configFileName)
                action = "error"
                break;
        textfile.close()
        
    return result.append(configFileName, action)

def mulX(x, y):
    print(f"start process {x} - {y}")
    time.sleep(3)
    print(f"end process {x} - {y}")
    res = x * y
    res_ap = (x, y, res)
    return res_ap

def runClient(configFileName):
    # get config name from the config file name
    configName = os.path.splitext(configFileName)[0]
    print('Name der Konfig:  {} \n'.format(configName))
    
    product = configName.split('_')[2]
    print('Name der Baureihe:  {} \n'.format(product))
    
    
    logFilePath = os.path.join(Log_OUTPUT, product, configName)
    print('log file path:  {} \n'.format(logFilePath))
    
    myenv = os.environ.copy()
    myenv['LOG_FILE_PATH'] = logFilePath
    myenv['LOGGING_FILE_NAME'] = configName
    myenv['FDC_RUN_STATUS_PATH'] = logFilePath
    
    myenv['ENVIRONMENT_TO_CONNECT'] = ENVIRONMENT_TO_CONNECT
    myenv['USERPID'] = USERPID
    
    myenv['FILE_DOWNLOAD_CLIENT_HOME'] = FILE_DOWNLOAD_CLIENT_HOME

    if not os.path.exists(logFilePath):
        os.makedirs(logFilePath)

    credentialsPath = os.path.join(FILE_DOWNLOAD_CLIENT_HOME, 'EncryptedCred_PROD.txt')
    configFilePath =  os.path.join(XML_INPUT_DIRECTORY, configFileName)
    downloadArgs ='--encryptedCredLocation="' + credentialsPath + '"' + '--inputFileLocation="' + configFilePath +'"'
    print('downloadArgs:  {} \n'.format(downloadArgs))
    
    javaCmd = os.path.join(JAVA_PATH, 'java')
    fdcClientPath = os.path.join(FILE_DOWNLOAD_CLIENT_HOME, 'fdc_v6_26_06_2024.jar')
    
    # C:"\apps\java\java17\bin\java" -Dfile.encoding=UTF-8 -jar "%FILE_DOWNLOAD_CLIENT_HOME%fdc_v6_26_06_2024.jar" %MODE% %DOWNLOAD_ARGS%
    command = [javaCmd, '-Dfile.encoding=UTF-8', '-jar', fdcClientPath, 'download_mode', downloadArgs]
    
    subprocess.run(command, env=myenv, check=True, capture_output=True)

# Apply Async
def main():
    fdcMnglogPath = os.path.join(Log_OUTPUT, "fdc_manager", datetime.now().strftime('fdcMng_%H_%M_%d_%m_%Y.log'))

    logging.basicConfig(filename=fdcMnglogPath, encoding="utf-8", filemode="a", level=logging.debug, format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M")
            
    handler = RotatingFileHandler(path, maxBytes=20, backupCount=5)
    logger.addHandler(handler)
    
    result_f = ''
    result_final=[]

    pool = Pool(processes=MAX_Processes)
    
    for filename in os.listdir(XML_INPUT_DIRECTORY):
        f = os.path.join(XML_INPUT_DIRECTORY, filename)
    # checking if it is a file
    if os.path.isfile(f):
        print('>> Startet FDC-Client mit der Konfigdatei:  {} \n'.format(f))
        result_f = pool.apply_async(runClient, args=(filename), callback=collect_result)
        result_final.append(result_f)
    
    #for x,y in lst:
    #    result_f = pool.apply_async(mulX, args=(x,y), callback=collect_result)
    #    result_final.append(result_f)

    pool.close()
    
    # wait that all subropresses are finished
    pool.join()
    
    print(f"Ergebniszusammenfassung:")
    # for f_res in result_final:
    #    r = f_res.get(timeout=10)
    #    print(r)

    for r in result:
        print(r)

        
if __name__ == '__main__':
    start = datetime.now()
    main()
    print("End Time Apply Async:", (datetime.now() - start).total_seconds())