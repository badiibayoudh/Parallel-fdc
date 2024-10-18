@echo off
setlocal enabledelayedexpansion

:: Verzeichnis, in dem die Dateien erstellt werden
set "target_dir=D:\AS-PLM\Tests\Testdaten"

:: Falls das Verzeichnis nicht existiert, wird es erstellt
if not exist "%target_dir%" (
    mkdir "%target_dir%"
)

:: Anzahl der zu erstellenden Dateien
set num_files=100

:: Schleife, um die Dateien zu erzeugen
for /l %%i in (1,1,%num_files%) do (
    :: Erstelle eine leere Datei mit einem einzigartigen Namen
    set "filename=file_%%i.txt"
    echo.>"%target_dir%\!filename!"
    
    :: Generiere eine zufällige Anzahl von Tagen zwischen 20 und 300
    set /a "days_ago=!random! %% 281 + 20"
    
    :: Berechne das Datum für den Dateistempel
    for /f %%a in ('powershell -command "(Get-Date).AddDays(-!days_ago!).ToString('yyyyMMddHHmmss')"') do set "mod_date=%%a"
    
    :: Setze den Zeitstempel der Datei mit PowerShell
    powershell -command "(Get-Item '%target_dir%\!filename!').LastWriteTime = [datetime]::ParseExact('!mod_date!', 'yyyyMMddHHmmss', $null)"
)

echo %num_files% Dateien wurden im Verzeichnis %target_dir% erstellt.
