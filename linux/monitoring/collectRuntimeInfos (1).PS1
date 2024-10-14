function getUniqueFileHandles{
  param($filePath)
  
  $uniqueFileHandlesLine = select-String -Path $filePath -Pattern "Handles nach der Entfernung von Duplikaten: "
  if ($uniqueFileHandlesLine -eq $null)
  {
    return "-"
  }
  else
  {
    return $uniqueFileHandlesLine.Line.Split("\:")[1].Trim()
  }
}

function getDownloadErrorCount{
  param($filePath)
  
  $notDownloadedFilesLine = select-String -Path $filePath -Pattern "-Elemente konnten aufgrund von Fehlern nicht heruntergeladen werden:"
  if ($notDownloadedFilesLine -eq $null)
  {
    return "-"
  }
  else
  {
    return $notDownloadedFilesLine.Line.Split("\-")[0].Trim().Split(" ")[2]
  }
}



function getFileCountToDownload{
  param($filePath)
  
  $fileCountToDownload = select-String -Path $filePath -Pattern " Handles werden heruntergeladen"
  if ($fileCountToDownload -eq $null)
  {
    return "-"
  }
  else
  {
      $fileCountToDownload_PartII = $fileCountToDownload.Line.Split("\.")[1]
      if ($fileCountToDownload_PartII -eq $null)
      {
        return "-"
      }
      else
      {
         return $fileCountToDownload_PartII.Split(" ")[1]
      }
  }
}

function getLastModTimeOfFile{
 param ($filePath)

  $lastModTimeString = "-"
  if (Test-Path $filePath -PathType Leaf)
  {
    $lastModTimeString = (Get-Item "$filePath").LastWriteTime.ToString("dd.MM.yyyy HH:mm:ss")
  }
  return $lastModTimeString
}

function getFirstStartTime{
 param ($jobDataHash)

  $firstStartTime = DateTime.MaxValue

  ForEach($job in $jobDataHash.Keys)
  {
    if ($firstStartTime > $jobDataHash[$job])
    {
      $firstStartTime = $jobDataHash[$job]
    }
  }

  return $firstStartTime
}

function isDate([string]$strdate)
{
    [boolean]($strdate -as [DateTime])
}

function addJobToHash{
 param ($jobsByTimeHash, 
        [string] $startTimeString, 
        [string] $jobName)

 if (isDate($startTimeString))
  {
    $startTime = ($startTimeString -as [DateTime])
    $roundedStartTime = $startTime.AddSeconds(-$startTime.Second).AddMilliseconds(-$startTime.Millisecond) #time with minute precision
    if ($jobsByTimeHash[$roundedStartTime] -eq $NULL)
    {
      $jobsByTimeHash[$roundedStartTime] = New-Object System.Collections.ArrayList
    }
    $jobsByTimeHash[$roundedStartTime].Add($jobName)
  }
}



$FDC_LOG_ROOT_DIR = "D:\git\Parallel-fdc\Testdaten\logs"
$FDC_RUNTIME_CSV = "D:\git\Parallel-fdc\Testdaten\FDC-Runtime.csv"
$FDC_RUNNING_JOB_COUNT_CSV = "D:\git\Parallel-fdc\Testdaten\FDC-RunningJobCount.csv"

# collect all log infos and create a csv file with the following columns:
# JobName;StartTime;ReportCreationTime;ModelDownloadCompleteTime;JTCountToDownload;EndTime

$csvHeaderLine = "JobName;StartTime;ReportReadyTime;UniqueJTCount;JTsToDownloadCount;JTDownloadErrorCount;JTDownloadCompleteTime;EndTime"
Set-Content $FDC_RUNTIME_CSV $csvHeaderLine

$jobsByStartTimeHash = @{}
$jobsByEndTimeHash = @{}
$startTimesByJobHash = @{}
$endTimesByJobHash = @{}
$jobs = New-Object System.Collections.ArrayList

