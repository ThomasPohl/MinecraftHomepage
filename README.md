# Niklas' Befehlsbuch

Webseite mit einer Übersicht aller Konsolen-Commands für Minecraft (Java und Bedrock) unter
[niklaspohl.de](https://niklaspohl.de).

- sortierbare und filterbare Tabelle (Edition, Kategorie, Berechtigung, Suche, Favoriten)
- Detailseite je Command mit **Command-Builder**: Werte auswählen, fertigen Command kopieren
- Umschalter Java/Bedrock, die letzte Auswahl wird gemerkt
- Deutsch und Englisch, Tag- und Nachtmodus, für Handy und Desktop
- keine Cookies, keine externen Dienste, Schrift und Grafiken liegen lokal

Kein offizielles Minecraft-Produkt. Nicht von Mojang oder Microsoft genehmigt oder mit ihnen verbunden.

## Aufbau

| Pfad | Inhalt |
| --- | --- |
| `site/` | die Webseite; genau dieser Ordner wird hochgeladen |
| `site/data/commands/*.json` | die Commands (Daten getrennt vom Code) |
| `site/data/lists.json` | Auswahllisten für den Builder (Mobs, Effekte, Biome …) |
| `site/data/catalog.json` | Items und Blöcke mit deutschen/englischen Namen und Kategorien |
| `site/data/selectors.json` | Ziel-Auswahlen (`@s`, `@a` …) mit Erklärungen und Filter-Beispielen |
| `site/data/site.json` | Angaben fürs Impressum, Datenstand, Liste der Command-Dateien |
| `site/js/` | App-Logik (reines JavaScript, kein Build-Schritt) |
| `scripts/validate.mjs` | prüft die Daten, läuft auch bei jedem Push |
| `tools/build_catalog.py` | erzeugt den Item- und Block-Katalog aus PrismarineJS/minecraft-data |
| `tools/make_assets.py` | erzeugt die eigene Pixel-Schrift und die Pixel-Grafiken |
| `CLAUDE.md` | Pflegeanleitung: Datenformat und Arbeitsweise |

## Lokal ansehen

```bash
python3 -m http.server 8000 --directory site
# dann http://localhost:8000 öffnen
```

Daten prüfen: `node scripts/validate.mjs`

## Deployment zu Netbeat

Jeder Push auf `main` prüft die Daten und lädt danach `site/` per FTP hoch
(`.github/workflows/deploy.yml`). Einmalig im GitHub-Repository einzurichten unter
*Settings → Secrets and variables → Actions*:

| Art | Name | Wert |
| --- | --- | --- |
| Secret | `FTP_SERVER` | FTP-Servername von Netbeat |
| Secret | `FTP_USERNAME` | FTP-Benutzer |
| Secret | `FTP_PASSWORD` | FTP-Passwort |
| Variable (optional) | `FTP_SERVER_DIR` | Zielordner der Domain, z. B. `./httpdocs/` (mit Schrägstrich am Ende) |
| Variable (optional) | `FTP_PROTOCOL` | `ftps` (Standard, verschlüsselt) oder `ftp` |

## Impressum

Anschrift und E-Mail stehen in `site/data/site.json`. Solange Felder leer sind, zeigt die Seite
dort eine gelbe Markierung „bitte ergänzen“.

## Lizenz

Apache License 2.0, siehe `LICENSE`. Texte, Pixel-Grafiken und die Schrift „Blockschrift“ wurden
für dieses Projekt selbst erstellt.
