import os

def list_xml_files_sorted(directory):
    try:
        # Liste aller XML-Dateien im angegebenen Pfad abrufen und nach Namen sortieren
        xml_files = sorted(
            [f for f in os.listdir(directory) if f.endswith('.xml') and os.path.isfile(os.path.join(directory, f))]
        )
        return xml_files
    except FileNotFoundError:
        return f"Das Verzeichnis '{directory}' wurde nicht gefunden."
    except PermissionError:
        return f"Zugriff auf das Verzeichnis '{directory}' verweigert."

# Beispielaufruf
directory_path = "D:\git\Parallel-fdc\linux\configs_INT_06092024\\fdc"
print(list_xml_files_sorted(directory_path))