ForEach($dirName in Get-ChildItem -Recurse -Directory $FDC_LOG_ROOT_DIR)
#ForEach($dirName in Get-ChildItem -Directory $FDC_LOG_ROOT_DIR)
{
  $jobLogDir = $dirName.FullName
  if (Test-Path "$jobLogDir\FDCUserLog.txt" -PathType Leaf)
  {
      $jobName = $dirName.Name
  
      $startTimeString = getLastModTimeOfFile("$jobLogDir\FDC.START")
      $reportReadyTime = getLastModTimeOfFile("$jobLogDir\FDC.PLMXML.SUCCESS")
      $modelDownloadCompleteTime = getLastModTimeOfFile("$jobLogDir\FDC.PHYSICAL_FILES.SUCCESS")
      if ($modelDownloadCompleteTime -eq "-")
      {
        $modelDownloadCompleteTime = getLastModTimeOfFile("$jobLogDir\FDC.PHYSICAL_FILES.ERROR")
      }
      $endTimeString = getLastModTimeOfFile("$jobLogDir\FDC.END")
  
      $uniqueFileHandles = getUniqueFileHandles("$jobLogDir\FDCUserLog.txt")
      $filesToDownload = getFileCountToDownload("$jobLogDir\FDCUserLog.txt")
      $downloadErrorCount = getDownloadErrorCount("$jobLogDir\FDCUserLog.txt")
  
      $jobs.Add($jobName)
      addJobToHash $jobsByStartTimeHash $startTimeString $jobName
      addJobToHash $jobsByEndTimeHash $endTimeString $jobName
      $startTimesByJobHash[$jobName] = $startTimeString
      $endTimesByJobHash[$jobName] = $endTimeString
  

      $csvLine = "$jobName;$startTimeString;$reportReadyTime;$uniqueFileHandles;$filesToDownload;$downloadErrorCount;$modelDownloadCompleteTime;$endTimeString"
      Write-Host $csvLine
      Add-Content $FDC_RUNTIME_CSV $csvLine
  }
  else
  {
    Write-Host "No FDCUserLog.txt found in $jobLogDir -> Skipping!"
  }
}

#calculate the number of running jobs in each minute between first start-time and last end-time
$runningJobCountHash = @{}

$firstStartTime = ($jobsByStartTimeHash.GetEnumerator() | Sort Name).Key[0]
$lastEndTime = ($jobsByEndTimeHash.GetEnumerator() | Sort Name)[$jobsByEndTimeHash.Count-1].Key[0]

For($t = $firstStartTime; $t -ile $lastEndTime; $t = $t.AddMinutes(1))
{
    $runningJobCountHash[$t] = New-Object System.Collections.ArrayList

    ForEach($job in $jobs)
    {
      if (($startTimesByJobHash[$job] -eq "-") -and ($endTimesByJobHash[$job] -eq "-"))
      {
        # do nothing
      }
      elseif (($startTimesByJobHash[$job] -eq "-") -and (isDate($endTimesByJobHash[$job])))
      {
        # Error case
      }
      elseif (isDate(($startTimesByJobHash[$job]) -and ($endTimesByJobHash[$job] -eq "-")))
      {
        # job still running
        $runningJobCountHash[$t].Add($job)
      }
      elseif ((($startTimesByJobHash[$job] -as [DateTime]) -le $t) -and ($t -le ($endTimesByJobHash[$job] -as [DateTime])))
      {
        $runningJobCountHash[$t].Add($job)
      }
    }
}

#write CSV
Set-Content $FDC_RUNNING_JOB_COUNT_CSV "DateTime;RunningJobCount"

foreach ($t in ($runningJobCountHash.GetEnumerator() | Sort Name).Key)
{
  $timeString = $t.toString("dd.MM.yyyy HH:mm:ss")
  $runningJobCount = $($runningJobCountHash[$t]).Count
  $csvLine = "$timeString;$runningJobCount"
  Write-Host $csvLine
  Add-Content $FDC_RUNNING_JOB_COUNT_CSV $csvLine
}
