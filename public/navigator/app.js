import {summaryFingerprint} from './summary-shared.js';
import {receiveSummary} from './summary-client.js';
import {citationLabel, citationKind} from './summary-citations.js';
import {createImportsPage, IMPORT_LABELS} from './imports-client.js';
for (const [lang, label] of Object.entries(IMPORT_LABELS)) STRINGS[lang].tab_imports = label;

const STATES = { CA: "California", NJ: "New Jersey", MA: "Massachusetts" };
const STATE_ORDER = ["CA", "NJ", "MA"];
const RESULT_ORDER = ["applies", "unknown", "superseded", "not_yet_effective", "pending"];
const LOW_CONFIDENCE = 0.7;
const CONTEXT_CHARS = 1500;
const TABS = ["lookup", "imports", "changes", "rules", "pipeline"];
const QUIET_TABS = ["changes", "rules", "pipeline"];
const ICON = {
  search: '<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true"><circle cx="8.5" cy="8.5" r="5.6" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M12.8 12.8 17 17" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
  down: '<svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  left: '<svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><path d="M7.5 2.5 4 6l3.5 3.5" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  right: '<svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><path d="M4.5 2.5 8 6 4.5 9.5" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  close: '<svg viewBox="0 0 14 14" width="14" height="14" aria-hidden="true"><path d="m3 3 8 8M11 3l-8 8" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>',
};

