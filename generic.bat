@ECHO OFF

rem Modes supported in FDC :  encrypt_mode   and  download_mode

rem  "FILE_DOWNLOAD_CLIENT_HOME=E:\FileDownloadclient\Downloadclient\"
rem set "FILE_DOWNLOAD_CLIENT_HOME=%1"
rem  "XML_INPUT_DIRECTORY=E:\FileDownloadclient\Konfigurationsdateien\"
rem set "XML_INPUT_DIRECTORY=%2"

rem replace <CHANGEME_USERPID> with pid
rem replace <CHANGEME_ENVIRONMENT_TO_CONNECT> with TI, TI2 or PROD
rem replace <CHANGEME_INPUT_FILE_NAME> with INPUT_XML

rem Technical User PID which is used to launch FDC 
rem set USERPID=pid5457  
set USERPID=pid1489

rem possible values for ENVIRONMENT_TO_CONNECT  : TI, TI2
rem set ENVIRONMENT_TO_CONNECT=PROD
set ENVIRONMENT_TO_CONNECT=TI

rem PATH D:\FileDownloadclient\FileDownloadClient_Armin\jdk-11.0.2\bin;!PATH!
rem set PATH=%PATH%;C:\Windows\System32\WindowsPowerShell\v1.0

rem set JAVA_HOME=D:\FileDownloadclient\FileDownloadClient_Armin\jdk-11.0.2


rem  LOG_FILE_PATH=E:\FileDownloadclient\Output\logs\C117\AS_C117_FC_L
rem set LOG_FILE_PATH=%3

rem enable to change application logfile name.
rem  LOGGING_FILE_NAME=AS_C117_FC_L
rem set LOGGING_FILE_NAME=%4

rem enable to change path to the folder where excution status files should be generated
rem default location:Location of jar file
rem  FDC_RUN_STATUS_PATH=E:\FileDownloadclient\Output\logs\C117\AS_C117_FC_L
rem set FDC_RUN_STATUS_PATH=%5
 
set STATUS_CHECK_INTERVAL=5
set MODE=%1   

IF [%1] == [] GOTO SetDefaultParam
IF %MODE% == encrypt_mode GOTO GetCredentials

IF NOT [%1] == [] GOTO Execute

:SetDefaultParam
ECHO No param recieved. Setting mode to download_mode
set MODE=download_mode
GOTO Execute

:GetCredentials
for /F "usebackq" %%p in (`powershell -Command "$clientId = read-host 'Enter Client Id' -AsSecureString ;$BSTR=[System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($clientId);[System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)"`) do set clientId=%%p
for /F "usebackq" %%p in (`powershell -Command "$clientSecret = read-host 'Enter Client Secret' -AsSecureString ;$BSTR=[System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($clientSecret);[System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)"`) do set clientSecret=%%p
for /F "usebackq" %%p in (`powershell -Command "$xApiKey = read-host 'Enter X-API-Key' -AsSecureString ;$BSTR=[System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($xApiKey);[System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)"`) do set xApiKey=%%p
GOTO Execute


:Execute
echo "Mode: %MODE%"
rem set DOWNLOAD_ARGS=--encryptedCredLocation="%USERPROFILE%\Credentials\EncryptedCred_PRD.txt" --inputFileLocation="%XML_INPUT_DIRECTORY%%configFileName%"
set DOWNLOAD_ARGS=--encryptedCredLocation="%USERPROFILE%\Credentials\EncryptedCred_INT.txt" --inputFileLocation="%XML_INPUT_DIRECTORY%%configFileName%"

echo "Download args: %DOWNLOAD_ARGS%"

C:"\apps\java\java17\bin\java" -Dfile.encoding=UTF-8 -jar "%FILE_DOWNLOAD_CLIENT_HOME%fdc_v6_26_06_2024.jar" %MODE% %DOWNLOAD_ARGS%

rem C:"\Armin\03_Freeware\graalvm-ce-java17-22.3.0\bin\java" -Dfile.encoding=UTF-8 -jar "%FILE_DOWNLOAD_CLIENT_HOME%svc40-batch-app.jar" %MODE% %DOWNLOAD_ARGS%
rem C:"\Program Files\EC\jre\bin\java" -Dfile.encoding=UTF-8 -jar "%FILE_DOWNLOAD_CLIENT_HOME%fdc_v6_26_06_2024.jar" %MODE% %DOWNLOAD_ARGS%

rem pause
echo Completed. The window will be closed in 30 Seconds
echo.
timeout /t %waitTimeBeforeClose%

REM exit

