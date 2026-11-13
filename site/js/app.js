// Niklas' Befehlsbuch – App-Logik (ohne Build-Schritt, ohne Abhängigkeiten).
import { T } from './i18n.js';
import { parseForm, formSyntax, assemble, compareVersions } from './syntax.js';

const LS_KEY = 'befehlsbuch.v1';
const EDITIONS = ['java', 'bedrock'];
const ED_LABEL = { java: 'Java', bedrock: 'Bedrock' };
const CATS = ['world', 'player', 'items', 'entities', 'chat', 'effects', 'logic', 'server'];

// ---------- Einstellungen (bleiben im Browser gespeichert) ----------
const prefs = Object.assign(
  { lang: (navigator.language || 'de').toLowerCase().startsWith('de') ? 'de' : 'en', theme: null, edition: 'java', filterEdition: 'all', favs: [] },
  readPrefs()
);
function readPrefs() {
  try { return JSON.parse(localStorage.getItem(LS_KEY) || '{}') || {}; } catch { return {}; }
}
function savePrefs() {
  try { localStorage.setItem(LS_KEY, JSON.stringify(prefs)); } catch { /* privater Modus: dann eben ohne Merken */ }
}

const view = { q: '', cat: 'all', perm: 'all', favOnly: false, sort: { key: 'name', dir: 1 } };
let data = { commands: [], lists: {}, site: {} };
const app = document.getElementById('app');
const t = (key) => T[prefs.lang][key];

// ---------- Hilfen ----------
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const editionsOf = (c) => EDITIONS.filter((e) => c[e]);
const nameOf = (c, e) => (c[e] && c[e].name) || c.id;
const hasFav = (id) => prefs.favs.includes(id);

function shownEdition(c) {
  if (prefs.filterEdition !== 'all' && c[prefs.filterEdition]) return prefs.filterEdition;
  if (c[prefs.edition]) return prefs.edition;
  return editionsOf(c)[0];
}
function permTier(c, e) {
  const p = c[e].perm;
  if (e === 'java') return p === 0 ? 0 : p <= 2 ? 1 : 2;
  return p === 'any' ? 0 : p === 'gd' ? 1 : 2;
}
function permRank(c, e) {
  const p = c[e].perm;
  return e === 'java' ? p : { any: 0, gd: 2, admin: 3, host: 3.5, owner: 4 }[p];
}
function permLabel(c, e) {
  return e === 'java' ? t('permJava')(c[e].perm) : t('permBedrock')[c[e].perm];
}
function needsCheats(c, e) {
  return e === 'java' ? c[e].perm > 0 : c[e].cheats !== false;
}
function listFor(type, edition) {
  const l = data.lists[type];
  if (!l) return null;
  if (Array.isArray(l)) return { values: l, free: false };
  return { values: l[edition] || l.values || [], free: !!l.free };
}

async function copyText(text, btn) {
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); } catch { /* nichts zu tun */ }
    ta.remove();
  }
  if (btn) {
    const old = btn.textContent;
    btn.textContent = t('copied');
    setTimeout(() => { btn.textContent = old; }, 1400);
  }
}