const state = {
  lang: "en", meta: null, request: 0, last: {}, data: null, cards: new Map(), filter: "",
  finder: { text: "", scope: "", active: -1, matches: [] },
  library: { place: "", category: "", status: "", text: "" },
  summaryController: null,
  summaryPopoverAnchor: null,
};
try { state.lang = localStorage.getItem("lang") || "en"; } catch (error) { /* private window */ }

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const wording = (key) => STRINGS[state.lang][key] ?? STRINGS.en[key] ?? key;
const t = (key, values = {}) => wording(key).replace(/\{(\w+)\}/g, (_, name) => values[name] ?? "");
// Same wording, with ready-made HTML dropped into the sentence: a control, or a number set in bold.
const th = (key, html) => esc(wording(key)).replace(/\{(\w+)\}/g, (_, name) => html[name] ?? "");
const safeUrl = (url) => (/^https?:\/\//.test(url || "") ? url : "");
const cityName = (legalCity) => (legalCity || "").split(",")[0];
const placeName = (rule) => (rule.level === "state" ? STATES[rule.jurisdiction] || rule.jurisdiction : cityName(rule.jurisdiction));
const scopeLabel = (scope) => STATES[scope] || cityName(scope);
const isDay = (value) => /^\d{4}-\d{2}-\d{2}$/.test(value || "");

function showDate(value) {
  if (!isDay(value)) return value || "";
  const locale = { en: "en-US", es: "es-US", zh: "zh-CN" }[state.lang];
  return new Date(value + "T00:00:00Z").toLocaleDateString(locale, { year: "numeric", month: "short", day: "numeric", timeZone: "UTC" });
}

const count = (n) => Number(n).toLocaleString({ en: "en-US", es: "es-US", zh: "zh-CN" }[state.lang]);

function dayBefore(value) {
  const day = new Date(value + "T00:00:00Z");
  day.setUTCDate(day.getUTCDate() - 1);
  return day.toISOString().slice(0, 10);
}

// Static snapshot: answers were computed once by the original engine and saved as files.
async function sha16(text) {
  const buf = await crypto.subtle.digest("SHA-1", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("").slice(0, 16);
}
async function api(path, params = {}) {
  const query = new URLSearchParams(Object.entries(params).filter(([, v]) => v !== "" && v != null)).toString();
  const response = await fetch(path + (query ? "?" + query : ""));
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || response.statusText);
  return body;
}

function route() {
  const [path, query = ""] = location.hash.replace(/^#\/?/, "").split("?");
  return { tab: TABS.includes(path) ? path : "lookup", params: Object.fromEntries(new URLSearchParams(query)) };
}

function go(tab, params = {}) {
  const query = new URLSearchParams(Object.entries(params).filter(([, v]) => v !== "" && v != null)).toString();
  location.hash = "#/" + tab + (query ? "?" + query : "");
}

function chrome() {
  document.documentElement.lang = state.lang;
  document.title = t("app_title");
  $$("[data-t]").forEach((node) => { node.textContent = t(node.dataset.t); });
  const current = route().tab;
  const link = (tab) => `<a href="#/${tab}" class="${QUIET_TABS.includes(tab) ? "quiet" : ""}" ${tab === current ? 'aria-current="page"' : ""}>${esc(t("tab_" + tab))}</a>`;
  $("#nav").setAttribute("aria-label", t("nav_label"));
  $("#nav").innerHTML = TABS.filter((tab) => !QUIET_TABS.includes(tab)).map(link).join("") + '<span class="nav-gap"></span>' + QUIET_TABS.map(link).join("");
  $("#lang").value = state.lang;
}

const wait = () => `<p class="wait">${esc(t("loading"))}</p>`;
// While extraction is still running the rule file is partial, and every page that lists rules says so.
const partial = (extraction) => (extraction && extraction.done < extraction.total ? `<p class="note caution"><b>${esc(t("partial_title"))}</b> ${esc(t("partial_body", { n: extraction.done, m: extraction.total }))}</p>` : "");
const problem = (error) => `<p class="note review problem">${esc(t("load_error", { msg: error.message }))}</p>`;

/* ---------- shared parts ---------- */

// Results for an address ("r") and the status of a rule ("s") share one set of marks.
function st(kind, vocabulary = "r") {
  return `<span class="st st-${esc(kind)}"><i aria-hidden="true"></i>${esc(t(vocabulary + "_" + kind))}</span>`;
}

function flagsOf(rule, answer) {
  const flags = [];
  if (answer && answer.conflict_flag) flags.push("flag_review");
  if (rule.conflict_flag) flags.push("flag_sources");
  if (rule.confidence != null && rule.confidence < LOW_CONFIDENCE) flags.push("flag_low");
  return flags;
}

function whenText(rule) {
  if (rule.status === "pending" || rule.status === "failed") return "";
  const parts = [rule.effective_date ? t(rule.status === "not_yet_effective" ? "takes_effect" : "since", { d: showDate(rule.effective_date) }) : t("no_date")];
  if (rule.valid_through) parts.push(t("valid_through", { d: showDate(rule.valid_through) }));
  return parts.join(" ");
}

// An "unknown" can be settled by the reader only when it waits on a building fact the record lacks.
function canAddFact(answer) {
  const address = state.data && state.data.address;
  if (!address) return false;
  return answer.missing_facts.some((missing) => (/built|newer_than/.test(missing.field) && address.year_built == null) || (/units/.test(missing.field) && address.units == null));
}

function quoteHtml(rule, source, extra = "") {
  return `<figure class="quote"><blockquote><span class="hl">${esc(source.quoted_span)}</span></blockquote>
    <figcaption><span class="cite">${esc(rule.citation)}.</span> ${esc(t("src_line", { doc: source.doc_id, t: source.retrieved || "—" }))} ${esc(t(source.origin === "starter" ? "official_pack" : "extra_source"))}${extra}</figcaption></figure>`;
}

function rowMore(rule, answer, reason, flags) {
  const source = rule.sources[0];
  const url = safeUrl(source.url);
  const when = whenText(rule);
  const notes = flags.map((key) => {
    const body = key === "flag_review" ? t("note_review") : key === "flag_sources" ? (rule.conflict_note || "").replace(/^Sources disagree:\s*/, "") : t("note_low", { p: Math.round(rule.confidence * 100) });
    return `<p class="note review"><b>${esc(t(key))}.</b> ${esc(body)}</p>`;
  }).join("");
  return `<div class="row-more">
    ${reason ? `<p><b>${esc(t("run_why"))}</b> ${esc(reason)}</p>` : ""}
    <p><b>${esc(t("run_rule"))}</b> ${esc(rule.requirement)}</p>
    ${notes}
    ${quoteHtml(rule, source, rule.sources.length > 1 ? " " + esc(t("more_sources", { n: rule.sources.length - 1 })) : "")}
    ${when ? `<p class="when">${esc(when)}</p>` : ""}
    <p class="actions">
      ${answer && answer.result === "not_yet_effective" && isDay(rule.effective_date) ? `<button class="btn primary" data-act="day" data-day="${esc(rule.effective_date)}">${esc(t("act_on_date", { d: showDate(rule.effective_date) }))}</button>` : ""}
      ${answer && answer.result === "unknown" && canAddFact(answer) ? `<button class="btn primary" data-act="building">${esc(t("act_add_fact"))}</button>` : ""}
      <button class="btn" data-act="sheet" data-focus="top">${esc(t(answer ? "act_decided" : "act_record"))}</button>
      <button class="btn" data-act="sheet" data-focus="source">${esc(t("act_find"))}</button>
      ${url ? `<a class="btn" href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(t("act_original"))}</a>` : ""}
    </p>
  </div>`;
}

// One row serves the address answer (a result at this address) and the rule list (the rule's own status).
function ruleRow(rule, answer) {
  state.cards.set(rule.team_rule_id, { rule, answer });
  const result = answer && answer.result;
  const shown = result || rule.status;
  const reason = answer && answer.explanation ? answer.explanation.split(" Source: ")[0] : "";
  const flags = flagsOf(rule, answer);
  return `<details class="row" data-rule="${esc(rule.team_rule_id)}" data-result="${esc(shown)}">
    <summary>
      <span class="row-status">${result ? st(result) : st(rule.status, "s")}${shown === "not_yet_effective" && rule.effective_date ? `<span class="row-sub">${esc(t("from_date", { d: showDate(rule.effective_date) }))}</span>` : ""}
        ${flags.includes("flag_review") ? `<span class="row-flag">${esc(t("flag_review"))}</span>` : ""}</span>
      <span class="row-main">
        <span class="row-title">${esc(rule.title || rule.citation)}</span>
        ${rule.key_value ? `<span class="row-key">${esc(rule.key_value)}</span>` : `<span class="row-sum">${esc(rule.requirement)}</span>`}
        ${reason && (result === "unknown" || result === "superseded") ? `<span class="row-why">${esc(reason)}</span>` : ""}
      </span>
      <span class="row-origin">
        ${answer ? `<span class="row-place">${esc(placeName(rule))}</span>` : ""}
        <span class="cite">${esc(rule.citation)}</span>
        ${flags.filter((key) => key !== "flag_review").map((key) => `<span class="row-flag">${esc(t(key))}</span>`).join("")}
      </span>
      <span class="row-chev">${ICON.down}</span>
    </summary>
    ${rowMore(rule, answer, reason, flags)}
  </details>`;
}

// Category on the left, its rules on the right: the same register on every page that lists rules.
function register(rows, emptyKey) {
  return state.meta.categories.map((category) => {
    const inside = rows.filter((row) => row.rule.category === category);
    if (!inside.length && !emptyKey) return "";
    return `<section class="group"><h3 class="side">${esc(t("c_" + category))}</h3>
      <div class="rows">${inside.length ? inside.map((row) => ruleRow(row.rule, row.answer)).join("") : `<p class="none">${esc(t(emptyKey))}</p>`}</div></section>`;
  }).join("");
}

const dl = (pairs) => `<dl class="dl">${pairs.filter(([, value]) => value).map(([label, value]) => `<div><dt>${esc(label)}</dt><dd>${value}</dd></div>`).join("")}</dl>`;

/* ---------- address finder ---------- */

function finderHtml(large) {
  return `<div class="finder${large ? " large" : ""}" id="finder">
    <span class="finder-icon">${ICON.search}</span>
    <input id="finder-input" type="text" role="combobox" aria-expanded="false" aria-controls="finder-list" aria-autocomplete="list" autocomplete="off" spellcheck="false"
      placeholder="${esc(t(large ? "finder_placeholder" : "finder_again"))}" aria-label="${esc(t("finder_placeholder"))}">
    <div class="pop finder-pop" id="finder-pop" hidden>
      <div class="finder-scope" id="finder-scope" hidden></div>
      <div class="finder-list" id="finder-list" role="listbox" aria-label="${esc(t("finder_placeholder"))}"></div>
    </div>
  </div>`;
}

function drawFinder() {
  const finder = state.finder;
  const tokens = finder.text.toLowerCase().split(/\s+/).filter(Boolean);
  finder.matches = state.meta.addresses.filter((a) => (!finder.scope || a.legal_city === finder.scope || a.state === finder.scope) && tokens.every((token) => a.hay.includes(token)));
  finder.active = finder.matches.length && tokens.length ? 0 : -1;
  const scope = $("#finder-scope");
  scope.hidden = !finder.scope;
  scope.innerHTML = finder.scope ? `<span>${esc(t("finder_scope", { place: scopeLabel(finder.scope) }))}</span><button class="linkbtn" data-act="scope-clear">${esc(t("finder_scope_clear"))}</button>` : "";
  const perCity = new Map();
  for (const a of finder.matches) perCity.set(a.legal_city, (perCity.get(a.legal_city) || 0) + 1);
  let city, html = "";
  finder.matches.forEach((a, index) => {
    if (a.legal_city !== city) {
      city = a.legal_city;
      html += `<div class="opt-group" role="presentation"><span>${esc(city ? cityName(city) + ", " + STATES[a.state] : STATES[a.state])}</span><span class="num">${perCity.get(city)}</span></div>`;
    }
    const units = a.units != null ? t("n_units", { n: a.units }) : a.units_at_least != null ? t("at_least_units", { n: a.units_at_least }) : "";
    html += `<div class="opt" role="option" id="opt-${index}" data-id="${esc(a.address_id)}" aria-selected="false">
      <span class="opt-street">${esc(a.street_address)}</span><span class="opt-id num">${esc(a.address_id)}</span>
      <span class="opt-meta"><span>${esc(a.postal_city)} ${esc(a.zip)}</span>${a.year_built != null ? `<span>${esc(t("built", { y: a.year_built }))}</span>` : ""}${units ? `<span>${esc(units)}</span>` : ""}</span>
    </div>`;
  });
  $("#finder-list").innerHTML = finder.matches.length ? html : `<p class="none">${esc(t("finder_none", { q: finder.text.trim() }))}</p>`;
  markActive();
}

function markActive() {
  const input = $("#finder-input");
  $$("#finder-list .opt").forEach((option, index) => option.setAttribute("aria-selected", String(index === state.finder.active)));
  const active = $("#opt-" + state.finder.active);
  if (active) { input.setAttribute("aria-activedescendant", active.id); active.scrollIntoView({ block: "nearest" }); }
  else input.removeAttribute("aria-activedescendant");
}

function openFinder() {
  $("#finder-pop").hidden = false;
  $("#finder-input").setAttribute("aria-expanded", "true");
  drawFinder();
}

function closeFinder() {
  const pop = $("#finder-pop");
  if (!pop || pop.hidden) return;
  pop.hidden = true;
  $("#finder-input").setAttribute("aria-expanded", "false");
}

function chooseAddress(id) {
  state.finder.text = "";
  state.finder.scope = "";
  closeFinder();
  go("lookup", { id, as_of: route().params.as_of });
}

function bindFinder() {
  const input = $("#finder-input");
  input.value = state.finder.text;
  input.addEventListener("focus", openFinder);
  input.addEventListener("input", () => { state.finder.text = input.value; openFinder(); });
  input.addEventListener("keydown", (event) => {
    const { matches } = state.finder;
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      if ($("#finder-pop").hidden) openFinder();
      if (matches.length) state.finder.active = (state.finder.active + (event.key === "ArrowDown" ? 1 : -1) + matches.length) % matches.length;
      markActive();
    } else if (event.key === "Enter" && matches.length) {
      chooseAddress(matches[Math.max(state.finder.active, 0)].address_id);
    } else if (event.key === "Escape") {
      closeFinder();
    }
  });
  // Keep the caret in the field while the list is clicked, so the list does not close under the pointer.
  $("#finder-pop").addEventListener("mousedown", (event) => event.preventDefault());
  $("#finder-list").addEventListener("click", (event) => {
    const option = event.target.closest(".opt");
    if (option) chooseAddress(option.dataset.id);
  });
}

