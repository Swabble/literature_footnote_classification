# dkuzwekce: Zuordnung von Fußnoten zu Literatureinträgen

Dieses Projekt demonstriert, wie automatisiert Fußnoten den passenden Literatureinträgen zugeordnet werden können. Die Umsetzung greift beispielhaft auf ein Language Model (LLM) zurück und zeigt die dazugehörige Datenverarbeitung. Alle Module befinden sich im Verzeichnis `src/`.

## Projektstruktur

```
.
├── data/                 # Beispiel­daten für Literatur und Fußnoten
├── prompt_templates/     # Vorlage für den LLM-Prompt
├── src/                  # Python-Module
├── run.py                # Einstiegspunkt des Programms
└── requirements.txt      # Benötigte Python-Abhängigkeiten
```

### Daten
- **data/literature.json** enthält einige Literatureinträge im JSON‑Format.
- **data/footnotes.html** beinhaltet die zugehörigen Fußnoten als HTML‑Datei.

Beim Einlesen erhalten alle Literatureinträge einen Schlüssel in der Form `L00001`, `L00002`, … und jede Fußnote einen Schlüssel `F00001`, `F00002`, ….

## Installation
1. Python 3.9 oder neuer installieren.
2. Optional: ein virtuelles Environment anlegen:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Benötigte Pakete installieren:
   ```bash
   pip install -r requirements.txt
   ```

## Konfiguration
Im Projektverzeichnis befindet sich eine Datei `config.json` mit den Einstellungen für das LLM. Beispielinhalt:

```json
{
  "api_key": "YOUR_API_KEY",
  "model": "gpt-4.1-nano",
  "max_tokens": 500,
  "temperature": 0.3,
  "request_interval": 1.0
}
```

Ohne `api_key` wird automatisch der `DummyAPIClient` verwendet.
Der Parameter `request_interval` gibt die minimale Zeit in Sekunden zwischen zwei
LLM-Aufrufen an und hilft, "Too Many Requests"-Fehler zu vermeiden.

## Ausführung
Das Programm kann direkt über `run.py` gestartet werden. Es liest die Daten ein, ruft das (hier simulierte) LLM über den `LLMClient` an und schreibt Fortschrittsinformationen in `status.json`. Die Protokollierung wird zentral durch den `LoggingManager` gesteuert.

```bash
python run.py
```

Während der Ausführung wird ein detailliertes Protokoll in der Datei `app.log` erzeugt.

Nach dem Lauf befindet sich im aktuellen Verzeichnis eine Datei `status.json`, die Informationen über den zuletzt verarbeiteten Eintrag bzw. Fehler enthalten kann.

## Tests
Der Beispielcode enthält derzeit keine Unit‑Tests, dennoch kann `pytest` ausgeführt werden:

```bash
pytest -q
```