// ---------- Rahmen (Kopf, Fuss, Sprache, Theme) ----------
function currentTheme() {
  return prefs.theme || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
}
function applyChrome() {
  const theme = currentTheme();
  document.documentElement.dataset.theme = theme;
  document.documentElement.lang = prefs.lang;
  document.querySelector('.brand-text').textContent = prefs.lang === 'de' ? "Niklas' Befehlsbuch" : "Niklas' Command Book";
  document.getElementById('tagline').textContent = t('tagline');
  const tt = document.getElementById('theme-toggle');
  tt.textContent = theme === 'dark' ? '☀ ' + t('themeLight') : '☾ ' + t('themeDark');
  document.querySelectorAll('[data-lang]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.lang === prefs.lang)));
  document.getElementById('foot-home').textContent = t('home');
  document.getElementById('foot-imprint').textContent = t('imprint');
  document.getElementById('foot-privacy').textContent = t('privacy');
  const dv = data.site.dataVersion;
  document.getElementById('disclaimer').textContent = t('disclaimer') + (dv ? ' ' + t('dataState')(dv.java, dv.bedrock, dv.checked) : '');
}

document.addEventListener('click', (ev) => {
  const lang = ev.target.closest('[data-lang]');
  if (lang) { prefs.lang = lang.dataset.lang; savePrefs(); applyChrome(); route(); return; }
  if (ev.target.closest('#theme-toggle')) {
    prefs.theme = currentTheme() === 'dark' ? 'light' : 'dark';
    savePrefs(); applyChrome();
  }
});

// ---------- Übersicht ----------
function matches(c) {
  const fe = prefs.filterEdition;
  if (fe !== 'all' && !c[fe]) return false;
  if (view.cat !== 'all' && c.cat !== view.cat) return false;
  if (view.favOnly && !hasFav(c.id)) return false;
  const e = shownEdition(c);
  if (view.perm !== 'all' && permTier(c, e) !== Number(view.perm)) return false;
  const q = view.q.trim().toLowerCase().replace(/^\//, '');
  if (!q) return true;
  const hay = [c.id, ...editionsOf(c).flatMap((x) => [nameOf(c, x), ...(c[x].alias || [])]),
    c.de.short, c.de.details, c.en.short, c.en.details, t('cats')[c.cat]].join(' ').toLowerCase();
  return q.split(/\s+/).every((w) => hay.includes(w));
}

function sortValue(c, key) {
  const e = shownEdition(c);
  switch (key) {
    case 'edition': return editionsOf(c).length === 2 ? 1 : c.java ? 0 : 2;
    case 'cat': return t('cats')[c.cat];
    case 'perm': return permRank(c, e);
    case 'since': return c[e].since || null;
    default: return nameOf(c, e);
  }
}
function sorted(list) {
  const { key, dir } = view.sort;
  return [...list].sort((a, b) => {
    const va = sortValue(a, key), vb = sortValue(b, key);
    let d;
    if (key === 'since') {
      if (va === null || vb === null) d = va === vb ? 0 : va === null ? 1 : -1;   // ohne Angabe immer ans Ende
      else d = compareVersions(va, vb) * dir;
    } else if (typeof va === 'number') d = (va - vb) * dir;
    else d = String(va).localeCompare(String(vb), prefs.lang) * dir;
    return d || nameOf(a, shownEdition(a)).localeCompare(nameOf(b, shownEdition(b)));
  });
}

const SORT_COLS = [['edition', 'edition'], ['name', 'colName'], ['cat', 'category'], ['perm', 'permission'], ['since', 'colSince']];

function renderList() {
  document.title = t('title');
  const th = (key, label, cls) => `<th scope="col" class="${cls}" data-sort="${key}"><button type="button">${esc(t(label))}<span class="arrow" aria-hidden="true">↕</span></button></th>`;
  app.innerHTML = `
    <section class="panel">
      <div class="controls">
        <div class="c-search"><label for="q">${esc(t('search'))}</label>
          <input type="search" id="q" placeholder="${esc(t('searchPh'))}" value="${esc(view.q)}" autocomplete="off"></div>
        <div class="c-edition"><label id="lbl-ed">${esc(t('edition'))}</label>
          <div class="seg" role="group" aria-labelledby="lbl-ed">
            ${['all', 'java', 'bedrock'].map((e) => `<button type="button" class="btn" data-fed="${e}" aria-pressed="${prefs.filterEdition === e}">${e === 'all' ? esc(t('all')) : ED_LABEL[e]}</button>`).join('')}
          </div></div>
        <div><label for="f-cat">${esc(t('category'))}</label>
          <select id="f-cat"><option value="all">${esc(t('allCats'))}</option>
            ${CATS.map((c) => `<option value="${c}" ${view.cat === c ? 'selected' : ''}>${esc(t('cats')[c])}</option>`).join('')}</select></div>
        <div><label for="f-perm">${esc(t('permission'))}</label>
          <select id="f-perm"><option value="all">${esc(t('allPerms'))}</option>
            ${t('tiers').map((l, i) => `<option value="${i}" ${view.perm === String(i) ? 'selected' : ''}>${esc(l)}</option>`).join('')}</select></div>
        <div><button type="button" class="btn" id="f-fav" aria-pressed="${view.favOnly}">${esc(t('favOnly'))}</button></div>
        <div class="mobile-sort"><label for="f-sort">${esc(t('sortBy'))}</label>
          <select id="f-sort">${SORT_COLS.map(([k, l]) => `<option value="${k}" ${view.sort.key === k ? 'selected' : ''}>${esc(t(l))}</option>`).join('')}</select></div>
      </div>
      <p class="count" id="count" aria-live="polite"></p>
    </section>
    <section class="panel table-wrap">
      <table class="cmds">
        <thead><tr>
          <th scope="col" class="c-fav"><span aria-hidden="true">★</span></th>
          ${th('edition', 'edition', 'c-ed')}${th('name', 'colName', 'c-name')}${th('cat', 'category', 'c-cat')}
          <th scope="col" class="c-desc">${esc(t('colDetails'))}</th>
          <th scope="col" class="c-syntax">${esc(t('colSyntax'))}</th>
          <th scope="col" class="c-ex">${esc(t('colExample'))}</th>
          ${th('perm', 'permission', 'c-perm')}${th('since', 'colSince', 'c-since')}
        </tr></thead>
        <tbody id="rows"></tbody>
      </table>
      <div id="empty" class="empty" hidden><p>${esc(t('noResults'))}</p><button type="button" class="btn" id="reset">${esc(t('resetFilters'))}</button></div>
    </section>`;
  updateRows();
}

function rowHtml(c) {
  const e = shownEdition(c), ed = c[e], name = nameOf(c, e);
  const forms = ed.forms || [''];
  const fav = hasFav(c.id);
  const alias = (ed.alias || []).map((a) => '/' + a).join(', ');
  return `<tr data-id="${esc(c.id)}">
    <td class="c-fav"><button type="button" class="star" data-fav="${esc(c.id)}" aria-pressed="${fav}" aria-label="${esc(fav ? t('favRemove') : t('favAdd'))}">${fav ? '★' : '☆'}</button></td>
    <td class="c-ed">${editionsOf(c).map((x) => `<span class="badge ${x}">${ED_LABEL[x]}</span>`).join('')}</td>
    <td class="c-name"><a href="#/c/${encodeURIComponent(c.id)}">/${esc(name)}</a>${alias ? `<span class="alias">${esc(alias)}</span>` : ''}</td>
    <td class="c-cat" data-label="${esc(t('category'))}">${esc(t('cats')[c.cat])}</td>
    <td class="c-desc">${esc(c[prefs.lang].short)}</td>
    <td class="c-syntax" data-label="${esc(t('colSyntax'))}">${esc(formSyntax(name, forms[0]))}${forms.length > 1 ? ` <span class="more">${esc(t('more')(forms.length - 1))}</span>` : ''}</td>
    <td class="c-ex" data-label="${esc(t('colExample'))}">${esc(ed.ex)}<button type="button" class="copy" data-copy="${esc(ed.ex)}">${esc(t('copy'))}</button></td>
    <td class="c-perm" data-label="${esc(t('permission'))}">${esc(permLabel(c, e))}</td>
    <td class="c-since ${ed.since ? '' : 'none'}" data-label="${esc(t('colSince'))}">${ed.since ? esc(ED_LABEL[e] + ' ' + ed.since) : '–'}</td>
  </tr>`;
}

function updateRows() {
  const rows = document.getElementById('rows');
  if (!rows) return;
  const list = sorted(data.commands.filter(matches));
  rows.innerHTML = list.map(rowHtml).join('');
  document.getElementById('count').textContent = t('count')(list.length, data.commands.length);
  document.getElementById('empty').hidden = list.length > 0;
  document.querySelector('table.cmds').hidden = list.length === 0;
  document.querySelectorAll('th[data-sort]').forEach((thEl) => {
    const active = thEl.dataset.sort === view.sort.key;
    if (active) thEl.setAttribute('aria-sort', view.sort.dir === 1 ? 'ascending' : 'descending');
    else thEl.removeAttribute('aria-sort');
    thEl.querySelector('.arrow').textContent = active ? (view.sort.dir === 1 ? '▲' : '▼') : '↕';
  });
  document.querySelectorAll('[data-fed]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.fed === prefs.filterEdition)));
}

app.addEventListener('input', (ev) => {
  if (ev.target.id === 'q') { view.q = ev.target.value; updateRows(); }
});
app.addEventListener('change', (ev) => {
  const id = ev.target.id;
  if (id === 'f-cat') { view.cat = ev.target.value; updateRows(); }
  else if (id === 'f-perm') { view.perm = ev.target.value; updateRows(); }
  else if (id === 'f-sort') { view.sort = { key: ev.target.value, dir: 1 }; updateRows(); }
});
app.addEventListener('click', (ev) => {
  const el = ev.target;
  const copy = el.closest('[data-copy]');
  if (copy) { copyText(copy.dataset.copy, copy); return; }
  const fav = el.closest('[data-fav]');
  if (fav) {
    const id = fav.dataset.fav;
    prefs.favs = hasFav(id) ? prefs.favs.filter((x) => x !== id) : [...prefs.favs, id];
    savePrefs();
    if (document.getElementById('rows')) updateRows();
    else {
      const on = hasFav(id);
      fav.setAttribute('aria-pressed', String(on));
      fav.setAttribute('aria-label', on ? t('favRemove') : t('favAdd'));
      fav.textContent = on ? '★' : '☆';
    }
    return;
  }
  const fed = el.closest('[data-fed]');
  if (fed) {
    prefs.filterEdition = fed.dataset.fed;
    if (fed.dataset.fed !== 'all') prefs.edition = fed.dataset.fed;   // letzte Auswahl merken
    savePrefs(); updateRows(); return;
  }
  if (el.closest('#f-fav')) {
    view.favOnly = !view.favOnly;
    el.closest('#f-fav').setAttribute('aria-pressed', String(view.favOnly));
    updateRows(); return;
  }
  if (el.closest('#reset')) {
    Object.assign(view, { q: '', cat: 'all', perm: 'all', favOnly: false });
    prefs.filterEdition = 'all'; savePrefs(); renderList(); return;
  }
  const sortTh = el.closest('th[data-sort]');
  if (sortTh) {
    const key = sortTh.dataset.sort;
    view.sort = { key, dir: view.sort.key === key ? -view.sort.dir : 1 };
    updateRows(); return;
  }
  const sw = el.closest('[data-edition]');
  if (sw) { prefs.edition = sw.dataset.edition; savePrefs(); route(); return; }
  const row = el.closest('tr[data-id]');
  if (row && !el.closest('a, button')) location.hash = '#/c/' + encodeURIComponent(row.dataset.id);
});

// ---------- Detailseite mit Command-Builder ----------
let builder = null;   // { name, edition, forms, index, tokens }

function renderDetail(id) {
  const c = data.commands.find((x) => x.id === id);
  if (!c) {
    app.innerHTML = `<a class="back" href="#/">${esc(t('back'))}</a><section class="panel"><p>${esc(t('notFound'))}</p></section>`;
    return;
  }
  const eds = editionsOf(c);
  const e = c[prefs.edition] ? prefs.edition : eds[0];
  const ed = c[e], name = nameOf(c, e), L = c[prefs.lang];
  const fav = hasFav(c.id);
  const alias = (ed.alias || []).map((a) => '/' + a).join(', ');
  document.title = `/${name} – ${t('title')}`;
  const forms = ed.forms || [''];
  builder = { name, edition: e, forms, index: 0, tokens: [] };

  app.innerHTML = `
    <a class="back" href="#/">${esc(t('back'))}</a>
    <section class="panel">
      <div class="detail-head">
        <div>
          <div>${eds.map((x) => `<span class="badge ${x}">${ED_LABEL[x]}</span>`).join('')}</div>
          <h1>/${esc(name)}</h1>
          ${alias ? `<p class="muted mono">${esc(t('aliases'))}: ${esc(alias)}</p>` : ''}
        </div>
        <button type="button" class="star" data-fav="${esc(c.id)}" aria-pressed="${fav}" aria-label="${esc(fav ? t('favRemove') : t('favAdd'))}">${fav ? '★' : '☆'}</button>
      </div>
      <p class="lead">${esc(L.short)}</p>
      <p class="prose">${esc(L.details)}</p>
      <div class="edition-switch">
        ${eds.length === 2
          ? `<span id="lbl-sw"><strong>${esc(t('edition'))}:</strong></span><div class="seg" role="group" aria-labelledby="lbl-sw">${eds.map((x) => `<button type="button" class="btn" data-edition="${x}" aria-pressed="${x === e}">${ED_LABEL[x]}</button>`).join('')}</div>`
          : `<span class="muted">${esc(t('onlyIn')(ED_LABEL[e]))}</span>`}
      </div>
      <dl class="facts">
        <div><dt>${esc(t('category'))}</dt><dd>${esc(t('cats')[c.cat])}</dd></div>
        <div><dt>${esc(t('permission'))}</dt><dd>${esc(permLabel(c, e))}</dd></div>
        <div><dt>${esc(t('cheats'))}</dt><dd>${esc(needsCheats(c, e) ? t('yes') : t('no'))}</dd></div>
        <div><dt>${esc(t('colSince'))}</dt><dd>${ed.since ? esc(ED_LABEL[e] + ' ' + ed.since) : esc(t('unknown'))}</dd></div>
      </dl>
    </section>

    <section class="panel">
      <h2>${esc(t('builder'))}</h2>
      <p class="hint">${esc(t('builderHint'))}</p>
      ${forms.length > 1 ? `<div class="field wide" style="margin-top:12px"><label for="b-form">${esc(t('variant'))}</label>
        <select id="b-form">${forms.map((f, i) => `<option value="${i}">${esc(formSyntax(name, f))}</option>`).join('')}</select></div>` : ''}
      <div id="b-fields" class="fields"></div>
      <h3 style="margin-top:18px">${esc(t('yourCommand'))}</h3>
      <div class="output"><code id="b-out" aria-live="polite"></code><button type="button" class="btn primary" id="b-copy">${esc(t('copy'))}</button></div>
      <p class="warn" id="b-warn" hidden>${esc(t('missing'))}</p>
    </section>

    <section class="panel">
      <h2>${esc(t('example'))}</h2>
      <div class="output"><code>${esc(ed.ex)}</code><button type="button" class="btn" data-copy="${esc(ed.ex)}">${esc(t('copy'))}</button></div>
      <h2 style="margin-top:22px">${esc(t('allForms'))}</h2>
      <ul class="syntax">${forms.map((f) => `<li>${esc(formSyntax(name, f))}</li>`).join('')}</ul>
    </section>`;

  renderFields();
  const formSel = document.getElementById('b-form');
  if (formSel) formSel.addEventListener('change', () => { builder.index = Number(formSel.value); renderFields(); });
  document.getElementById('b-fields').addEventListener('input', updateOutput);
  document.getElementById('b-fields').addEventListener('change', updateOutput);
  document.getElementById('b-copy').addEventListener('click', (ev) => copyText(document.getElementById('b-out').textContent, ev.currentTarget));
}

function fieldHtml(tk, i) {
  const id = 'p' + i;
  const label = tk.choice ? t('choice') : tk.name;
  const opt = tk.req ? '' : ` <span class="opt">(${esc(t('optional'))})</span>`;
  const head = `<label for="${id}">${esc(label)}${opt}</label>`;
  const emptyOpt = tk.req ? '' : `<option value="">${esc(t('none'))}</option>`;
  const select = (values) => `<select id="${id}" data-i="${i}">${emptyOpt}${values.map((v) => `<option ${tk.def === v ? 'selected' : ''}>${esc(v)}</option>`).join('')}</select>`;
  const text = (ph, value = '', extra = '') => `<input type="text" id="${id}" data-i="${i}" placeholder="${esc(ph)}" value="${esc(value)}" autocomplete="off" autocapitalize="off" spellcheck="false" ${extra}>`;
  const multi = (labels, fill) => `<div class="multi">${labels.map((l, n) =>
    `<input type="text" ${n === 0 ? `id="${id}"` : ''} data-i="${i}" data-part="${n}" aria-label="${esc(tk.name + ' ' + l)}" placeholder="${l}" value="${tk.req ? fill : ''}" autocomplete="off" autocapitalize="off" spellcheck="false">`).join('')}</div>`;

  let body;
  switch (tk.type) {
    case 'enum': body = select(tk.options); break;
    case 'bool': body = select(['true', 'false']); break;
    case 'int': body = text(t('ph').int, tk.def || '', 'inputmode="numeric"'); break;
    case 'float': body = text(t('ph').float, tk.def || '', 'inputmode="decimal"'); break;
    case 'pos': body = multi(['x', 'y', 'z'], '~'); break;
    case 'pos2': body = multi(['x', 'z'], '~'); break;
    case 'rot': body = multi(['yaw', 'pitch'], '0'); break;
    case 'target':
    case 'player':
      body = text(t('ph')[tk.type], tk.req ? (tk.def || '@s') : '', `list="dl-selector"`); break;
    case 'text': body = text(t('ph').text, tk.def || ''); break;
    default: {
      const l = listFor(tk.type, builder.edition);
      if (!l) body = text(t('ph').text, tk.def || '');
      else if (!l.free && l.values.length <= 15) body = select(l.values);
      else body = text(l.values[0] || '', tk.def || '', `list="dl-${esc(tk.type)}"`);
    }
  }
  const wide = tk.type === 'text' && /command|message|json|nbt|text/i.test(tk.name) ? ' wide' : '';
  return `<div class="field${wide}">${head}${body}</div>`;
}

function renderFields() {
  const box = document.getElementById('b-fields');
  builder.tokens = parseForm(builder.forms[builder.index]);
  const params = builder.tokens.map((tk, i) => [tk, i]).filter(([tk]) => tk.kind === 'param');
  const lists = new Set(['selector']);
  params.forEach(([tk]) => { if (listFor(tk.type, builder.edition)) lists.add(tk.type); });
  const datalists = [...lists].map((name) => {
    const l = listFor(name, builder.edition);
    return l ? `<datalist id="dl-${esc(name)}">${l.values.map((v) => `<option value="${esc(v)}"></option>`).join('')}</datalist>` : '';
  }).join('');
  box.innerHTML = (params.length ? params.map(([tk, i]) => fieldHtml(tk, i)).join('') : `<p class="muted">${esc(t('noParams'))}</p>`) + datalists;
  updateOutput();
}

function updateOutput() {
  const box = document.getElementById('b-fields');
  const values = builder.tokens.map(() => '');
  const parts = {};
  box.querySelectorAll('[data-i]').forEach((el) => {
    const i = Number(el.dataset.i), v = el.value.trim();
    if (el.dataset.part === undefined) values[i] = v;
    else (parts[i] = parts[i] || [])[Number(el.dataset.part)] = v;
  });
  Object.entries(parts).forEach(([i, arr]) => {
    const fill = builder.tokens[i].type === 'rot' ? '0' : '~';
    values[i] = arr.some(Boolean) ? arr.map((v) => v || fill).join(' ') : '';
  });
  const out = assemble(builder.name, builder.tokens, values);
  document.getElementById('b-out').textContent = out.text;
  document.getElementById('b-warn').hidden = !out.missing;
}

// ---------- Impressum / Datenschutz ----------
function renderStatic(which) {
  const todo = (what) => `<span class="todo">[${esc(t('todo'))}: ${esc(what)}]</span>`;
  const s = Object.fromEntries(Object.entries(data.site).map(([k, v]) => [k, typeof v === 'string' ? esc(v) : v]));
  document.title = `${t(which === 'imprint' ? 'imprint' : 'privacy')} – ${t('title')}`;
  app.innerHTML = `<a class="back" href="#/">${esc(t('back'))}</a>
    <section class="panel prose">${t(which === 'imprint' ? 'imprintBody' : 'privacyBody')(s, todo)}</section>`;
}

// ---------- Router ----------
function route() {
  const hash = location.hash.replace(/^#\/?/, '');
  if (hash.startsWith('c/')) renderDetail(decodeURIComponent(hash.slice(2)));
  else if (hash === 'impressum') renderStatic('imprint');
  else if (hash === 'datenschutz') renderStatic('privacy');
  else renderList();
}
window.addEventListener('hashchange', () => { route(); window.scrollTo(0, 0); app.focus({ preventScroll: true }); });

// ---------- Start ----------
async function load(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(path + ': ' + res.status);
  return res.json();
}
(async function start() {
  try {
    const [site, lists] = await Promise.all([load('data/site.json'), load('data/lists.json')]);
    const files = await Promise.all(site.commandFiles.map((f) => load(`data/commands/${f}.json`)));
    data = { site, lists, commands: files.flat() };
    prefs.favs = prefs.favs.filter((id) => data.commands.some((c) => c.id === id));
    applyChrome();
    route();
  } catch (err) {
    console.error(err);
    applyChrome();
    app.innerHTML = `<section class="panel"><p>${esc(t('loadError'))}</p></section>`;
  }
})();
