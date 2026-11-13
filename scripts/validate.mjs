#!/usr/bin/env node
// Prüft die Daten in site/data. Läuft ohne Abhängigkeiten:  node scripts/validate.mjs
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { parseForm, BASIC_TYPES } from '../site/js/syntax.js';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', 'site', 'data');
const read = (p) => JSON.parse(readFileSync(join(root, p), 'utf8'));

const CATS = ['world', 'player', 'items', 'entities', 'chat', 'effects', 'logic', 'server'];
const BEDROCK_PERMS = ['any', 'gd', 'admin', 'host', 'owner'];
const errors = [];
const err = (id, msg) => errors.push(`${id}: ${msg}`);

const site = read('site.json');
const lists = read('lists.json');
const ids = new Set();
let count = 0, java = 0, bedrock = 0;

for (const [name, l] of Object.entries(lists)) {
  if (name.startsWith('_')) continue;
  const groups = Array.isArray(l) ? [l] : ['values', 'java', 'bedrock'].filter((k) => l[k]).map((k) => l[k]);
  if (!groups.length) err('lists.' + name, 'keine Werte');
  for (const g of groups) {
    if (new Set(g).size !== g.length) err('lists.' + name, 'doppelte Einträge');
  }
}

for (const file of site.commandFiles) {
  for (const c of read(`commands/${file}.json`)) {
    count++;
    const id = c.id || '(ohne id)';
    if (!c.id) err(file, 'Eintrag ohne id');
    if (ids.has(c.id)) err(id, 'id doppelt vergeben');
    ids.add(c.id);
    if (!CATS.includes(c.cat)) err(id, `unbekannte Kategorie "${c.cat}"`);
    if (!c.java && !c.bedrock) err(id, 'weder java noch bedrock');
    for (const lang of ['de', 'en']) {
      if (!c[lang]?.short || !c[lang]?.details) err(id, `Text fehlt (${lang})`);
    }
    for (const e of ['java', 'bedrock']) {
      const ed = c[e];
      if (!ed) continue;
      e === 'java' ? java++ : bedrock++;
      if (e === 'java' && !(Number.isInteger(ed.perm) && ed.perm >= 0 && ed.perm <= 4)) err(id, 'java.perm muss 0–4 sein');
      if (e === 'bedrock' && !BEDROCK_PERMS.includes(ed.perm)) err(id, 'bedrock.perm unbekannt');
      if (!Array.isArray(ed.forms) || !ed.forms.length) { err(id, `${e}.forms fehlt`); continue; }
      const names = [ed.name || c.id, ...(ed.alias || [])];
      if (!ed.ex || !names.some((n) => ed.ex === '/' + n || ed.ex.startsWith('/' + n + ' '))) err(id, `${e}.ex passt nicht zum Namen`);
      for (const form of ed.forms) {
        try {
          let optionalSeen = false;
          for (const tk of parseForm(form)) {
            if (tk.kind !== 'param') { if (optionalSeen) err(id, `${e}: fester Text nach optionalem Parameter in "${form}"`); continue; }
            if (!tk.req) optionalSeen = true;
            else if (optionalSeen) err(id, `${e}: Pflichtparameter nach optionalem in "${form}"`);
            if (tk.type !== 'enum' && !BASIC_TYPES.includes(tk.type) && !['item', 'block'].includes(tk.type)) {
              const l = lists[tk.type];
              if (!l) err(id, `${e}: Liste "${tk.type}" fehlt in lists.json`);
              else if (!Array.isArray(l) && !l.values && !l[e]) err(id, `${e}: Liste "${tk.type}" hat keine Werte für ${e}`);
            }
          }
        } catch (ex) {
          err(id, `${e}: ${ex.message}`);
        }
      }
    }
  }
}

const catalog = read('catalog.json');
const seen = { i: new Set(), b: new Set() };
for (const en of catalog.entries) {
  const [cid, de, enName, cat, kind = 'i'] = en;
  if (!/^[a-z0-9_]+$/.test(cid || '') || !de || !enName) err('catalog.' + cid, 'unvollständig');
  if (!catalog.categories[cat]) err('catalog.' + cid, `unbekannte Kategorie "${cat}"`);
  if (!['i', 'b', 'ib'].includes(kind)) err('catalog.' + cid, 'Art muss i, b oder ib sein');
  for (const k of kind) { if (seen[k]?.has(cid)) err('catalog.' + cid, 'doppelt'); seen[k]?.add(cid); }
}

const sel = read('selectors.json');
for (const x of sel.selectors) {
  if (!/^@[a-z]$/.test(x.id) || !x.de || !x.en || !x.editions?.length || typeof x.player !== 'boolean') err('selectors.' + x.id, 'unvollständig');
}
for (const e of ['java', 'bedrock']) {
  for (const f of sel.filters[e] || []) if (!f.ex || !f.de || !f.en) err('selectors.filters.' + e, 'Eintrag unvollständig');
  if (!sel.selectors.some((x) => x.editions.includes(e) && x.player)) err('selectors', 'kein Spieler-Selektor für ' + e);
}

if (errors.length) {
  console.error(`${errors.length} Fehler:\n- ` + errors.join('\n- '));
  process.exit(1);
}
console.log(`OK: ${count} Commands (${java} Java, ${bedrock} Bedrock), ${Object.keys(lists).length - 1} Listen.`);
