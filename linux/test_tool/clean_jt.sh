#!/bin/bash

# Das Hauptverzeichnis, in dem die Unterverzeichnisse gelöscht werden sollen
hauptverzeichnis="/mounts/import/cdm/geo/jt"

# Das Verzeichnis, das NICHT gelöscht werden soll
behalten_verzeichnis="AS-PLM"

# Überprüfen, ob das Hauptverzeichnis existiert
if [ ! -d "$hauptverzeichnis" ]; then
  echo "Das Verzeichnis $hauptverzeichnis existiert nicht."
  exit 1
fi

# Schleife durch alle Unterverzeichnisse im Hauptverzeichnis
for verzeichnis in "$hauptverzeichnis"/*; do
  if [ -d "$verzeichnis" ]; then
    # Name des aktuellen Verzeichnisses extrahieren
    basename_verzeichnis=$(basename "$verzeichnis")
    
    # Überprüfen, ob das Verzeichnis das zu behaltende ist
    if [ "$basename_verzeichnis" != "$behalten_verzeichnis" ]; then
      echo "Lösche Verzeichnis: $verzeichnis"
      rm -rf "$verzeichnis"
    else
      echo "Behalte Verzeichnis: $verzeichnis"
    fi
  fi
done

echo "Aufräumen abgeschlossen."

