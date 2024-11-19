import os

def dateien_auflisten(verzeichnis):
    alle_dateien = []
    for wurzel, _, dateien in os.walk(verzeichnis):
        for datei in dateien:
            alle_dateien.append(os.path.join(wurzel, datei))
    return alle_dateien

def dateien_anzeigen(dateien):
    for datei in dateien:
        print(datei)
        
# Beispielverzeichnis und Ausführung
verzeichnis = "D:\git\Parallel-fdc\linux"
dateien = dateien_auflisten(verzeichnis)
dateien_anzeigen(dateien)
    