# Pflegeanleitung (für Claude und Menschen)

Statische Seite ohne Build-Schritt und ohne Abhängigkeiten. `site/` wird 1:1 per FTP zu Netbeat
hochgeladen (Push auf `main`). Nichts einführen, was einen Build oder externe Dienste braucht.

## Regeln

- **Daten und Code trennen.** Inhalte gehören nach `site/data/`, nicht in `site/js/`.
- **Urheberrecht.** Beschreibungen immer selbst formulieren, nie aus dem Minecraft-Wiki, von
  Microsoft Learn oder anderen Seiten übernehmen. Keine Mojang-Grafiken, -Texturen, -Schriften
  oder -Logos. Grafiken und Schrift kommen nur aus `tools/make_assets.py`. Ausnahme für Fakten: Block-IDs und englische Blocknamen stammen aus den
  offenen Registry-Daten von PrismarineJS/minecraft-data (siehe Katalog).
- **Keine externen Anfragen** (keine CDNs, Google Fonts, Analytics). Der Datenschutztext sagt das zu.
- **Zweisprachig.** Jeder Text braucht `de` und `en`. Oberflächen-Texte stehen in `site/js/i18n.js`.
- Der Hinweis „Kein offizielles Minecraft-Produkt …“ im Fuß muss bleiben; der Seitentitel darf
  nicht mit „Minecraft“ beginnen.
- Vor jedem Commit: `node scripts/validate.mjs`. Bei Änderungen an Aussehen oder Verhalten im
  Browser prüfen (`python3 -m http.server 8000 --directory site`), auch schmal (Handy) und im Nachtmodus.

## Einen Command hinzufügen oder ändern

Eintrag in der passenden Datei unter `site/data/commands/` (neue Datei zusätzlich in
`site/data/site.json` → `commandFiles` eintragen):

```json
{
  "id": "give", "cat": "items",
  "java":    { "perm": 2,    "since": "1.3.1",  "forms": ["<targets:player> <item:item> [count:int]"], "ex": "/give @s diamond 64" },
  "bedrock": { "perm": "gd", "since": "0.16.0", "forms": ["<player:player> <itemName:item> [amount:int]"], "ex": "/give @s diamond 64" },
  "de": { "short": "Ein Satz für die Tabelle.", "details": "Ein bis drei Sätze für die Detailseite." },
  "en": { "short": "…", "details": "…" }
}
```

- `cat`: `world`, `player`, `items`, `entities`, `chat`, `effects`, `logic`, `server`
- `java` / `bedrock`: weglassen, wenn es den Command in der Edition nicht gibt
- `perm`: Java `0`–`4` (OP-Level); Bedrock `any`, `gd` (Operator), `admin`, `host`, `owner`
- `cheats: false` (nur Bedrock): Command geht auch ohne aktivierte Cheats
- `name`: abweichender Name in dieser Edition (z. B. `xp`, `allowlist`); `alias`: weitere Namen
- `since`: Version der Einführung; weglassen, wenn nicht sicher bekannt
- `ex`: ein funktionierendes Beispiel, beginnt mit `/name`

### Formen

Jede Zeile in `forms` ist eine Schreibweise des Commands (ohne `/name`), aus der Tabelle,
Syntax-Anzeige und Builder entstehen:

| Schreibweise | Bedeutung |
| --- | --- |
| `wort` | fester Text |
| `(a\|b\|c)` | Pflicht-Auswahl aus festen Wörtern |
| `<name:typ>` | Pflicht-Parameter |
| `[name:typ]` | optionaler Parameter (nur am Ende der Form) |
| `<name:typ=wert>` | mit Vorgabewert |

Typen: `int`, `float`, `bool`, `text`, `pos` (x y z), `pos2` (x z), `rot` (yaw pitch), `target`,
`player`, `item`, `block` (aus dem Katalog), eine Inline-Auswahl `a|b|c` oder der Name einer Liste aus `site/data/lists.json`
(`entity`, `effect`, `enchantment`, `biome`, `structure`, `gamerule` …).
Formen dürfen keine Leerzeichen innerhalb eines Tokens enthalten. Bei sehr komplexen Commands
(z. B. `/execute`) nur die häufigsten Formen aufnehmen und das in `details` erwähnen.

## Listen (`site/data/lists.json`)

Array (gilt für beide Editionen), `{ "java": [...], "bedrock": [...] }` oder zusätzlich
`"free": true`. Listen ohne `free` mit höchstens 15 Einträgen werden als Dropdown gezeigt, alle
anderen als durchsuchbares Feld, in das man auch eigene Werte tippen kann. IDs unterscheiden
sich teils zwischen Java und Bedrock (z. B. `villager` / `villager_v2`).

## Item- und Block-Katalog (`site/data/catalog.json`)

Parameter vom Typ `item` und `block` zeigen eine Auswahl mit Kategorie-Filter, Suche und
deutschen/englischen Namen sowie ein freies Feld für eigene IDs. Eintrag:
`[id, deutscher Name, englischer Name, Kategorie, Art]`; Art `i` = nur Item (Standard), `b` = nur
Block, `ib` = beides. Ein optionales sechstes Feld nennt die Edition (`j` = nur Java, `b` = nur
Bedrock), weil manche IDs sich unterscheiden (Java `light`, Bedrock `light_block_15`).
Deutsche Namen wie im Spiel schreiben.

- **Blöcke** (Art `b`/`ib`) werden vollständig erzeugt, nicht von Hand gepflegt:
  `python3 -I tools/build_block_catalog.py <minecraft-data> <java-version> <bedrock-version>`
  mit einem Checkout von github.com/PrismarineJS/minecraft-data (liefert nur IDs und englische
  Namen). Deutsche Namen, Kategorien, ausgeschlossene technische Blöcke und Bedrock-Aliasse
  stehen als Regeln und Tabellen im Skript; Korrekturen dort eintragen und neu erzeugen.
- **Reine Items** (Art `i`) sind eine handgepflegte Auswahl häufiger Items; das Skript lässt sie stehen.

## Ziel-Auswahlen (`site/data/selectors.json`)

Parameter vom Typ `target` und `player` zeigen ein Dropdown mit erklärten Selektoren (`@s`, `@p` …)
plus ein freies Feld für Spielernamen oder Filter; darunter steht eine Hilfe mit Filter-Beispielen.
`player: true` heißt, der Selektor wählt nur Spieler aus und ist auch bei Typ `player` erlaubt.
Filter-Beispiele sind je Edition getrennt (Java `distance=..10`, Bedrock `r=10`).

## Nach einem Minecraft-Update

1. Changelogs von Java und Bedrock auf neue, geänderte oder entfernte Commands prüfen
   (offizielle Quellen: minecraft.net-Changelogs, Microsoft Learn für Bedrock).
2. Daten und Listen anpassen, `dataVersion` in `site/data/site.json` aktualisieren.
3. Validieren, im Browser prüfen, committen.

Bekannte Lücken: Bei `/posteffect`, `/compute`, `/publish` und `/swing` (Java 26.x) ist die
Syntax nur grob erfasst; `since` fehlt bei Commands, deren Einführungsversion nicht sicher belegt war.

## Schrift und Grafiken

`python3 tools/make_assets.py` (benötigt fontTools) erzeugt `site/fonts/blockschrift.woff` und
`site/img/*.svg` neu. Die Schrift enthält nur Großbuchstaben, Ziffern und einige Satzzeichen;
sie wird für Überschriften, Knöpfe und Abzeichen benutzt, Fließtext nutzt die Systemschrift.
