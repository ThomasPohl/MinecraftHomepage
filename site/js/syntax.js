// Mini-Sprache für Command-Formen (siehe CLAUDE.md, Abschnitt "Formen").
//
//   wort                 fester Text
//   (a|b|c)              Pflicht-Auswahl aus festen Wörtern
//   <name:typ>           Pflicht-Parameter
//   [name:typ]           optionaler Parameter
//   <name:typ=wert>      Parameter mit Vorgabewert
//
// typ ist: int, float, bool, text, pos, pos2, rot, target, player,
//          eine Inline-Auswahl "a|b|c" oder der Name einer Liste aus data/lists.json.

export const BASIC_TYPES = ['int', 'float', 'bool', 'text', 'pos', 'pos2', 'rot', 'target', 'player'];

export function parseForm(form) {
  const str = (form || '').trim();
  if (!str) return [];
  return str.split(/\s+/).map((tok) => {
    let m = tok.match(/^([<\[])([^:<>\[\]=]+)(?::([^=<>\[\]]+))?(?:=([^<>\[\]]*))?([>\]])$/);
    if (m) {
      const req = m[1] === '<';
      if ((req && m[5] !== '>') || (!req && m[5] !== ']')) throw new Error('Klammer passt nicht: ' + tok);
      const type = m[3] || 'text';
      const options = type.includes('|') ? type.split('|') : null;
      return { kind: 'param', req, name: m[2], type: options ? 'enum' : type, options, def: m[4] };
    }
    m = tok.match(/^\((.+)\)$/);
    if (m) return { kind: 'param', req: true, name: '', type: 'enum', options: m[1].split('|'), choice: true };
    if (/[<>\[\]()]/.test(tok)) throw new Error('Unlesbares Token: ' + tok);
    return { kind: 'lit', text: tok };
  });
}

export function tokenLabel(tk) {
  if (tk.kind === 'lit') return tk.text;
  if (tk.choice) return '(' + tk.options.join('|') + ')';
  return tk.req ? '<' + tk.name + '>' : '[' + tk.name + ']';
}

export function formSyntax(name, form) {
  return ['/' + name, ...parseForm(form).map(tokenLabel)].join(' ');
}

// Baut den fertigen Command. values[i] ist der eingegebene Wert zu Token i (oder '').
export function assemble(name, tokens, values) {
  let last = -1;
  tokens.forEach((tk, i) => { if (tk.kind === 'param' && !tk.req && values[i]) last = i; });
  const parts = ['/' + name];
  let missing = false;
  for (let i = 0; i < tokens.length; i++) {
    const tk = tokens[i];
    if (tk.kind === 'lit') { parts.push(tk.text); continue; }
    const v = values[i];
    if (tk.req) {
      if (v) parts.push(v); else { parts.push('<' + (tk.name || 'auswahl') + '>'); missing = true; }
    } else {
      if (i > last) break;                 // ab hier nur noch leere optionale Angaben
      if (v) parts.push(v);
      else if (tk.def) parts.push(tk.def);
      else { parts.push('<' + tk.name + '>'); missing = true; }
    }
  }
  return { text: parts.join(' '), missing };
}

export function compareVersions(a, b) {
  const pa = String(a).split('.').map(Number), pb = String(b).split('.').map(Number);
  for (let i = 0; i < Math.max(pa.length, pb.length); i++) {
    const d = (pa[i] || 0) - (pb[i] || 0);
    if (d) return d;
  }
  return 0;
}
