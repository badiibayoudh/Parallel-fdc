#!/bin/bash

# Verzeichnis mit den .plmxml-Dateien
#verzeichnis="/applications/local/config/fdc"
verzeichnis="/applications/local/config/fdc/tmp"

# Zu ersetzender Text und der neue Text
alter_text="/mounts/import/cdm/geo/jt"
neuer_text="/mounts/import/cdm/geo/jt/AS-PLM"

# Überprüfen, ob das Verzeichnis existiert
if [ ! -d "$verzeichnis" ]; then
  echo "Verzeichnis $verzeichnis existiert nicht."
  exit 1
fi

# Alle .plmxml-Dateien im Verzeichnis durchlaufen
for datei in "$verzeichnis"/*.xml; do
  # Überprüfen, ob Dateien gefunden wurden
  if [ ! -f "$datei" ]; then
    echo "Keine .xml-Dateien im Verzeichnis $verzeichnis gefunden."
    exit 1
  fi

  # Ersetzen des alten Textes durch den neuen in der Datei
   sed -i "s|$alter_text|$neuer_text|g" "$datei"

  echo "Ersetzt: $alter_text durch $neuer_text in $datei"
done

echo "Textänderungen in allen .xml-Dateien abgeschlossen."