function scopeFinder(scope) {
  state.finder.scope = scope;
  state.finder.text = "";
  const input = $("#finder-input");
  input.value = "";
  input.focus();
  openFinder();
  input.scrollIntoView({ block: "nearest" });
}

/* ---------- address lookup ---------- */

function landingHtml() {
  const states = STATE_ORDER.map((code) => {
    const cities = new Map();
    for (const a of state.meta.addresses) if (a.state === code && a.legal_city) cities.set(a.legal_city, (cities.get(a.legal_city) || 0) + 1);
    return `<div><button class="browse-state" data-act="scope" data-scope="${code}">${esc(STATES[code])}</button>
      <ul>${[...cities].map(([city, n]) => `<li><button data-act="scope" data-scope="${esc(city)}"><span>${esc(cityName(city))}</span><span class="num">${n}</span></button></li>`).join("")}</ul></div>`;
  }).join("");
  return `<section class="landing">
    <h1>${esc(t("landing_title"))}</h1>
    ${finderHtml(true)}
    <div class="landing-cols">
      <section><h2>${esc(t("browse_title"))}</h2><div class="browse">${states}</div></section>
    </div>
  </section>`;
}

function addressHtml(data) {
  const a = data.address;
  const entered = data.entered_facts;
  const mine = (name) => (name in entered ? ` <em class="mine">${esc(t("entered_by_you"))}</em>` : "");
  const gap = (key) => `<li class="gap"><span class="st st-unknown"><i aria-hidden="true"></i></span>${esc(t(key))} <button class="linkbtn" data-act="building">${esc(t("add_it"))}</button></li>`;
  const year = a.year_built != null ? `<li>${esc(t("built", { y: a.year_built }))}${mine("year_built")}</li>` : gap("no_year");
  const units = a.units != null ? `<li>${esc(t("n_units", { n: a.units }))}${mine("units")}</li>`
    : a.units_at_least != null ? `<li>${esc(t("at_least_units", { n: a.units_at_least }))}</li>` : gap("no_units");
  const city = cityName(a.legal_city);
  const crumb = (scope, label) => `<button data-act="scope" data-scope="${esc(scope)}" title="${esc(t("other_in", { place: label }))}">${esc(label)}</button>`;
  const note = a.resolved_by !== "geocoder" ? `<p class="note caution">${esc(t("city_fallback"))}</p>`
    : city && city.toLowerCase() !== String(a.postal_city).toLowerCase() ? `<p class="note">${esc(t("mailing_differs", { postal: a.postal_city, city }))}</p>` : "";
  const siblings = state.meta.addresses.filter((other) => other.legal_city === a.legal_city);
  const index = siblings.findIndex((other) => other.address_id === a.address_id);
  const step = (other, icon, key) => `<button class="iconbtn" data-act="address" data-id="${other ? esc(other.address_id) : ""}" ${other ? "" : "disabled"} title="${esc(t(key, { city }))}" aria-label="${esc(t(key, { city }))}">${icon}</button>`;
  return `<div class="finder-row">${finderHtml(false)}
      <div class="stepper">${step(siblings[index - 1], ICON.left, "prev_address")}<span class="num">${esc(t("step_of", { i: index + 1, n: siblings.length, city }))}</span>${step(siblings[index + 1], ICON.right, "next_address")}</div>
    </div>
    <header class="address">
      <p class="crumbs">${crumb(a.state, STATES[a.state] || a.state)}${city ? `<span aria-hidden="true">›</span>${crumb(a.legal_city, city)}` : ""}</p>
      <h1 class="plaque">${esc(a.street_address)}</h1>
      <p class="mail">${esc(a.postal_city)}, ${esc(a.state)} ${esc(a.zip)}</p>
      ${note}
      <ul class="facts">${year}${units}${a.use_description ? `<li>${esc(a.use_description)}</li>` : ""}<li><button class="linkbtn" data-act="building">${esc(t("building_record"))}</button></li></ul>
    </header>`;
}

function answerHtml(data) {
  const counts = Object.fromEntries(RESULT_ORDER.map((result) => [result, data.results.filter((row) => row.result === result).length]));
  if (state.filter && !counts[state.filter]) state.filter = "";
  const order = (x, y) => RESULT_ORDER.indexOf(x.result) - RESULT_ORDER.indexOf(y.result) || (x.rule.level === y.rule.level ? 0 : x.rule.level === "state" ? -1 : 1);
  const rows = data.results.map((answer) => ({ rule: answer.rule, answer })).sort((x, y) => order(x.answer, y.answer));
  const enacted = rows.filter((row) => row.answer.result !== "pending");
  const pending = rows.filter((row) => row.answer.result === "pending");
  const dates = new Map();
  for (const row of data.results) {
    if (!isDay(row.rule.effective_date)) continue;
    dates.set(row.rule.effective_date, (dates.get(row.rule.effective_date) || new Set()).add(row.rule.citation));
  }
  const keyDates = [...dates].sort((x, y) => (x[0] < y[0] ? 1 : -1));
  const entered = Object.entries(data.entered_facts).map(([name, value]) => `${t(name === "year_built" ? "b_year" : "b_units")}: ${value}`).join(", ");
  const dateButton = `<button class="datebtn" data-act="date" aria-expanded="false" aria-controls="date-pop">${esc(showDate(data.as_of))}${ICON.down}</button>`;
  return `<section class="answer">
    <div class="answer-head">
      <div class="datewrap">
        <h2>${th("rules_as_of", { date: dateButton })}</h2>
        ${data.as_of !== state.meta.default_date ? `<button class="linkbtn back" data-act="day" data-day="${esc(state.meta.default_date)}">${esc(t("date_default", { d: showDate(state.meta.default_date) }))}</button>` : ""}
        <div class="pop date-pop" id="date-pop" hidden>
          <label for="date-input">${esc(t("date_field"))}</label>
          <input id="date-input" type="date" value="${esc(data.as_of)}">
          ${keyDates.length ? `<p class="pop-title">${esc(t("date_changes"))}</p><ul class="keydates">${keyDates.map(([day, cites]) => `<li>
            <span class="num">${esc(showDate(day))}</span><span class="cite">${esc([...cites].join("; "))}</span>
            <span class="kd-go"><button class="btn small" data-act="day" data-day="${dayBefore(day)}">${esc(t("day_before"))}</button><button class="btn small" data-act="day" data-day="${day}">${esc(t("that_day"))}</button></span></li>`).join("")}</ul>` : ""}
        </div>
      </div>
      <div class="filters" role="group" aria-label="${esc(t("filter_label"))}">${RESULT_ORDER.filter((result) => counts[result]).map((result) => `<button class="filter" data-act="filter" data-result="${result}" aria-pressed="false" title="${esc(t("r_" + result + "_d"))}"><b class="num">${counts[result]}</b>${st(result)}</button>`).join("")}</div>
    </div>
    ${data.snapshot_note ? `<p class="note caution">${esc(t("snapshot_note", { d: showDate(data.as_of) }))}</p>` : ""}
    ${partial(data.extraction)}
    ${entered ? `<p class="note caution">${esc(t("entered_note", { facts: entered }))} <button class="linkbtn" data-act="remove-entries">${esc(t("remove_entries"))}</button></p>` : ""}
    ${summaryHtml(data)}
    <div id="enacted">${register(enacted, "no_rule_category")}</div>
    ${pending.length ? `<section id="pending" class="pending"><h2>${esc(t("sec_pending"))}</h2>${register(pending)}</section>` : ""}
    ${data.left_out.length ? `<details class="leftout"><summary>${esc(t("left_summary", { n: data.left_out.length }))}</summary>
      ${register(data.left_out.map((item) => ({ rule: item.rule, answer: { result: null, steps: item.steps, missing_facts: [] } })))}</details>` : ""}
  </section>`;
}

