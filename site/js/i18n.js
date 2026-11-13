// Alle Texte der Oberfläche in Deutsch und Englisch.
export const T = {
  de: {
    title: "Niklas' Befehlsbuch – Commands für Minecraft",
    tagline: 'Alle Konsolen-Commands für Java und Bedrock – zum Nachschlagen, Zusammenklicken und Kopieren.',
    themeDark: 'Nacht', themeLight: 'Tag',
    search: 'Suche', searchPh: 'z. B. teleport, Wetter, Items …',
    edition: 'Edition', all: 'Alle', both: 'Java + Bedrock',
    category: 'Kategorie', allCats: 'Alle Kategorien',
    permission: 'Berechtigung', allPerms: 'Alle Berechtigungen',
    favOnly: '★ Favoriten', sortBy: 'Sortieren nach',
    count: (n, total) => `${n} von ${total} Commands`,
    colName: 'Name', colDetails: 'Details', colSyntax: 'Syntax', colExample: 'Beispiel', colSince: 'Seit',
    noResults: 'Kein Command passt zu diesen Filtern.', resetFilters: 'Filter zurücksetzen',
    copy: 'Kopieren', copied: 'Kopiert!',
    favAdd: 'Als Favorit merken', favRemove: 'Favorit entfernen',
    more: (n) => `+${n} weitere`,
    back: '← Zur Übersicht',
    aliases: 'Auch', builder: 'Command-Builder', variant: 'Variante',
    builderHint: 'Wähle die Werte aus – unten entsteht der fertige Command.',
    yourCommand: 'Dein Command', missing: 'Es fehlen noch Pflichtangaben (in spitzen Klammern).',
    noParams: 'Dieser Command braucht in dieser Form keine weiteren Angaben.',
    optional: 'optional', choice: 'Auswahl', none: '– leer lassen –',
    customTarget: 'Spielername oder eigene Auswahl …',
    targetHelp: 'Welche Ziele kann ich angeben?',
    playerNameEx: 'Niklas', playerNameDesc: 'der Name eines Spielers, der gerade online ist',
    playersOnly: 'Bei diesem Command sind nur Spieler als Ziel erlaubt.',
    filterTitle: 'Genauer auswählen:', filterIntro: 'Hinter eine Auswahl kannst du Filter in eckige Klammern schreiben. Wähle dafür oben „Spielername oder eigene Auswahl“.',
    allForms: 'Alle Schreibweisen', example: 'Beispiel',
    onlyIn: (e) => `Diesen Command gibt es nur in der ${e} Edition.`,
    cheats: 'Cheats nötig', yes: 'Ja', no: 'Nein', unknown: '–',
    notFound: 'Diesen Command kenne ich nicht.',
    loadError: 'Die Daten konnten nicht geladen werden. Bitte lade die Seite neu.',
    cats: { world: 'Welt', player: 'Spieler', items: 'Items', entities: 'Mobs & Objekte', chat: 'Chat & Anzeige', effects: 'Sound & Effekte', logic: 'Logik & Daten', server: 'Server' },
    tiers: ['Jeder', 'Operator / Cheats', 'Server-Verwaltung'],
    permJava: (n) => (n === 0 ? 'Jeder' : `OP-Level ${n}`),
    permBedrock: { any: 'Jeder', gd: 'Operator', admin: 'Admin', host: 'Gastgeber', owner: 'Server-Besitzer' },
    ph: { int: 'Zahl', float: 'Zahl, z. B. 1.5', text: 'Text', target: 'Name oder @…', player: 'Spielername oder @…' },
    home: 'Übersicht', imprint: 'Impressum', privacy: 'Datenschutz',
    disclaimer: 'KEIN OFFIZIELLES MINECRAFT-PRODUKT. NICHT VON MOJANG ODER MICROSOFT GENEHMIGT ODER MIT MOJANG ODER MICROSOFT VERBUNDEN. Minecraft ist eine Marke von Mojang Synergies AB.',
    dataState: (j, b, d) => `Datenstand: Java ${j}, Bedrock ${b} (geprüft am ${d}).`,
    todo: 'bitte ergänzen',
    imprintBody: (s, todo) => `
      <h1>Impressum</h1>
      <h2>Angaben gemäß § 5 DDG</h2>
      <p>${s.owner}${s.careOf ? '<br>c/o ' + s.careOf : ''}<br>${s.street || todo('Straße und Hausnummer')}<br>${s.city || todo('PLZ und Ort')}<br>${s.country}</p>
      <h2>Kontakt</h2>
      <p>E-Mail: ${s.email || todo('E-Mail-Adresse')}</p>
      <h2>Inhaltlich verantwortlich</h2>
      <p>${s.owner}, Anschrift wie oben.</p>
      <h2>Hinweis zu Minecraft</h2>
      <p>Dies ist eine private Fan-Seite. Sie ist kein offizielles Minecraft-Produkt und steht in keiner Verbindung zu Mojang oder Microsoft. Minecraft ist eine Marke von Mojang Synergies AB.</p>
      <h2>Inhalte dieser Seite</h2>
      <p>Alle Texte, die Pixel-Grafiken und die Pixel-Schrift wurden für diese Seite selbst erstellt. Es werden keine Grafiken, Texturen, Schriften oder Texte aus dem Spiel oder von anderen Webseiten verwendet. Command-Namen und ihre Schreibweise sind Fakten über das Spiel.</p>
      <h2>Haftung für Inhalte</h2>
      <p>Die Angaben wurden sorgfältig zusammengestellt. Weil sich das Spiel mit jedem Update ändert, kann nicht garantiert werden, dass jeder Command in jeder Version genau so funktioniert. Benutzung auf eigene Verantwortung – am besten vorher eine Sicherung der Welt anlegen.</p>`,
    privacyBody: (s, todo) => `
      <h1>Datenschutz</h1>
      <h2>Kurz gesagt</h2>
      <p>Diese Seite verwendet keine Cookies, keine Werbung, keine Statistik-Werkzeuge und lädt nichts von fremden Servern. Auch die Schrift liegt direkt auf dieser Seite.</p>
      <h2>Verantwortlich</h2>
      <p>${s.owner}, ${s.street || todo('Straße und Hausnummer')}, ${s.city || todo('PLZ und Ort')}. E-Mail: ${s.email || todo('E-Mail-Adresse')}</p>
      <h2>Was beim Aufruf der Seite passiert</h2>
      <p>Die Seite liegt beim Hosting-Anbieter ${s.hoster}. Wie bei jedem Webserver werden beim Abruf technische Daten verarbeitet, zum Beispiel die IP-Adresse, Datum und Uhrzeit, die abgerufene Datei und der verwendete Browser. Das ist nötig, um die Seite auszuliefern und den Betrieb abzusichern (Art. 6 Abs. 1 lit. f DSGVO).</p>
      <h2>Einstellungen im Browser</h2>
      <p>Sprache, Tag-/Nacht-Modus, die zuletzt gewählte Edition und deine Favoriten werden nur in deinem eigenen Browser gespeichert (Local Storage). Diese Daten verlassen dein Gerät nicht. Du kannst sie jederzeit löschen, indem du die Websitedaten in deinem Browser entfernst.</p>
      <h2>Deine Rechte</h2>
      <p>Du hast das Recht auf Auskunft, Berichtigung, Löschung und Einschränkung der Verarbeitung deiner Daten sowie ein Beschwerderecht bei einer Datenschutz-Aufsichtsbehörde.</p>`,
  },

  en: {
    title: "Niklas' Command Book – Commands for Minecraft",
    tagline: 'Every console command for Java and Bedrock – look it up, click it together and copy it.',
    themeDark: 'Night', themeLight: 'Day',
    search: 'Search', searchPh: 'e.g. teleport, weather, items …',
    edition: 'Edition', all: 'All', both: 'Java + Bedrock',
    category: 'Category', allCats: 'All categories',
    permission: 'Permission', allPerms: 'All permissions',
    favOnly: '★ Favourites', sortBy: 'Sort by',
    count: (n, total) => `${n} of ${total} commands`,
    colName: 'Name', colDetails: 'Details', colSyntax: 'Syntax', colExample: 'Example', colSince: 'Since',
    noResults: 'No command matches these filters.', resetFilters: 'Reset filters',
    copy: 'Copy', copied: 'Copied!',
    favAdd: 'Add to favourites', favRemove: 'Remove favourite',
    more: (n) => `+${n} more`,
    back: '← Back to overview',
    aliases: 'Also', builder: 'Command builder', variant: 'Variant',
    builderHint: 'Pick the values – the finished command appears below.',
    yourCommand: 'Your command', missing: 'Some required values are still missing (in angle brackets).',
    noParams: 'In this form the command needs no further values.',
    optional: 'optional', choice: 'Choice', none: '– leave empty –',
    customTarget: 'Player name or custom selector …',
    targetHelp: 'Which targets can I use?',
    playerNameEx: 'Niklas', playerNameDesc: 'the name of a player who is online',
    playersOnly: 'This command only accepts players as targets.',
    filterTitle: 'Be more specific:', filterIntro: 'You can add filters in square brackets after a selector. Choose "Player name or custom selector" above to type one.',
    allForms: 'All forms', example: 'Example',
    onlyIn: (e) => `This command only exists in the ${e} Edition.`,
    cheats: 'Cheats required', yes: 'Yes', no: 'No', unknown: '–',
    notFound: 'I do not know this command.',
    loadError: 'The data could not be loaded. Please reload the page.',
    cats: { world: 'World', player: 'Player', items: 'Items', entities: 'Mobs & entities', chat: 'Chat & display', effects: 'Sound & effects', logic: 'Logic & data', server: 'Server' },
    tiers: ['Everyone', 'Operator / cheats', 'Server administration'],
    permJava: (n) => (n === 0 ? 'Everyone' : `OP level ${n}`),
    permBedrock: { any: 'Everyone', gd: 'Operator', admin: 'Admin', host: 'Host', owner: 'Server owner' },
    ph: { int: 'Number', float: 'Number, e.g. 1.5', text: 'Text', target: 'Name or @…', player: 'Player name or @…' },
    home: 'Overview', imprint: 'Legal notice', privacy: 'Privacy',
    disclaimer: 'NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT. Minecraft is a trademark of Mojang Synergies AB.',
    dataState: (j, b, d) => `Data as of: Java ${j}, Bedrock ${b} (checked on ${d}).`,
    todo: 'please add',
    imprintBody: (s, todo) => `
      <h1>Legal notice</h1>
      <h2>Information according to § 5 DDG (Germany)</h2>
      <p>${s.owner}${s.careOf ? '<br>c/o ' + s.careOf : ''}<br>${s.street || todo('street and number')}<br>${s.city || todo('postcode and town')}<br>${s.country === 'Deutschland' ? 'Germany' : s.country}</p>
      <h2>Contact</h2>
      <p>Email: ${s.email || todo('email address')}</p>
      <h2>Responsible for content</h2>
      <p>${s.owner}, address as above.</p>
      <h2>About Minecraft</h2>
      <p>This is a private fan site. It is not an official Minecraft product and is not associated with Mojang or Microsoft. Minecraft is a trademark of Mojang Synergies AB.</p>
      <h2>Content of this site</h2>
      <p>All texts, the pixel graphics and the pixel font were made for this site. No graphics, textures, fonts or texts from the game or from other websites are used. Command names and their syntax are facts about the game.</p>
      <h2>Liability for content</h2>
      <p>The information was compiled with care. Because the game changes with every update, there is no guarantee that every command works exactly like this in every version. Use at your own risk – ideally back up your world first.</p>`,
    privacyBody: (s, todo) => `
      <h1>Privacy</h1>
      <h2>In short</h2>
      <p>This site uses no cookies, no ads, no analytics and loads nothing from third-party servers. Even the font is served from this site.</p>
      <h2>Controller</h2>
      <p>${s.owner}, ${s.street || todo('street and number')}, ${s.city || todo('postcode and town')}. Email: ${s.email || todo('email address')}</p>
      <h2>What happens when you open the site</h2>
      <p>The site is hosted by ${s.hoster}. As with any web server, technical data is processed on each request, such as the IP address, date and time, the requested file and the browser used. This is necessary to deliver the site and keep it secure (Art. 6(1)(f) GDPR).</p>
      <h2>Settings in your browser</h2>
      <p>Language, day/night mode, the last chosen edition and your favourites are stored only in your own browser (local storage). This data never leaves your device. You can delete it at any time by clearing the site data in your browser.</p>
      <h2>Your rights</h2>
      <p>You have the right to access, rectification, erasure and restriction of processing of your data, and the right to lodge a complaint with a data protection authority.</p>`,
  },
};
