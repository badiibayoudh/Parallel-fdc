import yaml
import os

def load_config_with_env_required(filename="application.yml"):
    """
    Lädt eine YAML-Datei und ersetzt Platzhalter durch Werte aus den Umgebungsvariablen.
    Wirft eine Exception, wenn eine erforderliche Umgebungsvariable fehlt.

    :param yaml_file: Pfad zur YAML-Datei
    :return: Dictionary mit aufgelöster Konfiguration
    """
    def resolve_env(value):
        """
        Ersetzt Platzhalter im Format ${VAR} mit Umgebungsvariablen.
        Wirft eine Exception, wenn die Variable nicht gesetzt ist.
        """
        if isinstance(value, str) and "${" in value:
            start = value.find("${") + 2
            end = value.find("}", start)
            var_name = value[start:end]
            env_value = os.getenv(var_name)
            if env_value is None:
                raise ValueError(f"Die erforderliche Umgebungsvariable '{var_name}' ist nicht gesetzt.")
            return env_value
        return value

    def recursive_resolve(config):
        """
        Rekursive Verarbeitung der YAML-Datenstruktur.
        """
        if isinstance(config, dict):
            return {k: recursive_resolve(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [recursive_resolve(i) for i in config]
        else:
            return resolve_env(config)

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the full path to the YAML file
    file_path = os.path.join(script_dir, filename)
    
    with open(file_path, 'r') as file:
        try:
            raw_config = yaml.safe_load(file)
        except yaml.YAMLError as e:
            print("Error reading YAML file:", e)
            return None
        
        resolved_config = recursive_resolve(raw_config)
        return resolved_config

def read_yaml_properties(filename="application.yml"):
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the full path to the YAML file
    file_path = os.path.join(script_dir, filename)
    
    # Read the YAML file
    with open(file_path, 'r') as file:
        try:
            properties = yaml.safe_load(file)
            return properties
        except yaml.YAMLError as e:
            print("Error reading YAML file:", e)
            return None
        
###### Please configure the client by entering the settings below.. ##########

"""
XML_INPUT_DIRECTORY = 'D:/git/Parallel-fdc/windows/configsPrd/'
FILE_DOWNLOAD_CLIENT_HOME = 'D:/git/Parallel-fdc/'
Log_OUTPUT = 'D:/git/Parallel-fdc/logs/'
JAVA_PATH='D:/Apps/Java/jdk-17/jdk-17.0.7/bin/'
CREDENTIALS_PATH='D:/git/Parallel-fdc/EncryptedCred_PROD.txt'
Move_PLMXML_FROM='D:/git/Parallel-fdc/test/plmxml_fdc'
Move_PLMXML_TO='D:/git/Parallel-fdc/test/plmxml'
ENVIRONMENT_TO_CONNECT='PROD'
USERPID='pid5457'

MONITORING_PATH = 'D:\AS-PLM\Tests\Testdaten\Monitoring'
ARCHIVE_PATH = 'D:\AS-PLM\Tests\Testdaten\Archive'

#FDC_RUNTIME_CSV = r"D:\git\Parallel-fdc\Testdaten\FDC-Runtime-new.csv"
#FDC_RUNNING_JOB_COUNT_CSV = r"D:\git\Parallel-fdc\Testdaten\FDC-RunningJobCount-new.csv"

STATUS_CHECK_INTERVAL=5
MAX_Processes=5
MOVE_PLMXML=False
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

FDC_RUNTIME_CSV = '/applications/logs/fdc/'
FDC_RUNNING_JOB_COUNT_CSV = '/applications/logs/fdc/'

STATUS_CHECK_INTERVAL=5
MAX_Processes=5
waitTimeBeforeClose=30    


"""

"""
# INT gegen PRD
FILE_DOWNLOAD_CLIENT_HOME = '/applications/asplm/asplmint/cust_root_dir/cdm_importer/fdc/'
# Aktive config Verzsichniss
XML_INPUT_DIRECTORY = '/applications/local/config/fdc/'
#XML_INPUT_DIRECTORY = '/applications/asplm/asplmint/cust_root_dir/cdm_importer/fdc_1.0.0/input_config_RegressionTests'
#XML_INPUT_DIRECTORY = '/applications/asplm/asplmint/cust_root_dir/cdm_importer/fdc_1.0.0/input_configs_test'
#XML_INPUT_DIRECTORY = '/applications/asplm/asplmint/cust_root_dir/cdm_importer/fdc/testConfig/'
Log_OUTPUT = '/applications/logs/fdc/'
JAVA_PATH='/applications/asplm/asplmint/java/jdk17/bin/'
#CREDENTIALS='/applications/asplm/asplmint/cust_root_dir/cdm_importer/fdc/secure/EncryptedCred_PROD.txt'
CREDENTIALS='/applications/asplm/asplmint/security/fdc/encrypted_cred.txt'

Move_PLMXML_FROM='/mounts/import/cdm/VISVIEW/AS-PLM_fdc/'
Move_PLMXML_TO='/mounts/import/cdm/VISVIEW/AS-PLM/'
MOVE_PLMXML=True

MONITORING_PATH = '/applications/logs/fdc/monitoring'
ARCHIVE_PATH = '/applications/logs/fdc/archive'

FDC_MAP= '/mounts/import/cdm/MAP_fdc'

STATUS_CHECK_INTERVAL=1
MAX_Processes=15

ENVIRONMENT_TO_CONNECT='PROD'

#userpid ist mit dem alten interne Credentials-Dateim verbunden
#USERPID='pid5457'

USERPID='pid1489'


"""
# Thanks.
################################################################################