function summaryHtml(data) {
  return `<section id="law-summary" class="law-summary" aria-labelledby="summary-title">
    <header><h3 id="summary-title">${esc(t("summary_title"))}</h3><p class="hint">${esc(t("summary_scope"))}</p>
      <p class="summary-legend"><span class="legend-applies">${esc(t("r_applies"))}</span><span class="legend-review">? ${esc(t("summary_review"))}</span><span class="legend-inactive">◷ ${esc(t("summary_inactive"))}</span><span class="legend-excluded">× ${esc(t("summary_excluded"))}</span><span>${esc(t("summary_extra_hint"))}</span></p>
    </header>
    <div class="summary-scroll" tabindex="0" role="region" aria-label="${esc(t("summary_title"))}">
      ${data.extraction.done < data.extraction.total ? `<p class="note caution">${esc(t("summary_partial", {n: data.extraction.done, m: data.extraction.total}))}</p>` : ""}
      <p class="summary-status hint" role="status">${esc(t("summary_loading"))}</p>
      <div class="summary-sections"></div>
      <div class="summary-error" hidden><p class="note caution"></p><button class="btn small" data-act="summary-retry">${esc(t("summary_retry"))}</button></div>
    </div>
  </section>`;
}

function showSummaryFailure(box, error = {}) {
  box.dataset.status = "error";
  $(".summary-status", box).textContent = t("summary_incomplete");
  $(".summary-error", box).hidden = false;
  $(".summary-error p", box).textContent = t(error.code === "missing_key" ? "summary_missing_key" : "summary_failed");
}

function appendSummaryParagraph(box, paragraph) {
  const sections = $(".summary-sections", box);
  let section = $(`[data-section="${paragraph.section}"]`, sections);
  if (!section) {
    section = document.createElement("section");
    section.dataset.section = paragraph.section;
    section.innerHTML = `<h4>${esc(t("summary_" + paragraph.section))}</h4>`;
    sections.append(section);
  }
  const block = document.createElement("div");
  block.className = "summary-paragraph";
  block.innerHTML = `<p>${paragraph.sentences.map(sentence => `<span class="summary-sentence">${esc(sentence.text)}<span class="summary-inline-refs">${sentence.refs.map(ref => {
    const kind = citationKind(ref);
    const rule = state.cards.get(ref.rule_id)?.rule;
    const short = citationLabel(ref.citation, rule);
    const sourceNumber = rule?.sources.length > 1 ? `<sup>${ref.source_index + 1}</sup>` : "";
    const origin = t(ref.origin === "starter" ? "official_pack" : "extra_source");
    const result = ref.result ? t("r_" + ref.result) : t("summary_excluded");
    const label = `${ref.citation} · ${ref.doc_id} · ${result}${ref.conflict_flag ? " · " + t("flag_review") : ""} · ${origin}`;
    return `<button class="summary-citation ref-${kind}${ref.conflict_flag ? " ref-conflict" : ""}${ref.origin !== "starter" ? " ref-extra" : ""}" data-rule="${esc(ref.rule_id)}" data-act="summary-source" data-source-index="${ref.source_index}" title="${esc(label)}" aria-label="${esc(t("summary_open_source", {source: label}))}" aria-haspopup="dialog" aria-expanded="false">${kind !== "applies" ? `<span class="ref-status" aria-hidden="true">${{review: "?", inactive: "◷", excluded: "×"}[kind]}</span>` : ""}${esc(short)}${sourceNumber}</button>`;
  }).join("")}</span></span>`).join(" ")}</p>`;
  section.append(block);
}

function closeSummaryPopover(returnFocus = false) {
  const anchor = state.summaryPopoverAnchor;
  $("#summary-reference-popover")?.remove();
  anchor?.setAttribute("aria-expanded", "false");
  anchor?.removeAttribute("aria-controls");
  state.summaryPopoverAnchor = null;
  if (returnFocus && anchor?.isConnected) anchor.focus({preventScroll: true});
}

function summaryReferencePreview(anchor) {
  const same = state.summaryPopoverAnchor === anchor;
  closeSummaryPopover();
  if (same) return;
  const id = anchor.dataset.rule, index = Number(anchor.dataset.sourceIndex);
  const card = state.cards.get(id), source = card?.rule.sources[index];
  if (!source) return;
  const {rule, answer} = card;
  const sourceUrl = safeUrl(source.url);
  let hostname = "";
  try {if (sourceUrl) hostname = new URL(sourceUrl).hostname;} catch { /* the saved citation remains readable */ }
  const reason = answer?.explanation || (answer?.result == null ? answer?.steps?.at(-1)?.explanation : "");
  const pop = document.createElement("section");
  pop.id = "summary-reference-popover";
  pop.className = "pop summary-reference-popover";
  pop.setAttribute("role", "dialog");
  pop.setAttribute("aria-labelledby", "summary-reference-title");
  pop.innerHTML = `<header><span class="cite">${esc(rule.citation)}</span><button class="iconbtn" data-act="summary-dismiss" aria-label="${esc(t("close"))}">${ICON.close}</button></header>
    <h4 id="summary-reference-title">${esc(rule.title || rule.citation)}</h4>
    <div class="reference-status">${answer?.result ? st(answer.result) : `<span class="muted">${esc(t("summary_excluded"))}</span>`}${rule.conflict_flag || answer?.conflict_flag ? `<span class="reference-caution">${esc(t("flag_review"))}</span>` : ""}</div>
    <p class="reference-key">${esc(rule.key_value || rule.requirement)}</p>
    ${reason && answer?.result !== "applies" ? `<p class="hint">${esc(reason)}</p>` : ""}
    ${rule.conflict_flag || answer?.conflict_flag ? `<p class="hint reference-caution">${esc(t("note_review"))}</p>` : ""}
    <p class="reference-source">${esc(placeName(rule))} · ${esc(source.doc_id)}${hostname ? " · " + esc(hostname) : ""}<br>${esc(t(source.origin === "starter" ? "official_pack" : "extra_source"))}</p>
    <button class="btn small reference-details" data-act="summary-details" data-rule="${esc(id)}" data-source-index="${index}">${esc(t("summary_full_details"))}${ICON.right}</button>`;
  document.body.append(pop);
  state.summaryPopoverAnchor = anchor;
  anchor.setAttribute("aria-expanded", "true");
  anchor.setAttribute("aria-controls", pop.id);
  const rect = anchor.getBoundingClientRect();
  const left = Math.max(12, Math.min(rect.left, window.innerWidth - pop.offsetWidth - 12));
  const below = rect.bottom + 8;
  const top = below + pop.offsetHeight <= window.innerHeight - 12 ? below : Math.max(12, rect.top - pop.offsetHeight - 8);
  pop.style.left = `${left}px`; pop.style.top = `${top}px`;
  $(".reference-details", pop).focus({preventScroll: true});
}

