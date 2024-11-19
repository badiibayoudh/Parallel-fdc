import os

def xml_dateinamen_auflisten(verzeichnis):
    """Listet die Namen aller .xml-Dateien ohne Extension in einem Verzeichnis auf."""
    dateinamen = [os.path.splitext(datei)[0] for datei in os.listdir(verzeichnis) if datei.endswith('.xml')]
    return dateinamen

def dateinamen_anzeigen(dateinamen):
    """Zeigt die Namen der Dateien an."""
    for name in dateinamen:
        print(name)

# Beispielverzeichnis und Ausführung
verzeichnis = "D:\git\Parallel-fdc\linux\configs"
dateinamen = xml_dateinamen_auflisten(verzeichnis)
dateinamen_anzeigen(dateinamen)
