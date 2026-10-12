/* cmdquiz engine: answer checking, permission drills and progress weighting.
 * A line-for-line port of the logic in cmdquiz.py, so the web and terminal
 * versions grade answers identically. No DOM code here (it also runs in Node
 * for the tests).
 */
(function (root) {
  "use strict";

  // ------------------------------------------------------------------ shell-style splitting (Python shlex.split, posix)
  function shlexSplit(s) {
    const out = [];
    let cur = "", inTok = false, i = 0;
    while (i < s.length) {
      const ch = s[i];
      if (ch === "'") {
        const j = s.indexOf("'", i + 1);
        if (j < 0) throw new Error("No closing quotation");
        cur += s.slice(i + 1, j); inTok = true; i = j + 1;
      } else if (ch === '"') {
        inTok = true; i++;
        for (;;) {
          if (i >= s.length) throw new Error("No closing quotation");
          const c = s[i];
          if (c === '"') { i++; break; }
          if (c === "\\" && i + 1 < s.length && (s[i + 1] === '"' || s[i + 1] === "\\")) { cur += s[i + 1]; i += 2; continue; }
          cur += c; i++;
        }
      } else if (ch === "\\") {
        if (i + 1 >= s.length) throw new Error("No escaped character");
        cur += s[i + 1]; inTok = true; i += 2;
      } else if (" \t\r\n".includes(ch)) {
        if (inTok) { out.push(cur); cur = ""; inTok = false; }
        i++;
      } else {
        cur += ch; inTok = true; i++;
      }
    }
    if (inTok) out.push(cur);
    return out;
  }

  function splitTokens(text) {
    try { return shlexSplit(text.trim()); }
    catch (e) { return text.split(/\s+/).filter(Boolean); }
  }

  // ------------------------------------------------------------------ answer checking
  const CLUSTER = /^-[A-Za-z]{2,}$/;

  function rawTokens(text) {
    const toks = splitTokens(text);
    while (toks.length && toks[0] === "sudo") toks.shift();
    return toks;
  }

  /** Tokenise like a shell, drop sudo, ignore quote style, sort letters in -la style groups. */
  function canon(text) {
    return rawTokens(text).map(t => CLUSTER.test(t) ? "-" + t.slice(1).split("").sort().join("") : t);
  }

  const sameList = (a, b) => a.length === b.length && a.every((v, i) => v === b[i]);
  const looseKey = text => text.toLowerCase().replace(/[^a-z0-9]/g, "");

  function checkTyped(given, accepted) {
    const g = canon(given);
    return g.length > 0 && accepted.some(a => sameList(g, canon(a)));
  }

  function checkLoose(given, accepted) {
    const g = looseKey(given);
    return g.length > 0 && accepted.some(a => g === looseKey(a));
  }

  function checkDrill(given, accepted) {
    const g = given.toLowerCase().replace(/ /g, "");
    return accepted.some(a => a.toLowerCase().replace(/ /g, "") === g);
  }

  function checkAnswer(q, given) {
    if (q.loose) return checkLoose(given, q.answers);
    if (q.typed === false) return checkDrill(given, q.answers);
    return checkTyped(given, q.answers);
  }

  /** Re-quote a token for display the way you'd type it: ll='ls -la', '{print $1}'. */
  function showTok(t) {
    if (!/[\s{}]/.test(t)) return t;
    const eq = t.indexOf("=");
    if (eq >= 0 && /^[A-Za-z_][A-Za-z0-9_]*$/.test(t.slice(0, eq))) return `${t.slice(0, eq)}='${t.slice(eq + 1)}'`;
    return `'${t}'`;
  }

  // Token diff (longest common subsequence), grouped into equal / changed runs like difflib opcodes.
  function lcsTable(a, b) {
    const n = a.length, m = b.length;
    const L = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));
    for (let i = n - 1; i >= 0; i--)
      for (let j = m - 1; j >= 0; j--)
        L[i][j] = a[i] === b[j] ? L[i + 1][j + 1] + 1 : Math.max(L[i + 1][j], L[i][j + 1]);
    return L;
  }
  function ratio(a, b) {
    const t = a.length + b.length;
    return t ? 2 * lcsTable(a, b)[0][0] / t : 1;
  }
  function opcodes(a, b) {
    const L = lcsTable(a, b), ops = [];
    let i = 0, j = 0;
    const push = (tag, i1, i2, j1, j2) => {
      const last = ops[ops.length - 1];
      if (last && last[0] === tag) { last[2] = i2; last[4] = j2; } else ops.push([tag, i1, i2, j1, j2]);
    };
    while (i < a.length || j < b.length) {
      if (i < a.length && j < b.length && a[i] === b[j]) { push("equal", i, i + 1, j, j + 1); i++; j++; }
      else if (j < b.length && (i >= a.length || L[i][j + 1] >= L[i + 1][j])) { push("change", i, i, j, j + 1); j++; }
      else { push("change", i, i + 1, j, j); i++; }
    }
    return ops;
  }

  /** Your answer vs. the closest accepted answer, token by token: [{text, ok}] for each side. */
  function diff(given, accepted) {
    const g = canon(given);
    let best = accepted[0], bestR = -1;
    for (const a of accepted) { const r = ratio(g, canon(a)); if (r > bestR) { bestR = r; best = a; } }
    const gRaw = rawTokens(given).map(showTok), cRaw = rawTokens(best).map(showTok), c = canon(best);
    const you = [], ans = [];
    for (const [tag, i1, i2, j1, j2] of opcodes(g, c)) {
      gRaw.slice(i1, i2).forEach(t => you.push({ text: t, ok: tag === "equal" }));
      cRaw.slice(j1, j2).forEach(t => ans.push({ text: t, ok: tag === "equal" }));
    }
    return { you, ans };
  }

  // ------------------------------------------------------------------ permission drills
  const oct = (n, w) => n.toString(8).padStart(w, "0");
  const triple = n => [["r", 4], ["w", 2], ["x", 1]].map(([c, b]) => (n & b ? c : "-")).join("");

  function modeStr(o) {
    const sp = (o >> 9) & 7, u = (o >> 6) & 7, g = (o >> 3) & 7, x = o & 7;
    const s = [triple(u), triple(g), triple(x)];
    if (sp & 4) s[0] = s[0].slice(0, 2) + (u & 1 ? "s" : "S");
    if (sp & 2) s[1] = s[1].slice(0, 2) + (g & 1 ? "s" : "S");
    if (sp & 1) s[2] = s[2].slice(0, 2) + (x & 1 ? "t" : "T");
    return s.join("");
  }

  function applyChmod(mode9, expr) {
    const shifts = { u: 6, g: 3, o: 0 };
    for (const clause of expr.split(",")) {
      const m = /^([ugoa]*)([+\-=])([rwx]*)$/.exec(clause);
      const who = (m[1] === "" || m[1] === "a") ? "ugo" : m[1];
      const bits = [...m[3]].reduce((s, p) => s + { r: 4, w: 2, x: 1 }[p], 0);
      for (const w of who) {
        const sh = shifts[w], cur = (mode9 >> sh) & 7;
        const nw = m[2] === "+" ? cur | bits : m[2] === "-" ? cur & ~bits : bits;
        mode9 = (mode9 & ~(7 << sh)) | (nw << sh);
      }
    }
    return mode9;
  }

  const digitParts = d => {
    const parts = [4, 2, 1].filter(v => d & v).map(String);
    return parts.length > 1 ? `${parts.join("+")} = ${triple(d)}` : `${d} = ${triple(d)}`;
  };
  const groupsBreakdown = o => [["owner", 6], ["group", 3], ["other", 0]]
    .map(([n, sh]) => `${n} ${(o >> sh) & 7}: ${digitParts((o >> sh) & 7)}`).join("   ");

  const STR_TO_OCTAL = [0o755, 0o644, 0o640, 0o750, 0o700, 0o600, 0o664, 0o775, 0o754, 0o444, 0o711, 0o660, 0o777, 0o500];
  const OCTAL_TO_STR = [0o755, 0o644, 0o640, 0o750, 0o700, 0o600, 0o664, 0o775, 0o754, 0o444, 0o711, 0o660, 0o740];
  const SYM_STARTS = [0o644, 0o755, 0o640, 0o700, 0o600, 0o664, 0o750];
  const SYM_EXPRS = ["u+x", "g+w", "o-r", "go-rx", "a+r", "u=rwx,g=rx,o=", "g=rw", "o+w", "u-w", "ug+x", "a-x", "o=r"];
  const MASKS = [0o022, 0o002, 0o027, 0o077, 0o007, 0o037, 0o026];
  const SPECIAL_MODES = [0o4755, 0o2755, 0o2770, 0o6755, 0o4700, 0o2775, 0o2750, 0o4711];

  function drillStrToOctal(o) {
    const s = modeStr(o);
    const one = (i, sh) => {
      const parts = [4, 2, 1].filter((v, k) => s[i + k] !== "-").map(String);
      const d = (o >> sh) & 7;
      return parts.length > 1 ? `${s.slice(i, i + 3)} = ${parts.join("+")} = ${d}` : `${s.slice(i, i + 3)} = ${d}`;
    };
    const steps = [[0, 6], [3, 3], [6, 0]].map(([i, sh]) => one(i, sh)).join("   ");
    return ["What octal mode is " + s + " ?", [oct(o, 3)],
      `Split into owner/group/other and add r=4 w=2 x=1 in each:  ${steps}  ->  ${oct(o, 3)}`];
  }

  function drillOctalToStr(o) {
    return [`What does mode ${oct(o, 3)} look like in ls -l (9 characters, no leading -)?`, [modeStr(o)],
      `Each digit is one group, built from 4=r 2=w 1=x:  ${groupsBreakdown(o)}  ->  ${modeStr(o)}`];
  }

  function drillSymbolic(start, expr) {
    const res = applyChmod(start, expr);
    const words = { u: "owner", g: "group", o: "other", a: "everyone", "+": "add", "-": "remove", "=": "set exactly" };
    const said = expr.split(",").map(clause => {
      const m = /^([ugoa]*)([+\-=])([rwx]*)$/.exec(clause);
      const who = [...(m[1] || "a")].map(w => words[w]).join("+");
      return `${clause} = ${words[m[2]]} ${m[3] || "nothing"} for ${who}`;
    });
    return [`A file is ${oct(start, 3)}. After chmod ${expr} file, what is its octal mode?`, [oct(res, 3)],
      `${oct(start, 3)} is ${modeStr(start)}. ${said.join("; ")}. Result: ${modeStr(res)} = ${oct(res, 3)}.`];
  }

  function drillUmask(mask) {
    const kind = "file", base = 0o666, res = base & ~mask;
    const steps = [[6, "owner"], [3, "group"], [0, "other"]].map(([sh, n]) => {
      const b = (base >> sh) & 7, m = (mask >> sh) & 7, r = (res >> sh) & 7;
      return `${n} ${triple(b)} minus ${triple(m)} = ${triple(r)} (${r})`;
    });
    const note = (mask & 0o111) ? " A file has no x to remove, so mask bit 1 changes nothing." : "";
    return [`umask ${oct(mask, 3)}: what permissions does a new ${kind} get? (octal)`, [oct(res, 3)],
      `New ${kind}s start at ${oct(base, 3)}; the umask REMOVES its bits:  ` + steps.join("   ") + `  ->  ${oct(res, 3)}.${note}`];
  }

  function specialNote(o) {
    const sp = (o >> 9) & 7, bits = [];
    if (sp & 4) bits.push("4 = SUID: s replaces the owner's x");
    if (sp & 2) bits.push("2 = SGID: s replaces the group's x");
    if (sp & 1) bits.push("1 = sticky: t replaces the others' x");
    const parts = [4, 2, 1].filter(v => sp & v).map(String);
    const head = `First digit ${sp}` + (parts.length > 1 ? ` = ${parts.join(" + ")}` : "");
    return head + ": " + bits.join("; ") + ".";
  }

  function drillSpecialToStr(o) {
    return [`What does mode ${oct(o, 4)} look like in ls -l (9 characters)?`, [modeStr(o)],
      `Last three digits ${oct(o & 0o777, 3)} = ${modeStr(o & 0o777)}. ${specialNote(o)}  ->  ${modeStr(o)}`];
  }

  function drillStrToSpecial(o) {
    return [`What 4-digit octal mode is ${modeStr(o)} ?`, [oct(o, 4)],
      `Read the s/t letters first: ${specialNote(o)} The rest is ${modeStr(o & 0o777)} = ${oct(o & 0o777, 3)}, so ${oct(o, 4)}.`];
  }

  const choice = arr => arr[Math.floor(Math.random() * arr.length)];
  const DRILLS = [
    () => drillStrToOctal(choice(STR_TO_OCTAL)),
    () => drillOctalToStr(choice(OCTAL_TO_STR)),
    () => drillSymbolic(choice(SYM_STARTS), choice(SYM_EXPRS)),
    () => drillUmask(choice(MASKS)),
    () => drillSpecialToStr(choice(SPECIAL_MODES)),
    () => drillStrToSpecial(choice(SPECIAL_MODES)),
  ];

  function drillItems(n) {
    const items = [];
    for (let k = 0; k < n; k++) {
      const [prompt, answers, explain] = choice(DRILLS)();
      items.push({ id: null, topic: "drill", prompt, answers, why: "", explain, typed: false, loose: false });
    }
    return items;
  }

  // ------------------------------------------------------------------ progress
  const newDb = () => ({ q: {}, best: 0, sessions: 0, xp: 0 });
  function rec(db, id) { return db.q[id] || (db.q[id] = { right: 0, wrong: 0, streak: 0 }); }
  function isMissed(db, id) { const r = db.q[id]; return !!r && r.wrong > 0 && r.streak < 2; }

  /** Weighted draw without repeats: missed questions come up more, mastered ones less. */
  function pick(db, pool, n) {
    pool = pool.slice();
    const chosen = [];
    while (pool.length && chosen.length < n) {
      const weights = pool.map(q => {
        const r = db.q[q.id];
        return r ? Math.max(0.4, 1 + 2.5 * Math.min(r.wrong, 3) - 0.8 * Math.min(r.streak, 3)) : 3.0;
      });
      let x = Math.random() * weights.reduce((a, b) => a + b, 0), k = 0;
      while (k < weights.length - 1 && (x -= weights[k]) > 0) k++;
      chosen.push(pool.splice(k, 1)[0]);
    }
    return chosen;
  }

  function rankFor(ranks, xp) {
    let cur = ranks[0], nxt = null;
    ranks.forEach((r, i) => { if (xp >= r[0]) { cur = r; nxt = ranks[i + 1] || null; } });
    return [cur, nxt];
  }

  function wrap(text, width) {
    const words = text.split(/\s+/).filter(Boolean), lines = [];
    let line = "";
    for (const w of words) {
      if (!line) line = w;
      else if ((line + " " + w).length <= width) line += " " + w;
      else { lines.push(line); line = w; }
    }
    if (line) lines.push(line);
    return lines;
  }

  const api = {
    shlexSplit, canon, rawTokens, checkTyped, checkLoose, checkDrill, checkAnswer, showTok, diff, ratio,
    modeStr, applyChmod, triple, drillStrToOctal, drillOctalToStr, drillSymbolic, drillUmask,
    drillSpecialToStr, drillStrToSpecial, drillItems, DRILL_INPUTS: { STR_TO_OCTAL, OCTAL_TO_STR, SYM_STARTS, SYM_EXPRS, MASKS, SPECIAL_MODES },
    newDb, rec, isMissed, pick, rankFor, wrap,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.CMDQUIZ = api;
})(typeof window !== "undefined" ? window : globalThis);