async function startSummary(params, request, data) {
  const box = $("#law-summary");
  if (!box || request !== state.request) return;
  closeSummaryPopover();
  state.summaryController?.abort();
  const controller = new AbortController(); state.summaryController = controller;
  const current = () => !controller.signal.aborted && request === state.request && box.isConnected;
  box.dataset.status = "loading";
  delete box.dataset.firstParagraphMs; delete box.dataset.totalMs; delete box.dataset.cached;
  $(".summary-sections", box).replaceChildren();
  $(".summary-error", box).hidden = true;
  $(".summary-status", box).textContent = t("summary_loading");
  const started = performance.now();
  try {
    const fingerprint = await summaryFingerprint(data);
    if (!current()) return;
    const query = {address_id: params.id, as_of: data.as_of};
    for (const field of ["year_built", "units"]) if (params[field] !== undefined && params[field] !== "") query[field] = params[field];
    await receiveSummary({query, language: state.lang, fingerprint, signal: controller.signal, onEvent(event) {
      if (!current()) return;
      if (event.type === "paragraph") {
        if (!box.dataset.firstParagraphMs) box.dataset.firstParagraphMs = String(Math.round(performance.now() - started));
        appendSummaryParagraph(box, event.paragraph);
      }
      if (event.type === "complete") {
        box.dataset.status = "complete"; box.dataset.cached = String(event.cached);
        box.dataset.totalMs = String(Math.round(performance.now() - started));
        $(".summary-status", box).textContent = t(event.empty ? "summary_empty" : "summary_complete");
      }
      if (event.type === "error") showSummaryFailure(box, event);
    }});
  } catch (error) {
    if (!current()) return;
    if (error.code === "stale_evidence") {
      $(".summary-status", box).textContent = t("summary_refreshing");
      void render(); // Refresh the visible laws before requesting their new summary.
      return;
    }
    showSummaryFailure(box, error);
  }
}

function applyFilter() {
  const answer = $(".answer");
  if (!answer) return;
  const filter = state.filter;
  $$(".filter", answer).forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.result === filter)));
  $$("#enacted .row, #pending .row", answer).forEach((row) => { row.hidden = Boolean(filter) && row.dataset.result !== filter; });
  $$("#enacted .group, #pending .group", answer).forEach((group) => { group.hidden = Boolean(filter) && !$(`.row[data-result="${filter}"]`, group); });
  const pending = $("#pending");
  if (pending) pending.hidden = Boolean(filter) && filter !== "pending";
}

async function renderLookup(params, request) {
  const started = performance.now();
  const view = $("#view");
  if (!params.id) {
    state.data = null;
    view.innerHTML = landingHtml();
    bindFinder();
    return;
  }
  if (!view.firstElementChild) view.innerHTML = wait();
  view.classList.add("busy");
  let data;
  try {
    data = await api("/api/lookup", { address_id: params.id, as_of: params.as_of || state.meta.default_date, year_built: params.year_built, units: params.units });
  } finally {
    view.classList.remove("busy");
  }
  // A slower answer for an earlier click must not replace a newer one.
  if (request !== state.request) return;
  state.data = data;
  state.cards = new Map();
  document.title = `${data.address.street_address}, ${cityName(data.address.legal_city) || data.address.postal_city} · ${t("app_title")}`;
  view.innerHTML = addressHtml(data) + answerHtml(data);
  bindFinder();
  applyFilter();
  $("#law-summary").dataset.resultsMs = String(Math.round(performance.now() - started));
  void startSummary(params, request, data);
}

function relook(changes) {
  const { params } = route();
  go("lookup", { id: params.id, as_of: params.as_of, year_built: params.year_built, units: params.units, ...changes });
}

function closeDatePop() {
  const pop = $("#date-pop");
  if (!pop || pop.hidden) return;
  pop.hidden = true;
  $(".datebtn").setAttribute("aria-expanded", "false");
}

/* ---------- second level: the sheet ---------- */

function openSheet(html) {
  const sheet = $("#sheet");
  sheet.innerHTML = `<div class="sheet-in">${html}</div>`;
  if (!sheet.open) sheet.showModal();
  $(".sheet-body", sheet).scrollTop = 0;
}

function stepsHtml(steps) {
  const out = (outcome) => `<span class="out out-${esc(outcome)}">${esc(String(outcome).replace(/_/g, " "))}</span>`;
  const pairs = (facts) => Object.entries(facts).map(([k, v]) => `${k.replace(/_/g, " ")}: ${v !== null && typeof v === "object" ? JSON.stringify(v) : v ?? "—"}`).join(", ");
  const lines = (facts) => (Array.isArray(facts) ? facts.map((item) => `<span class="fact">${item.outcome ? out(item.outcome) + " " : ""}${esc(item.explanation || pairs(item))}</span>`)
    : facts && typeof facts === "object" && Object.keys(facts).length ? [`<span class="fact">${esc(pairs(facts))}</span>`] : []).join("");
  return `<ol class="steps">${steps.map((step) => `<li><span class="num">${esc(step.step)}</span><span>${esc(step.explanation)}</span>${out(step.outcome)}${lines(step.facts)}</li>`).join("")}</ol>`;
}

function ruleSheet(id, focus, sourceIndex = 0) {
  const { rule, answer } = state.cards.get(id);
  const result = answer && answer.result;
  const relation = (list) => list.map((other) => `<p><span class="cite">${esc(other.citation)}</span> <span class="muted num">${esc(other.team_rule_id)}</span><span class="basis cite">“${esc(other.basis)}”</span></p>`).join("");
  const corrections = rule.fact_corrections.map((c) => `<p>${esc(Object.entries(c.after || {}).map(([k, v]) => `${k.replace(/_/g, " ")}: ${v}`).join(", "))}<span class="basis">${esc(c.source || c.reason || "")}</span></p>`).join("");
  const sources = rule.sources.map((source, index) => {
    const url = safeUrl(source.url);
    return `<div class="source" data-index="${index}">${quoteHtml(rule, source)}
      <p class="actions"><button class="btn" data-act="context" aria-expanded="false">${esc(t("ctx_show"))}</button>${url ? `<a class="btn" href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(t("act_original"))}</a>` : ""}</p>
      <div class="context-box" hidden></div></div>`;
  }).join("");
  openSheet(`<header class="sheet-head"><div>${result ? st(result) : st(rule.status, "s")}<h2>${esc(rule.title || rule.citation)}</h2>
      <p class="sheet-sub"><span>${esc(placeName(rule))}</span><span class="cite">${esc(rule.citation)}</span></p></div>
      <button class="iconbtn" data-act="close" aria-label="${esc(t("close"))}" title="${esc(t("close"))}">${ICON.close}</button></header>
    <div class="sheet-body" data-rule="${esc(id)}">
      ${answer && answer.steps ? `<section><h3>${esc(t("sheet_decided"))}</h3>${stepsHtml(answer.steps)}</section>` : ""}
      <section id="sheet-source"><h3>${esc(t("sheet_source"))}</h3>${sources}</section>
      <section><h3>${esc(t("sheet_rule"))}</h3>${dl([
        [t("f_requirement"), esc(rule.requirement)], [t("f_key"), esc(rule.key_value)], [t("f_coverage"), esc(rule.coverage_conditions)],
        [t("f_exemptions"), esc(rule.exemptions)], [t("f_penalty"), esc(rule.penalty)], [t("f_interaction"), esc(rule.interaction)],
        [t("f_yields"), relation(rule.yields_to)], [t("f_prevails"), relation(rule.prevails_over)],
        [t("f_effective"), esc(rule.effective_date ? showDate(rule.effective_date) : t("no_date"))], [t("f_valid"), esc(showDate(rule.valid_through))],
        [t("f_corrections"), corrections],
      ])}</section>
      <section><h3>${esc(t("sheet_extract"))}</h3>${dl([
        [t("f_confidence"), rule.confidence != null ? Math.round(rule.confidence * 100) + "%" : ""], [t("f_rule_id"), esc(rule.team_rule_id)],
        [t("f_documents"), esc(rule.sources.map((source) => source.doc_id).join(", "))], [t("f_packet"), esc(rule.packet_id)], [t("f_date_source"), esc(rule.date_source)],
      ])}</section>
    </div>`);
  if (focus === "source") {
    $("#sheet-source").scrollIntoView();
    const source = $(`#sheet-source .source[data-index="${sourceIndex}"]`);
    if (source) {source.scrollIntoView({block: "start"}); showContext(source);}
  }
}

