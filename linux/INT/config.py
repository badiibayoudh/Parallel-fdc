
###### Please configure the client by entering the settings below.. ##########
"""
STATUS_CHECK_INTERVAL=5
MAX_Processes=5
MOVE_PLMXML=False

XML_INPUT_DIRECTORY = 'D:/git/Parallel-fdc/windows/configsPrd/'
FILE_DOWNLOAD_CLIENT_HOME = 'D:/git/Parallel-fdc/'
Log_OUTPUT = 'D:/git/Parallel-fdc/logs/'
JAVA_PATH='D:/Apps/Java/jdk-17/jdk-17.0.7/bin/'
CREDENTIALS_PATH='D:/git/Parallel-fdc/EncryptedCred_PROD.txt'
Move_PLMXML_FROM='D:/git/Parallel-fdc/test/plmxml_fdc'
Move_PLMXML_TO='D:/git/Parallel-fdc/test/plmxml'
ENVIRONMENT_TO_CONNECT='PROD'
USERPID='pid5457'
"""

"""
# T3 gegen CRM
XML_INPUT_DIRECTORY = '/applications/asplm/asplmt3/cust_root_dir/cdm_importer/fdc/configsInt/'
FILE_DOWNLOAD_CLIENT_HOME = '/applications/asplm/asplmt3/cust_root_dir/cdm_importer/fdc/'
Log_OUTPUT = '/applications/asplm/asplmt3/cust_root_dir/cdm_importer/fdc/logs/'
JAVA_PATH='/applications/asplm/asplmt3/cust_root_dir/cdm_importer/fdc/java/jdk-17.0.11/bin/'
CREDENTIALS = '/applications/asplm/asplmt3/cust_root_dir/cdm_importer/fdc/EncryptedCred_INT.txt'
Move_PLMXML_FROM='D:/git/Parallel-fdc/test/plmxml_fdc'
Move_PLMXML_TO='/mounts/import/cdm/VISVIEW/AS-PLM_fdc'
ENVIRONMENT_TO_CONNECT='TI'
USERPID='pid1489'
STATUS_CHECK_INTERVAL=5

MAX_Processes=5
waitTimeBeforeClose=30    
    
"""


"""
# T3 gegen PRD
XML_INPUT_DIRECTORY = '/applications/asplm/asplmt3/cust_root_dir/cdm_importer/fdc/configs/'
FILE_DOWNLOAD_CLIENT_HOME = '/applications/asplm/asplmt3/cust_root_dir/cdm_importer/fdc/'
Log_OUTPUT = '/applications/asplm/asplmt3/cust_root_dir/cdm_importer/fdc/logs/'
JAVA_PATH='/applications/asplm/asplmt3/cust_root_dir/cdm_importer/fdc/java/jdk-17.0.11/bin/'
CREDENTIALS='/applications/asplm/asplmt3/cust_root_dir/cdm_importer/fdc/EncryptedCred_PROD.txt'
ENVIRONMENT_TO_CONNECT='PROD'
USERPID='pid5457'
STATUS_CHECK_INTERVAL=5

MAX_Processes=5
waitTimeBeforeClose=30    
"""

# INT gegen PRD
FILE_DOWNLOAD_CLIENT_HOME = '/applications/asplm/asplmint/cust_root_dir/cdm_importer/fdc/'
# Aktive config Verzsichniss
XML_INPUT_DIRECTORY = '/applications/local/config/fdc/'
#XML_INPUT_DIRECTORY = '/applications/asplm/asplmint/cust_root_dir/cdm_importer/fdc_1.0.0/input_configs_test'
#XML_INPUT_DIRECTORY = '/applications/asplm/asplmint/cust_root_dir/cdm_importer/fdc/testConfig/'
Log_OUTPUT = '/applications/logs/fdc/'
JAVA_PATH='/applications/asplm/asplmint/java/jdk17/bin/'
#CREDENTIALS='/applications/asplm/asplmint/cust_root_dir/cdm_importer/fdc/secure/EncryptedCred_PROD.txt'
CREDENTIALS='/applications/asplm/asplmint/security/fdc/encrypted_cred.txt'

Move_PLMXML_FROM='/mounts/import/cdm/VISVIEW/AS-PLM_fdc/'
Move_PLMXML_TO='/mounts/import/cdm/VISVIEW/AS-PLM/'
MOVE_PLMXML=True

ENVIRONMENT_TO_CONNECT='PROD'
#userpid ist mit dem alten interne Credentials-Dateim verbunden
#USERPID='pid5457'
USERPID='pid1489'
STATUS_CHECK_INTERVAL=5
MAX_Processes=15


# Thanks.
################################################################################
