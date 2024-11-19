printf "Setting environment variables..."
if [[ -r "/applications/local/set_appl_env" ]]; then
    source "/applications/local/set_appl_env" cdm_importer
else
    printf "Could not source set_appl_env"

    export FDC_HOME=/applications/asplm/asplmt3/cust_root_dir/cdm_importer/fdc
    export FDC_LOG_DIR=/applications/logs/fdc
    export FDC_CREDENTIALS_FILE=/applications/asplm/asplmt3/security/fdc/encrypted_cred.txt
    export FDC_CONF_DIR=/applications/local/config/fdc
    export JAVA_HOME=/applications/asplm/asplmt3/java/jdk17
    export PATH=${JAVA_HOME}/bin:$PATH

fi

python3 ${FDC_HOME}/ManageFdc.py