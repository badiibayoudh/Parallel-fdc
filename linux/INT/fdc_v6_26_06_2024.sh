#!/bin/bash

# *********************************************************************************************************************************************

# modes supported in FDC :  encrypt_mode   and  download_mode 
# run FDC in encrpytmode ( in cmd prompt : >fdc.bat encrypt_mode ) to encrpt the credentials
# run FDC in download_mode ( in cmd prompt : >fdc.bat download_mode ) / double click fdc.bat to start file download 

# ------------------------------------------------------------------------------------------------------------------ 
 
# replace <CHANGEME_USERPID> with Technical User PID which is used to launch FDC 
# replace <CHANGEME_LOGFILE_NAME> with unique log file name 
# replace <CHANGEME_ENVIRONMENT_TO_CONNECT> with TI , TI2 , PROD
# replace <CHANGEME_LOG_FILE_PATH_INCLUDING_FILE_NAME> with log file path including file Name
# replace <CHANGEME_USER_LOCALE> with en_US or de_DE
# replace <CHANGEME_STATUS_INTERVAL_IN_MINUTES> with time interval in minutes for job status check from  maintenance table
# replace <CHANGEME_FDC_RUN_STATUS_PATH> with path to the folder where execution status files should be generated.  
# replace <CHANGEME_INPUT_FILE_NAME> with input xml file name eg: FileDownloadClientInput.xml 

# *********************************************************************************************************************************************


get_value()
{
local 'args' 'char' 'charcount' 'prompt'   
  args+=( "${1}" )
	reply=''
	while IFS='' read -n '1' -p "$prompt" -r -s 'char'; do
		case "${char}" in
          # Handles NULL
          ( $'\000' )
            break
            ;;
          # Handles BACKSPACE and DELETE
          ( $'\010' | $'\177' )
            if (( charcount > 0 )); then
              prompt=$'\b \b'
              reply="${reply%?}"
              (( charcount-- ))
            else
              prompt=''
            fi
            ;;
          ( * )
            prompt='*'
            reply+="${char}"
            (( charcount++ ))
            ;;
        esac
	done
	export "${args[@]}"="${reply}"
	printf '\n' >&2
}


get_inputs_clientCred()
{
    echo  'Enter Client Id :'
		get_value clientId 
		echo  'Enter Client Secret :' 
		get_value clientSecret
		echo  'Enter Client x-api-key :' 
		get_value xApiKey
}

get_inputs_authcode()
{
  	echo  'Enter Auth code Client Id :' 
		get_value authCodeClientId
		echo  'Enter  x-api-key :' 
		get_value xApiKey
}
##################################################################

echo "Starting File Download Client"
export FILE_DOWNLOAD_CLIENT_HOME=`pwd`

#change the JAVA_HOME accordingly
export JAVA_PATH="$JAVA_HOME"

#Technical User PID which is used to launch FDC 
export USERPID="<CHANGEME_USERPID>" 

#enable to change application logfile folder path
export LOG_FILE_PATH="$FILE_DOWNLOAD_CLIENT_HOME/log"

# enable to change application logfile name.
export LOGGING_FILE_NAME="<CHANGEME_LOGFILE_NAME>"

#possible values for ENVIRONMENT_TO_CONNECT  :  TI, TI2, PROD
export ENVIRONMENT_TO_CONNECT="<CHANGEME_ENVIRONMENT_TO_CONNECT>"

#default value for USER_LOG_PATH is $HOME/FDCUserLog.txt
export USER_LOG_PATH="<CHANGEME_LOG_FILE_PATH_INCLUDING_FILE_NAME>"

#possible values for USER_LOG_LOCALE  : en_US, de_DE (Log file language)
#default value: de_DE
export USER_LOCALE="<CHANGEME_USER_LOCALE>"

#default: j0SDiaBR - 30 min , Others- 5 sec , helps reduce DB hits in consumer.
#Its recommended to keep higher time interval for bigger structures
export STATUS_CHECK_INTERVAL="<CHANGEME_STATUS_INTERVAL_IN_MINUTES>"
 
# enable to change path to the folder where excution status files should be generated
# default location:Location of jar file
export FDC_RUN_STATUS_PATH="<CHANGEME_FDC_RUN_STATUS_PATH>"

# TESTENV: Use to switch between AUTHORIZATION_CODE and CLIENT_CREDENTIALS
# default CLIENT_CREDENTIALS
# export GRANT_TYPE="CLIENT_CREDENTIALS"

export MODE="$1"

if [ -z "$MODE" ]
then
	echo No param recieved. Setting mode to download_mode
	export MODE="download_mode"
fi
 
if [ "$MODE" = "encrypt_mode" ];then
	if [ -z "${GRANT_TYPE}" ]; then
    get_inputs_clientCred
	else
		case "$GRANT_TYPE" in 
		"CLIENT_CREDENTIALS") 
		get_inputs_clientCred
		;;
      
		"AUTHORIZATION_CODE") 
	  get_inputs_authcode
		;;       
		esac 
	fi
fi


export DOWNLOAD_ARGS="--encryptedCredLocation=$HOME/Credentials/EncryptedCred.txt --inputFileLocation=$FILE_DOWNLOAD_CLIENT_HOME/<CHANGEME_INPUT_FILE_NAME>"

"$JAVA_PATH/java" -Dfile.encoding=UTF-8 -jar "$FILE_DOWNLOAD_CLIENT_HOME/fdc_v6_26_06_2024.jar" $MODE $DOWNLOAD_ARGS

wait
echo "Completed"
