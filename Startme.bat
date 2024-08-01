@echo off 
REM *** Start multiple time the download client ***

REM generate credentials-Datei


REM Please change the paths below ..
set "XML_INPUT_DIRECTORY=C:\git\Parallel-fdc\windows\configInt\"
set "FILE_DOWNLOAD_CLIENT_HOME=C:\git\Parallel-fdc\"
set "Log_OUTPUT=C:\git\Parallel-fdc\logs\"
REM set "maxProc=28"
set "maxProc=7"
set "waitTimeBeforeClose=30"
REM Thanks ..

set "Launcher_HOME=%~dp0"
echo %Launcher_HOME%
echo "XML input directory: %XML_INPUT_DIRECTORY%"
echo "Log output directory: %Log_OUTPUT%"
for %%a in (%XML_INPUT_DIRECTORY%*) do call :loop %%a

pause
goto :eof


:loop

call :checkinstances

if %INSTANCES% LSS %maxProc% goto :work

rem wait a second, can be adjusted with -w (-n 2 because the first ping returns immediately;
rem otherwise just use an address that's unused and -n 1)
echo Waiting for instances to close ...
ping -n 2 ::1 >nul 2>&1
rem jump back to see whether we can spawn a new process now
rem goto loop
goto :loop

:work	
	set "configFilePath=%1"
	set "configName=%~dpn1"

	echo.
	echo "-----------------------"
	echo "| Run download client |
	echo "-----------------------"
	
	echo "configFilePath: %configFilePath%"
	echo "configName: %configName%"

	
	echo "config file path: %configFilePath%
	for %%b in ("%configFilePath%") do set "configFileName=%%~nxa"
	echo "Config file name: %configFileName%"
	
	for %%b in ("%configName%") do set "configName=%%~na"
	echo "Config name: %configName%"

	Set "Up2Sub=%configFileName:*_=%"
	Set "baureihe=%Up2Sub:_="&:"%"
	echo "Baureihe: %baureihe%"

	set "LOG_FILE_PATH=%Log_OUTPUT%%Baureihe%\%configName%"
	echo "log file path: %LOG_FILE_PATH%"

	set LOGGING_FILE_NAME=%configName%
	echo "logging file name: %configName%"

	set "FDC_RUN_STATUS_PATH=%LOG_FILE_PATH%"

	if not exist "%LOG_FILE_PATH%" mkdir %LOG_FILE_PATH%

	start "download_client_instance" call "%Launcher_HOME%generic.bat"
	
    goto :eof

:waitqueue
rem wait a second, can be adjusted with -w (-n 2 because the first ping returns immediately;
rem otherwise just use an address that's unused and -n 1)
rem echo Waiting for instances to close ...
ping -n 2 ::1 >nul 2>&1
rem jump back to see whether we can spawn a new process now
rem goto loop
goto :loop
	
:checkinstances
rem this could probably be done better. But INSTANCES should contain the number of running instances afterwards.
for /f "usebackq" %%t in (`tasklist /fo csv /fi "imagename eq cmd.exe"^|find /v /c ""`) do set INSTANCES=%%t
echo "current Number of running cmd.exe: %INSTANCES%"
goto :eof