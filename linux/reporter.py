import os
import re
from datetime import datetime, timedelta
import csv

import logging
logger = logging.getLogger('fdc_Manager')

def get_unique_file_handles(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    unique_file_handles_line = re.search(r"Handles nach der Entfernung von Duplikaten: (.+)", content)
    if unique_file_handles_line is None:
        return "-"
    else:
        return unique_file_handles_line.group(1).strip()

def get_download_error_count(file_path):
    not_downloaded_files_line = None
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if "-Elemente konnten aufgrund von Fehlern nicht heruntergeladen werden:" in line:
                not_downloaded_files_line = line
                break

    if not_downloaded_files_line is None:
        return "-"
    else:
        return not_downloaded_files_line.split("-")[0].strip().split(" ")[2]

def get_file_count_to_download(file_path):
    file_count_to_download = None
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if " Handles werden heruntergeladen" in line:
                file_count_to_download = line
                break

    if file_count_to_download is None:
        return "-"
    else:
        file_count_to_download_part_ii = file_count_to_download.split(".")[1]
        if file_count_to_download_part_ii is None:
            return "-"
        else:
            return file_count_to_download_part_ii.split(" ")[1]

def get_last_mod_time_of_file(file_path):
    last_mod_time_string = "-"
    if os.path.isfile(file_path):
        last_mod_time = os.path.getmtime(file_path)
        last_mod_time_string = datetime.fromtimestamp(last_mod_time).strftime("%d.%m.%Y %H:%M:%S")
    return last_mod_time_string

def get_first_start_time(job_data_hash):
    first_start_time = datetime.max
    for job in job_data_hash.keys():
        if first_start_time > job_data_hash[job]:
            first_start_time = job_data_hash[job]
    return first_start_time

def is_date(str_date):
    try:
        datetime.strptime(str_date, "%d.%m.%Y %H:%M:%S")
        return True
    except ValueError:
        return False

def add_job_to_hash(jobs_by_time_hash, start_time_string, job_name):
    if is_date(start_time_string):
        start_time = datetime.strptime(start_time_string, "%d.%m.%Y %H:%M:%S")
        rounded_start_time = start_time.replace(second=0, microsecond=0)  # time with minute precision
        if rounded_start_time not in jobs_by_time_hash:
            jobs_by_time_hash[rounded_start_time] = []
        jobs_by_time_hash[rounded_start_time].append(job_name)

def xml_dateinamen_auflisten(verzeichnis):
    """Listet die Namen aller .xml-Dateien ohne Extension in einem Verzeichnis auf."""
    dateinamen = [os.path.splitext(datei)[0] for datei in os.listdir(verzeichnis) if datei.endswith('.xml')]
    return dateinamen

def generateReport(FdcLogRootDir, FdcRuntimeCSV, FdcRunningJobCountCSV, FdcConfigDir):
    logger.info('Generating Reports: {} und {}'.format(FdcRuntimeCSV, FdcRunningJobCountCSV))
    
    # Collect the names of FDC configuration files
    all_configs = xml_dateinamen_auflisten(FdcConfigDir)
    
    csv_header_line = "JobName;StartTime;ReportReadyTime;UniqueJTCount;JTsToDownloadCount;JTDownloadErrorCount;JTDownloadCompleteTime;EndTime"
    with open(FdcRuntimeCSV, 'w', newline='') as file:
        file.write(csv_header_line + '\n')

    jobs_by_start_time_hash = {}
    jobs_by_end_time_hash = {}
    start_times_by_job_hash = {}
    end_times_by_job_hash = {}
    jobs = []

    for dir_name, _, _ in os.walk(FdcLogRootDir):
        job_log_dir = dir_name
        if os.path.isfile(os.path.join(job_log_dir, "FDCUserLog.txt")):
            job_name = os.path.basename(job_log_dir)

            # SMA-291: Bei der Erstellung der Monitoring-Datei werden nur FDC.logs berücksichtigt, zu welchen ein Konfig.xml vorhanden.
            if not job_name in all_configs:
                continue
            
            start_time_string = get_last_mod_time_of_file(os.path.join(job_log_dir, "FDC.START"))
            report_ready_time = get_last_mod_time_of_file(os.path.join(job_log_dir, "FDC.PLMXML.SUCCESS"))
            model_download_complete_time = get_last_mod_time_of_file(os.path.join(job_log_dir, "FDC.PHYSICAL_FILES.SUCCESS"))
            
            # SMA-291: Entfernen der Suche nach JTDownloadCompleteTime mit  FDC.PHYSICAL_Files.Error. Soll nur in FDC.PHYSICAL_Files_Success gesucht werden. Wenn Success nicht vorhanden, dann keine Endzeit, dann einen "-" (Strich) eintragen
            #if model_download_complete_time == "-":
            #    model_download_complete_time = get_last_mod_time_of_file(os.path.join(job_log_dir, "FDC.PHYSICAL_FILES.ERROR"))
            end_time_string = get_last_mod_time_of_file(os.path.join(job_log_dir, "FDC.END"))

            unique_file_handles = get_unique_file_handles(os.path.join(job_log_dir, "FDCUserLog.txt"))
            files_to_download = get_file_count_to_download(os.path.join(job_log_dir, "FDCUserLog.txt"))
            download_error_count = get_download_error_count(os.path.join(job_log_dir, "FDCUserLog.txt"))

            jobs.append(job_name)
            add_job_to_hash(jobs_by_start_time_hash, start_time_string, job_name)
            add_job_to_hash(jobs_by_end_time_hash, end_time_string, job_name)
            start_times_by_job_hash[job_name] = start_time_string
            end_times_by_job_hash[job_name] = end_time_string

            csv_line = f"{job_name};{start_time_string};{report_ready_time};{unique_file_handles};{files_to_download};{download_error_count};{model_download_complete_time};{end_time_string}"
            #logger.info(csv_line)
            with open(FdcRuntimeCSV, 'a', newline='') as file:
                file.write(csv_line + '\n')
        else:
            logger.info(f"No FDCUserLog.txt found in {job_log_dir} -> Skipping!")

    running_job_count_hash = {}
    first_start_time = min(jobs_by_start_time_hash.keys())
    last_end_time = max(jobs_by_end_time_hash.keys())

    t = first_start_time
    while t <= last_end_time:
        running_job_count_hash[t] = []

        for job in jobs:
            if (start_times_by_job_hash[job] == "-") and (end_times_by_job_hash[job] == "-"):
                continue
            elif (start_times_by_job_hash[job] == "-") and is_date(end_times_by_job_hash[job]):
                continue  # Error case
            elif is_date(start_times_by_job_hash[job]) and (end_times_by_job_hash[job] == "-"):
                running_job_count_hash[t].append(job)  # job still running
            elif (datetime.strptime(start_times_by_job_hash[job], "%d.%m.%Y %H:%M:%S") <= t <=
              datetime.strptime(end_times_by_job_hash[job], "%d.%m.%Y %H:%M:%S")):
                running_job_count_hash[t].append(job)
            
        t = t + timedelta(minutes=1)
    
    csv_runtime_header_line = "DateTime;RunningJobCount" 
    with open(FdcRunningJobCountCSV, 'w', newline='') as file:
        file.write(csv_runtime_header_line + '\n')

    for t in sorted(running_job_count_hash.keys()):
        time_string = t.strftime("%d.%m.%Y %H:%M:%S")
        running_job_count = len(running_job_count_hash[t])
        csv_line = f"{time_string};{running_job_count}"
        #logger.info(csv_line)
        with open(FdcRunningJobCountCSV, 'a', newline='') as file:
            file.write(csv_line + '\n')


### Testing ###
#FDC_LOG_ROOT_DIR = r"D:\git\Parallel-fdc\Testdaten\logs"
#FDC_RUNTIME_CSV = r"D:\git\Parallel-fdc\Testdaten\FDC-Runtime-new.csv"
#FDC_RUNNING_JOB_COUNT_CSV = r"D:\git\Parallel-fdc\Testdaten\FDC-RunningJobCount-new.csv"
#generateReport(FDC_LOG_ROOT_DIR, FDC_RUNTIME_CSV, FDC_RUNNING_JOB_COUNT_CSV)