async function showContext(box) {
  const panel = $(".context-box", box);
  const button = $('[data-act="context"]', box);
  const opening = panel.hidden;
  panel.hidden = !opening;
  button.setAttribute("aria-expanded", String(opening));
  button.textContent = t(opening ? "ctx_hide" : "ctx_show");
  if (!opening || panel.firstChild) return;
  const source = state.cards.get(box.closest("[data-rule]").dataset.rule).rule.sources[Number(box.dataset.index)];
  try {
    const found = await api("/api/source", { doc_id: source.doc_id, quote: source.quoted_span });
    panel.innerHTML = found.found ? `<div class="context">${esc(found.before)}<mark>${esc(found.match)}</mark>${esc(found.after)}</div>`
      : `<p class="note review">${esc(t("quote_not_found"))}</p>`;
    const mark = $("mark", panel);
    if (mark) $(".context", panel).scrollTop = mark.offsetTop - 60;
  } catch (error) {
    panel.innerHTML = problem(error);
  }
}

function buildingSheet() {
  const a = state.data.address;
  const entered = state.data.entered_facts;
  const missing = `<em class="muted">${esc(t("not_in_record"))}</em>`;
  const mine = (name) => (name in entered ? ` <em class="mine">${esc(t("entered_by_you"))}</em>` : "");
  const geo = a.geocode || {};
  const gaps = ["year_built", "units"].filter((name) => a[name] == null || name in entered);
  openSheet(`<header class="sheet-head"><div><h2>${esc(t("building_record"))}</h2><p class="sheet-sub"><span class="plain-address">${esc(a.street_address)}</span></p></div>
      <button class="iconbtn" data-act="close" aria-label="${esc(t("close"))}" title="${esc(t("close"))}">${ICON.close}</button></header>
    <div class="sheet-body">
      <section><h3>${esc(t("b_where"))}</h3>${dl([
        [t("b_id"), esc(a.address_id)], [t("b_street"), esc(a.street_address)], [t("b_mailing"), esc(`${a.postal_city}, ${a.state} ${a.zip}`)],
        [t("b_city"), esc(a.legal_city || "—")], [t("b_how"), esc(t(a.resolved_by === "geocoder" ? "how_geocoder" : "how_postal"))],
        [t("b_matched"), esc(geo.matched_address)], [t("b_place"), esc([geo.place_name, geo.place_geoid].filter(Boolean).join(", "))],
      ])}</section>
      <section><h3>${esc(t("b_building"))}</h3>${dl([
        [t("b_year"), a.year_built != null ? esc(a.year_built) + mine("year_built") : missing],
        [t("b_units"), a.units != null ? esc(a.units) + mine("units") : a.units_at_least != null ? esc(t("at_least_units", { n: a.units_at_least })) : missing],
        [t("b_use"), esc([a.use_description, a.use_code].filter(Boolean).join(", "))],
      ])}
      ${gaps.length ? `<form id="facts" class="addfact"><p class="sub-head">${esc(t("add_title"))}</p><p class="hint">${esc(t("add_hint"))}</p>
        <div class="addfact-row">${gaps.map((name) => `<label>${esc(t(name === "year_built" ? "b_year" : "b_units"))}<input name="${name}" inputmode="numeric" pattern="\\d{1,4}" value="${esc(entered[name] ?? "")}"></label>`).join("")}
        <button class="btn primary">${esc(t("recheck"))}</button></div></form>` : ""}</section>
      <section><h3>${esc(t("b_record"))}</h3>${dl([[t("b_dataset"), esc(a.source_dataset)], [t("b_retrieved"), esc(a.retrieved_at)]])}</section>
    </div>`);
}

/* ---------- law changes ---------- */

async function renderChanges(request) {
  const view = $("#view");
  view.innerHTML = wait();
  const data = await api("/api/changes");
  if (request !== state.request) return;
  const cityOf = new Map(state.meta.addresses.map((a) => [a.address_id, a.legal_city || "—"]));
  view.innerHTML = `<header class="page-head"><div class="import-heading"><h1>${esc(t("tab_changes"))}</h1><a class="btn primary" href="#/imports">${esc(t("tab_imports"))}</a></div>${data.snapshot_note ? `<p class="note caution">${esc(t("snapshot_note", { d: showDate(data.as_of) }))}</p>` : ""}
    ${partial(data.extraction)}</header>
    ${data.tests.map((item) => {
      const dates = item.query_dates;
      const day = dates.as_of_after || dates.as_of;
      const affected = item.output.affected_address_ids;
      const flagged = new Set(item.output.conflict_flag_address_ids);
      const byCity = new Map(item.cities.map((row) => [row.city, []]));
      for (const id of affected) byCity.set(cityOf.get(id), [...(byCity.get(cityOf.get(id)) || []), id]);
      return `<article class="group case">
        <div class="side"><span class="case-id">${esc(item.test.test_id)}</span>
          <span class="case-dates">${esc(dates.as_of ? t("on_date", { a: showDate(dates.as_of) }) : t("compare_dates", { a: showDate(dates.as_of_before), b: showDate(dates.as_of_after) }))}</span></div>
        <div class="case-body">
          <h2>${esc(item.test.title)}</h2>
          <p class="asks"><b>${esc(t("case_asks"))}</b> ${esc(item.test.expected_behavior)}</p>
          ${item.missing_rules.length ? `<p class="note review">${esc(t("incomplete", { rules: item.missing_rules.join(", ") }))}</p>` : ""}
          <p class="finding"><span>${th("n_affected", { n: `<strong class="num">${affected.length}</strong>` })}</span><span>${th("n_flagged", { n: `<strong class="num">${flagged.size}</strong>` })}</span></p>
          ${item.transitions.length ? `<ul class="moves">${item.transitions.map((row) => `<li>${row.before ? st(row.before) + '<span class="to" aria-hidden="true">→</span>' : ""}${row.after ? st(row.after) : ""}
            <span class="cite">${esc(row.citation)}</span><span class="muted num">${esc(t("n_addresses", { n: row.addresses }))}</span></li>`).join("")}</ul>` : ""}
          ${item.cities.length ? `<table class="tally"><thead><tr><th>${esc(t("th_city"))}</th><th>${esc(t("th_affected"))}</th><th>${esc(t("th_flagged"))}</th></tr></thead>
            <tbody>${item.cities.map((row) => `<tr><th>${esc(cityName(row.city))}</th><td class="num">${esc(t("x_of_y", { a: row.affected, b: row.total }))}</td><td class="num">${row.flagged}</td></tr>`).join("")}</tbody></table>` : ""}
          ${affected.length ? `<details class="fold"><summary>${esc(t("fold_addresses", { n: affected.length }))}</summary>
            ${flagged.size ? `<p class="hint">${esc(t("ids_flagged"))}</p>` : ""}
            ${[...byCity].filter(([, ids]) => ids.length).map(([city, ids]) => `<p class="ids"><b>${esc(cityName(city))}</b>${ids.map((id) => `<a class="num${flagged.has(id) ? " flagged" : ""}" href="#/lookup?id=${esc(id)}&as_of=${esc(day)}">${esc(id)}</a>`).join("")}</p>`).join("")}</details>` : ""}
          <details class="fold"><summary>${esc(t("fold_rules"))}</summary>
            <ul class="plain">${Object.entries(item.rule_mapping).map(([external, rules]) => `<li><span class="num">${esc(external)}</span> ${rules.length ? rules.map((rule) => `<span class="cite">${esc(rule.citation)}</span> <span class="muted num">${esc(rule.team_rule_id)}</span>`).join("; ") : `<span class="row-flag">${esc(t("not_extracted"))}</span>`}</li>`).join("")}</ul>
            <p class="hint">${esc(item.output.notes)}</p></details>
        </div>
      </article>`;
    }).join("")}
    <p class="fine">${esc(data.disclaimer)}</p>`;
}

