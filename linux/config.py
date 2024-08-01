
###### Please configure the client by entering the settings below.. ##########
# lokal windows gegen Smaragd-PRD (nur für Test)

STATUS_CHECK_INTERVAL=5
MAX_Processes=5
COPY_PLMXML=False

XML_INPUT_DIRECTORY = 'D:/git/Parallel-fdc/windows/configsPrd/'
FILE_DOWNLOAD_CLIENT_HOME = 'D:/git/Parallel-fdc/'
Log_OUTPUT = 'D:/git/Parallel-fdc/logs/'
JAVA_PATH='D:/Apps/Java/jdk-17/jdk-17.0.7/bin/'
CREDENTIALS_PATH='D:/git/Parallel-fdc/EncryptedCred_PROD.txt'
Move_PLMXML_FROM='D:/git/Parallel-fdc/test/plmxml_fdc'
Move_PLMXML_TO='D:/git/Parallel-fdc/test/plmxml'
COPY_PLMXML=True
ENVIRONMENT_TO_CONNECT='PROD'
USERPID='pid5457'


"""
# ASPLM-T3 gegen Smaragd-CRM
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
# ASPLM-T3 gegen Smaragd-PRD
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

"""
# ASPLM-INT gegen Smaragd-PRD
FILE_DOWNLOAD_CLIENT_HOME = '/applications/asplm/asplmint/cust_root_dir/cdm_importer/fdc/'
XML_INPUT_DIRECTORY = '/applications/asplm/asplmint/cust_root_dir/cdm_importer/fdc/configs/'
Log_OUTPUT = '/applications/asplm/asplmint/cust_root_dir/cdm_importer/fdc/logs/'
JAVA_PATH='/applications/asplm/asplmint/cust_root_dir/cdm_importer/fdc/java/jdk-17.0.11/bin/'
CREDENTIALS='/applications/asplm/asplmint/cust_root_dir/cdm_importer/fdc/EncryptedCred_PROD.txt'

Move_PLMXML_FROM='/mounts/import/cdm/VISVIEW/AS-PLM_fdc/'
Move_PLMXML_TO='/mounts/import/cdm/VISVIEW/AS-PLM/'
COPY_PLMXML=False

ENVIRONMENT_TO_CONNECT='PROD'
USERPID='pid5457'
STATUS_CHECK_INTERVAL=5
MAX_Processes=5
"""

# Thanks.
################################################################################