# Anzahl der zu erstellenden Dateien
anzahl_dateien=100

# Verzeichnis, in dem die Dateien erstellt werden sollen
verzeichnis="/applications/logs/fdc"

# Verzeichnis erstellen, wenn es noch nicht existiert
mkdir -p "$verzeichnis"

# Dateien erzeugen
for i in $(seq 1 $anzahl_dateien); do
  # Dateiname
  datei="$verzeichnis/datei_test_cron$i.log"

  # Datei erstellen
  touch "$datei"

  # Zufällige Anzahl von Tagen in der Vergangenheit (zwischen 20 und 300)
  tage=$((RANDOM % 281 + 10))

  # Das Änderungsdatum der Datei auf die entsprechende Zeit setzen
  # Aktuelles Datum minus die zufällige Anzahl von Tagen
  timestamp=$(date -d "$tage days ago" +"%Y%m%d%H%M")

  # Setze den Zeitstempel der Datei
  touch -t "$timestamp" "$datei"

  echo "Erstellt: $datei mit Zeitstempel vor $tage Tagen"
done

echo "Fertig! $anzahl_dateien Dateien wurden erstellt."