/* ---------- all rules ---------- */

async function renderRules(request) {
  const view = $("#view");
  view.innerHTML = wait();
  const data = await api("/api/rules");
  if (request !== state.request) return;
  const f = state.library;
  // State first, then its cities: the same order as the jurisdiction stack of an address.
  const places = STATE_ORDER.flatMap((code) => [code, ...[...new Set(data.rules.map((rule) => rule.jurisdiction))].filter((place) => place.endsWith(", " + code)).sort()]);
  const statuses = [...new Set(data.rules.map((rule) => rule.status))].sort();
  view.innerHTML = `<header class="page-head"><h1>${esc(t("tab_rules"))}</h1><p>${esc(t("rules_intro", { d: showDate(data.as_of) }))}</p>${data.snapshot_note ? `<p class="note caution">${esc(t("snapshot_note", { d: showDate(data.as_of) }))}</p>` : ""}
    ${partial(data.extraction)}</header>
    <div class="toolbar">
      <input id="lib-text" type="search" placeholder="${esc(t("search_rules"))}" aria-label="${esc(t("search_rules"))}">
      <select id="lib-place" aria-label="${esc(t("all_places"))}"><option value="">${esc(t("all_places"))}</option>${STATE_ORDER.map((code) => `<optgroup label="${esc(STATES[code])}">
        ${places.filter((place) => place === code || place.endsWith(", " + code)).map((place) => `<option value="${esc(place)}">${esc(place === code ? t("statewide") : cityName(place))}</option>`).join("")}</optgroup>`).join("")}</select>
      <select id="lib-category" aria-label="${esc(t("all_categories"))}"><option value="">${esc(t("all_categories"))}</option>${state.meta.categories.map((c) => `<option value="${c}">${esc(t("c_" + c))}</option>`).join("")}</select>
      <select id="lib-status" aria-label="${esc(t("all_statuses"))}"><option value="">${esc(t("all_statuses"))}</option>${statuses.map((s) => `<option value="${esc(s)}">${esc(t("s_" + s))}</option>`).join("")}</select>
      <span class="count num" id="lib-count"></span>
    </div>
    <div id="lib-list"></div>
    <p class="fine">${esc(data.disclaimer)}</p>`;
  const draw = () => {
    const tokens = f.text.toLowerCase().split(/\s+/).filter(Boolean);
    const rows = data.rules.filter((rule) => (!f.place || rule.jurisdiction === f.place) && (!f.category || rule.category === f.category) && (!f.status || rule.status === f.status)
      && tokens.every((token) => [rule.title, rule.citation, rule.requirement, rule.team_rule_id, rule.key_value].join(" ").toLowerCase().includes(token)));
    state.cards = new Map();
    $("#lib-count").textContent = t("n_rules", { n: rows.length });
    $("#lib-list").innerHTML = rows.length ? places.map((place) => {
      const inside = rows.filter((rule) => rule.jurisdiction === place);
      if (!inside.length) return "";
      const isState = place in STATES;
      return `<section class="place${isState ? "" : " city"}"><h2>${esc(isState ? STATES[place] : cityName(place))} <small>${esc(isState ? t("statewide") : STATES[place.slice(-2)])}, ${esc(t("n_rules", { n: inside.length }))}</small></h2>
        ${register(inside.map((rule) => ({ rule })))}</section>`;
    }).join("") : `<p class="none">${esc(t("no_rules_match"))}</p>`;
  };
  for (const name of ["text", "place", "category", "status"]) {
    const input = $("#lib-" + name);
    input.value = f[name];
    input.addEventListener("input", () => { f[name] = input.value; draw(); });
  }
  draw();
}

/* ---------- how it works ---------- */

async function renderPipeline(request) {
  const view = $("#view");
  view.innerHTML = wait();
  const d = await api("/api/pipeline");
  if (request !== state.request) return;
  const x = d.extraction;
  const answers = Object.values(d.lookups).reduce((a, b) => a + b, 0);
  const stage = (number, title, lines) => `<li class="group"><div class="side"><span class="stage-n num">${number}</span>${esc(t(title))}</div><div class="stage-body">${lines.map((line) => `<p>${esc(line)}</p>`).join("")}</div></li>`;
  const tally = (label, entries) => `<p class="counts"><span>${esc(t(label))}</span>${entries.map(([mark, n]) => `<span class="count-item"><b class="num">${count(n)}</b>${mark}</span>`).join("")}</p>`;
  view.innerHTML = `<header class="page-head"><h1>${esc(t("tab_pipeline"))}</h1></header>
    <ol class="stages">
      ${stage(1, "p1", [t("p1_a", { n: d.corpus.manifest_documents, m: d.corpus.manifest_with_text }), t("p1_b", { n: d.corpus.added_documents })])}
      ${stage(2, "p2", [t("p2_a", { n: x.packets_done, m: x.packets_total }), t("p2_b", { n: x.records_parsed, t: x.ran_at })])}
      ${stage(3, "p3", [t("p3_a", { n: x.accepted, m: x.rejected }), t("p3_b", { n: d.rules.total })])}
      ${stage(4, "p4", [t("p4_a", { n: d.addresses.total, a: d.addresses.resolved_by.geocoder || 0, b: d.addresses.resolved_by.postal_city_fallback || 0 })])}
      ${stage(5, "p5", [t("p5_a", { n: count(answers), d: showDate(d.as_of) })])}
    </ol>
    ${tally("rules_label", Object.entries(d.rules.by_status).map(([status, n]) => [st(status, "s"), n]))}
    ${tally("answers_label", RESULT_ORDER.filter((result) => d.lookups[result]).map((result) => [st(result), d.lookups[result]]))}
    <h2 class="sub-title">${esc(t("documents"))}</h2>
    <div class="scroll"><table class="docs"><thead><tr><th>${esc(t("th_doc"))}</th><th>${esc(t("th_place"))}</th><th>${esc(t("th_source"))}</th><th>${esc(t("th_text"))}</th><th>${esc(t("th_sections"))}</th><th>${esc(t("th_rules"))}</th></tr></thead>
      <tbody>${d.documents.map((doc) => `<tr class="${doc.no_text ? "dim" : ""}"><th class="num">${esc(doc.doc_id)}</th><td>${esc(doc.jurisdictions)}</td>
        <td>${safeUrl(doc.url) ? `<a href="${esc(doc.url)}" target="_blank" rel="noopener noreferrer">${esc(new URL(doc.url).hostname.replace(/^www\./, ""))}</a>` : "—"}<span class="muted">${esc(doc.source_type || "")}</span></td>
        <td>${esc(t(doc.no_text ? "no_text" : "has_text"))}${doc.origin !== "starter" ? `<span class="muted">${esc(t("extra_source"))}</span>` : ""}</td>
        <td class="num">${doc.packets || ""}</td><td class="num">${doc.rules || ""}</td></tr>`).join("")}</tbody></table></div>
    <p class="fine">${esc(d.disclaimer)}</p>`;
}

/* ---------- key figures ----------
   Money, rates, dates and legal time periods are what a reader scans for, so they carry
   their own ink (--figure).
   The pass runs over anything inserted into the page — lists, panels, dialogs — so no template
   has to remember to do it. Links, highlighted quotes and table counters are left alone. */
const FIGURE_MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiembre|Octubre|Noviembre|Diciembre|Ene|Feb|Mar|Abr|May|Jun|Jul|Ago|Sep|Oct|Nov|Dic";
const FIGURE = new RegExp([
  "\\$[\\d,]+(?:\\.\\d+)?",                                        // $1,000 · $446.00
  "\\d+(?:\\.\\d+)?\\s?%",                                         // 5% · 2.87%
  `(?:${FIGURE_MONTHS})\\.?\\s+\\d{1,2}(?:st|nd|rd|th)?,?\\s+\\d{4}`, // July 1, 2024
  `\\d{1,2}(?:\\s+de)?\\s+(?:${FIGURE_MONTHS})\\.?(?:\\s+de)?\\s+\\d{4}`, // 1 ene 2026
  "\\d{4}[-/]\\d{1,2}[-/]\\d{1,2}",                               // 2024-07-01
  "\\d{4}年\\d{1,2}月\\d{1,2}日",                                   // 2024年7月1日
  "\\d+(?:\\.\\d+)?\\s+(?:calendar\\s+|business\\s+|working\\s+)?(?:days|day|weeks|week|months|month|years|year|hours|hour)", // 30 days · 12 months
  "\\d+(?:\\.\\d+)?\\s+(?:días|día|semanas|semana|meses|mes|años|año|horas|hora)(?:\\s+(?:calendario|hábiles?))?", // 30 días · 12 meses
  "\\d+(?:\\.\\d+)?\\s*(?:个)?(?:日|天|周|星期|个月|月|年|小时)"       // 30天 · 12个月
].join("|"), "gi");
const FIGURE_SKIP = "a, button, h1, mark, .hl, .num, script, style, select, option, textarea, code, .fig";

let markingFigures = false;
function markFigures(root) {
  if (markingFigures || !root || root.nodeType !== 1) return;
  const nodes = [];
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      const parent = node.parentElement;
      if (!parent || parent.closest(FIGURE_SKIP) || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
      FIGURE.lastIndex = 0;
      return FIGURE.test(node.nodeValue) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
    },
  });
  while (walker.nextNode()) nodes.push(walker.currentNode);
  if (!nodes.length) return;
  markingFigures = true;
  for (const node of nodes) {
    const text = node.nodeValue;
    const frag = document.createDocumentFragment();
    let last = 0;
    FIGURE.lastIndex = 0;
    let hit;
    while ((hit = FIGURE.exec(text))) {
      const before = hit.index ? text[hit.index - 1] : "";
      const after = text[hit.index + hit[0].length] || "";
      // A figure glued to a word or to URL escapes ("2025-12-02%20") is an identifier, not an amount.
      if (/[\w%]/.test(before) || /[0-9%]/.test(after)) continue;
      if (hit.index > last) frag.append(text.slice(last, hit.index));
      const span = document.createElement("span");
      span.className = "fig";
      span.textContent = hit[0];
      frag.append(span);
      last = hit.index + hit[0].length;
    }
    if (!last) continue;
    if (last < text.length) frag.append(text.slice(last));
    node.replaceWith(frag);
  }
  markingFigures = false;
}

new MutationObserver((records) => {
  for (const record of records) {
    for (const added of record.addedNodes) {
      markFigures(added.nodeType === 1 ? added : added.parentElement);
    }
  }
}).observe(document.body, { childList: true, subtree: true });

/* ---------- start ---------- */

const importsPage = createImportsPage({lang: () => state.lang, esc, t, st});
async function render() {
  importsPage.stop();
  closeSummaryPopover();
  state.summaryController?.abort(); state.summaryController = null;
  $("#law-summary")?.remove();
  chrome();
  const { tab, params } = route();
  const request = ++state.request;
  const view = $("#view");
  if (tab !== state.last.tab) view.innerHTML = "";
  if (tab !== state.last.tab || params.id !== state.last.id) window.scrollTo(0, 0);
  state.last = { tab, id: params.id };
  try {
    if (tab === "lookup") await renderLookup(params, request);
    if (tab === "changes") await renderChanges(request);
    if (tab === "rules") await renderRules(request);
    if (tab === "pipeline") await renderPipeline(request);
    if (tab === "imports") await importsPage.render(params, () => request === state.request && route().tab === 'imports');
  } catch (error) {
    if (request === state.request) view.innerHTML = problem(error);
  }
}

document.addEventListener("click", (event) => {
  if (!event.target.closest(".summary-citation, #summary-reference-popover")) closeSummaryPopover();
  if (!event.target.closest("#finder")) closeFinder();
  if (!event.target.closest(".datewrap")) closeDatePop();
  if (event.target === $("#sheet")) $("#sheet").close();
  const target = event.target.closest("[data-act]");
  if (!target) return;
  const act = target.dataset.act;
  if (act === "filter") {
    state.filter = state.filter === target.dataset.result ? "" : target.dataset.result;
    applyFilter();
    // The list just changed length under a bar that stays in view; start reading it from its top.
    if ($(".answer").getBoundingClientRect().top < 0) $(".answer").scrollIntoView();
  }
  if (act === "date") { const pop = $("#date-pop"); pop.hidden = !pop.hidden; target.setAttribute("aria-expanded", String(!pop.hidden)); }
  if (act === "day") relook({ as_of: target.dataset.day });
  if (act === "address" && target.dataset.id) chooseAddress(target.dataset.id);
  if (act === "scope") { $("#sheet").close(); scopeFinder(target.dataset.scope); }
  if (act === "scope-clear") { state.finder.scope = ""; drawFinder(); }
  if (act === "sheet") ruleSheet(target.closest("[data-rule]").dataset.rule, target.dataset.focus);
  if (act === "summary-source") summaryReferencePreview(target);
  if (act === "summary-dismiss") closeSummaryPopover(true);
  if (act === "summary-details") {closeSummaryPopover(); ruleSheet(target.dataset.rule, "source", Number(target.dataset.sourceIndex));}
  if (act === "summary-retry" && state.data) void startSummary(route().params, state.request, state.data);
  if (act === "building") buildingSheet();
  if (act === "context") showContext(target.closest(".source"));
  if (act === "remove-entries") relook({ year_built: "", units: "" });
  if (act === "close") $("#sheet").close();
});
document.addEventListener("change", (event) => {
  if (event.target.id === "date-input" && isDay(event.target.value)) relook({ as_of: event.target.value });
});
document.addEventListener("submit", (event) => {
  if (event.target.id !== "facts") return;
  event.preventDefault();
  $("#sheet").close();
  relook(Object.fromEntries(new FormData(event.target)));
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && state.summaryPopoverAnchor) {event.preventDefault(); closeSummaryPopover(true);}
  if (event.key === "Escape") closeDatePop();
});
document.addEventListener("scroll", (event) => {
  const pop = $("#summary-reference-popover");
  if (pop && !pop.contains(event.target)) closeSummaryPopover();
}, true);
window.addEventListener("resize", () => closeSummaryPopover());
$("#lang").addEventListener("change", (event) => {
  state.lang = event.target.value;
  try { localStorage.setItem("lang", state.lang); } catch (error) { /* private window */ }
  $("#view").innerHTML = "";
  render();
});
window.addEventListener("pagehide", () => {state.summaryController?.abort(); closeSummaryPopover();});
window.addEventListener("pageshow", (event) => {if (event.persisted && state.meta) void render();});
window.addEventListener("hashchange", () => {
  if ($("#sheet").open) $("#sheet").close();
  render();
});

(async () => {
  chrome();
  try {
    state.meta = await api("/api/meta");
    const rank = (a) => STATE_ORDER.indexOf(a.state) + "|" + (a.legal_city || "~") + "|" + a.address_id;
    state.meta.addresses.sort((x, y) => (rank(x) < rank(y) ? -1 : 1));
    for (const a of state.meta.addresses) a.hay = [a.address_id, a.street_address, a.postal_city, a.legal_city, STATES[a.state], a.zip].join(" ").toLowerCase();
    await render();
  } catch (error) {
    $("#view").innerHTML = problem(error);
  }
})();
