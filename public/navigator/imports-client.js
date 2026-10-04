export const IMPORT_LABELS = {en: 'Parse law text', es: 'Analizar texto legal', zh: '解析法规正文'};

const WORDS = {
  en: {
    title: 'Parse law changes', lead: 'Paste a law’s full text to see which rules it adds and which addresses it changes.',
    body: 'Law text', body_hint: 'Paste the complete text, or upload a UTF-8 .txt file. A URL alone is not accepted.', upload: 'Upload a .txt file',
    start: 'Start parsing', starting: 'Submitting…', missing: 'Please submit law text; a URL alone is not accepted.', bad_file: 'Please select a UTF-8 .txt file.', bad_utf8: 'The file is not readable UTF-8 text.', no_model: 'The server needs an extraction model configured.',
    history: 'Submitted texts', empty: 'No texts submitted yet.', back: 'Back to law changes', another: 'Submit another text',
    preparing: 'Saving the text', extracting: 'Reading and extracting rules', checking: 'Checking rules and source quotes', comparing: 'Checking address impact', ready: 'Parsing complete', failed: 'Parsing did not finish', interrupted: 'Parsing was interrupted', applied: 'Results in use',
    progress: '{done} of {total} text sections checked', live: 'You can leave this page and return to the saved task.', refresh: 'Refresh status', poll_error: 'Could not refresh the task: {msg}.',
    raw: 'View the submitted text', extra: 'User-supplied source, outside the official distributed corpus.', preview: 'Extracted rules', details: 'View source quotes and changes to existing rules', before: 'Previously recorded', after: 'Extracted from this text', absent: 'No rule previously recorded', no_answer: 'Not in the results',
    apply: 'Use these results', applied_hint: 'Address queries now use these results with the dates read from the text.', recompare: 'Refresh impact', retry: 'Continue parsing',
    covered: 'Covers {n} sample addresses as of {day}.', future: 'Not yet effective on {day}. From {from}, it may cover {n} sample addresses.', proposed: 'Still a proposal. If enacted, it may cover {n} sample addresses.', failed_law: 'Failed or withdrawn. Its affected list is empty.', uncertain: 'Status or coverage needs checking; {n} potentially covered sample addresses.',
    cases: 'Track changes using the challenge examples', dates: 'Compare {before} → {after}', on_day: 'As of {day}', affected: '{n} affected addresses', review: '{n} addresses need review', ids: 'View affected addresses', missing_rules: 'Some related rules have not been extracted; this comparison is incomplete.',
    case_T1: 'California law takes effect', case_T2: 'City laws stay within each city', case_T3: 'NJ law is enacted but takes effect later', case_T4: 'Massachusetts bills are still proposals', case_T5: 'Failed Massachusetts ballot measure has no rent cap',
    record_changes: 'Changes to recorded answers as of {day} ({n} addresses)', records_hint: 'This compares the stored results before and after this submission. A change in a record does not mean the law is in force.', none: 'No recorded address answers change on this date.', city: 'City', addresses: 'Changed / total', flagged: 'Needs review',
    rules: 'Extracted rules ({n})', quote: 'Checked quote from the submitted text', preserve: 'Other categories of the same law retain their previous rules.', warn: 'Notes to check', unchanged: 'No rule facts changed.',
    f_requirement: 'What the rule says', f_key_value: 'Key figure', f_coverage_conditions: 'Who is covered', f_exemptions: 'Exemptions', f_penalty: 'Penalty', f_effective_date: 'Effective date', f_valid_through: 'Valid through', f_lifecycle: 'Law status', f_interaction: 'Relation to other laws',
    enacted: 'Enacted', pending_bill: 'Proposed, not law', not_stated: 'Not stated in the text', source_record: 'Source and date',
  },
  es: {
    title: 'Analizar cambios legales', lead: 'Pegue el texto completo de una ley para ver qué normas añade y qué direcciones cambia.',
    body: 'Texto legal', body_hint: 'Pegue el texto completo o cargue un archivo .txt en UTF-8. No se acepta solo una URL.', upload: 'Cargar archivo .txt',
    start: 'Iniciar análisis', starting: 'Enviando…', missing: 'Envíe el texto legal; no se acepta solo una URL.', bad_file: 'Seleccione un archivo .txt en UTF-8.', bad_utf8: 'El archivo no es texto UTF-8 legible.', no_model: 'Es necesario configurar el modelo en el servidor.',
    history: 'Textos enviados', empty: 'Aún no hay textos enviados.', back: 'Volver a cambios legales', another: 'Enviar otro texto',
    preparing: 'Guardando el texto', extracting: 'Leyendo y extrayendo normas', checking: 'Comprobando normas y citas', comparing: 'Comprobando direcciones afectadas', ready: 'Análisis completo', failed: 'El análisis no terminó', interrupted: 'Análisis interrumpido', applied: 'Resultados en uso',
    progress: '{done} de {total} secciones comprobadas', live: 'Puede salir de esta página y volver a la tarea guardada.', refresh: 'Actualizar estado', poll_error: 'No se pudo actualizar la tarea: {msg}.',
    raw: 'Ver el texto enviado', extra: 'Fuente aportada por el usuario, fuera del corpus oficial.', preview: 'Normas extraídas', details: 'Ver citas y cambios a las normas existentes', before: 'Registro anterior', after: 'Extraído de este texto', absent: 'No había norma registrada', no_answer: 'No figura en los resultados',
    apply: 'Usar estos resultados', applied_hint: 'Las consultas usan estos resultados y las fechas extraídas del texto.', recompare: 'Actualizar impacto', retry: 'Continuar análisis',
    covered: 'Cubre {n} direcciones de muestra al {day}.', future: 'Aún no vigente al {day}. Desde {from}, podría cubrir {n} direcciones.', proposed: 'Sigue siendo una propuesta. Si se aprueba, podría cubrir {n} direcciones.', failed_law: 'Rechazada o retirada. La lista de afectadas está vacía.', uncertain: 'Hay que comprobar el estado o alcance; {n} direcciones potencialmente cubiertas.',
    cases: 'Seguir los cambios con los ejemplos del reto', dates: 'Comparar {before} → {after}', on_day: 'Al {day}', affected: '{n} direcciones afectadas', review: '{n} direcciones requieren revisión', ids: 'Ver direcciones afectadas', missing_rules: 'Faltan algunas normas relacionadas; la comparación está incompleta.',
    case_T1: 'Entra en vigor la ley de California', case_T2: 'Las normas municipales se limitan a cada ciudad', case_T3: 'La ley de NJ está aprobada, pero entra en vigor después', case_T4: 'Los proyectos de Massachusetts siguen pendientes', case_T5: 'La propuesta rechazada de Massachusetts no limita el alquiler',
    record_changes: 'Cambios de los registros al {day} ({n} direcciones)', records_hint: 'Compara los registros antes y después de este envío. Un cambio de registro no significa que la ley esté vigente.', none: 'No cambian las respuestas registradas en esta fecha.', city: 'Ciudad', addresses: 'Cambiadas / total', flagged: 'Requiere revisión',
    rules: 'Normas extraídas ({n})', quote: 'Cita comprobada del texto enviado', preserve: 'Las otras categorías de la misma ley conservan sus normas anteriores.', warn: 'Notas para revisar', unchanged: 'No cambiaron los hechos de la norma.',
    f_requirement: 'Qué dice la norma', f_key_value: 'Cifra clave', f_coverage_conditions: 'A quién cubre', f_exemptions: 'Excepciones', f_penalty: 'Sanción', f_effective_date: 'Fecha de vigencia', f_valid_through: 'Válido hasta', f_lifecycle: 'Estado de la ley', f_interaction: 'Relación con otras leyes',
    enacted: 'Aprobada', pending_bill: 'Propuesta, no es ley', not_stated: 'No indicado en el texto', source_record: 'Fuente y fecha',
  },
  zh: {
    title: '解析法规变更', lead: '粘贴法规全文，查看它新增哪些规则、改变哪些地址的结论。',
    body: '法规正文', body_hint: '粘贴完整正文，或上传 UTF-8 编码的 .txt 文件。不能只提交网址。', upload: '上传 .txt 文件',
    start: '开始解析', starting: '正在提交…', missing: '必须提交法规正文，不能只提交网址。', bad_file: '请选择 UTF-8 编码的 .txt 文件。', bad_utf8: '文件不是可读的 UTF-8 文本。', no_model: '服务端尚未配置提取模型。',
    history: '已提交的正文', empty: '还没有提交记录。', back: '返回法律变更', another: '提交另一份正文',
    preparing: '保存正文', extracting: '智能体正在读取正文', checking: '检查规则和原文引用', comparing: '判断地址影响', ready: '解析完成', failed: '本次解析未完成', interrupted: '解析已中断', applied: '已使用解析结果',
    progress: '已检查 {total} 个正文分段中的 {done} 个', live: '离开页面不会取消任务，可以从提交记录继续查看。', refresh: '刷新进度', poll_error: '暂时无法刷新任务：{msg}。',
    raw: '查看提交的正文', extra: '用户提交的来源，不属于官方分发的比赛语料。', preview: '智能体识别的结果', details: '展开原文引用和已有规则的变化', before: '原来记录的规则', after: '本次正文提取的规则', absent: '原来没有这条规则', no_answer: '未列入查询结果',
    apply: '使用解析结果', applied_hint: '地址查询已使用本次结果，按正文中的日期判断。', recompare: '刷新影响结果', retry: '继续解析',
    covered: '截至 {day}，覆盖 {n} 个样本地址。', future: '截至 {day} 尚未生效。从 {from} 起，可能覆盖 {n} 个样本地址。', proposed: '仍是提案。如果通过，可能覆盖 {n} 个样本地址。', failed_law: '未通过或已撤回。受影响列表为空，不作为现行规则。', uncertain: '状态或覆盖范围需要确认，可能涉及 {n} 个样本地址。',
    cases: '按题目示例追踪变更', dates: '比较 {before} → {after}', on_day: '截至 {day}', affected: '受影响地址 {n} 个', review: '需复核地址 {n} 个', ids: '展开受影响地址', missing_rules: '相关法规尚未全部提取，这份比较仍不完整。',
    case_T1: '加州法规到了生效日期', case_T2: '城市法规只覆盖各自的城市', case_T3: '新泽西法规已通过，将来才生效', case_T4: '麻州法案尚未通过', case_T5: '麻州公投提案失败，不产生涨租上限',
    record_changes: '截至 {day} 的记录修正（{n} 个地址）', records_hint: '这里比较提交前后的查询记录；记录发生变化，不代表法规已经生效。', none: '这个日期的地址查询记录没有变化。', city: '城市', addresses: '记录变化 / 总数', flagged: '需要复核',
    rules: '提取出的规则（{n}）', quote: '已核对的正文引用', preserve: '同一法规中未在本次正文出现的其他类别，继续保留原有规则。', warn: '需要核对的提示', unchanged: '规则事实没有变化。',
    f_requirement: '规则内容', f_key_value: '关键数字', f_coverage_conditions: '覆盖范围', f_exemptions: '例外', f_penalty: '处罚', f_effective_date: '生效日期', f_valid_through: '有效至', f_lifecycle: '法规状态', f_interaction: '与其他法规的关系',
    enacted: '已通过', pending_bill: '提案，尚未通过', not_stated: '正文未说明', source_record: '来源与获取日期',
  },
};

export function createImportsPage(context) {
  const esc = context.esc;
  const tr = (key, values = {}) => (WORDS[context.lang()][key] || WORDS.en[key] || key).replace(/\{(\w+)\}/g, (_, k) => values[k] ?? '');
  const draft = {text: ''};
  let timer, generation = 0;
  const view = () => document.querySelector('#view');
  const $ = selector => view().querySelector(selector);
  async function request(url, body) {
    const response = await fetch(url, body === undefined ? {} : {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
    const data = await response.json(); if (!response.ok) throw new Error(data.error || response.statusText);
    // Online: extraction runs in its own request, kept open while this page is.
    if (body !== undefined && (url === '/api/imports' || url.endsWith('/retry'))) fetch('/api/imports/' + data.id + '/run', {method: 'POST'}).catch(() => {});
    return data;
  }
  function formHtml(data) {
    return `<form id="law-import-form" class="import-form">
      <label class="import-field import-body">${esc(tr('body'))}<textarea name="text" rows="10" required aria-describedby="import-body-hint">${esc(draft.text)}</textarea><span id="import-body-hint" class="hint">${esc(tr('body_hint'))}</span></label>
      <label class="import-upload">${esc(tr('upload'))}<input id="import-text-file" type="file" accept=".txt,text/plain"><span id="import-file-name" class="hint"></span></label>
      <p id="import-form-error" class="note review" role="alert" hidden></p>${!data.configured ? `<p class="note caution">${esc(tr('no_model'))}</p>` : ''}
      <button class="btn primary" type="submit" ${data.configured ? '' : 'disabled'}>${esc(tr('start'))}</button>
    </form>`;
  }
  const historyHtml = data => `<section class="import-history"><h2>${esc(tr('history'))}</h2>${data.jobs.length ? `<ul>${data.jobs.map(j => `<li><a data-job-title="${esc(j.id)}" href="#/imports?id=${esc(j.id)}">${esc(j.title)}</a><span data-job-status="${esc(j.id)}">${esc([j.jurisdiction, tr(j.status === 'running' ? j.stage : j.status)].filter(Boolean).join(' · '))}</span><time datetime="${esc(j.created_at)}">${esc(new Date(j.created_at).toLocaleString(context.lang()))}</time></li>`).join('')}</ul>` : `<p class="muted">${esc(tr('empty'))}</p>`}</section>`;
  function bindForm(alive) {
    const form = $('#law-import-form'), errorBox = $('#import-form-error');
    const error = message => {errorBox.hidden = false; errorBox.textContent = message;};
    form.addEventListener('input', () => Object.assign(draft, Object.fromEntries(new FormData(form))));
    $('#import-text-file').addEventListener('change', async event => {
      const file = event.target.files[0]; if (!file) return;
      if (!/\.txt$/i.test(file.name)) {error(tr('bad_file')); event.target.value = ''; return;}
      try {
        const text = new TextDecoder('utf-8', {fatal: true}).decode(await file.arrayBuffer());
        if (text.includes('\0')) throw new Error(); if (!alive()) return;
        draft.text = text; form.elements.text.value = text; $('#import-file-name').textContent = file.name; errorBox.hidden = true;
      } catch {if (alive()) error(tr('bad_utf8'));}
    });
    form.addEventListener('submit', async event => {
      event.preventDefault(); Object.assign(draft, Object.fromEntries(new FormData(form)));
      if (!draft.text.trim() || draft.text.trim().split(/\s+/).every(word => /^https?:\/\/\S+$/i.test(word))) {error(tr('missing')); return;}
      const button = form.querySelector('[type=submit]'); button.disabled = true; button.textContent = tr('starting'); errorBox.hidden = true;
      try {const job = await request('/api/imports', draft); draft.text = ''; if (alive()) location.hash = '#/imports?id=' + job.id;}
      catch (e) {if (alive()) error(e.message);} finally {button.disabled = false; button.textContent = tr('start');}
    });
  }
  function ruleDetails(rule, changed = []) {
    if (!rule) return `<p class="muted">${esc(tr('absent'))}</p>`;
    return `<p class="cite">${esc(rule.citation)}</p><dl class="import-facts">${['lifecycle', 'requirement', 'key_value', 'coverage_conditions', 'exemptions', 'penalty', 'effective_date', 'valid_through', 'interaction'].map(k => {
      const value = k === 'lifecycle' ? tr(['failed', 'withdrawn'].includes(rule[k]) ? 'failed_law' : rule[k] || 'not_stated') : rule[k] ?? tr('not_stated');
      return `<div class="${changed.includes(k) ? 'changed' : ''}"><dt>${esc(tr('f_' + k))}</dt><dd>${esc(typeof value === 'object' ? JSON.stringify(value) : value)}</dd></div>`;
    }).join('')}</dl><p class="hint">${esc(tr('source_record'))}: ${esc(rule.source_url || '—')} · ${esc(rule.retrieved || '—')}</p><p class="hint">${esc(tr('quote'))}</p><blockquote class="import-quote">${esc(rule.quoted_span || '')}</blockquote>`;
  }
  function idsHtml(ids, day, applied) {
    return ids.length ? `<details class="fold"><summary>${esc(tr('ids'))} (${ids.length})</summary><p class="import-ids">${ids.map(id => applied ? `<a href="#/lookup?id=${esc(id)}&as_of=${esc(day)}">${esc(id)}</a>` : `<span>${esc(id)}</span>`).join(' ')}</p></details>` : '';
  }
  function scopeText(rule, scope, asOf) {
    const n = scope?.affected_address_ids.length ?? 0;
    if (['failed', 'withdrawn'].includes(rule.lifecycle)) return tr('failed_law');
    if (rule.lifecycle === 'pending_bill') return tr('proposed', {n});
    if (rule.status === 'not_yet_effective') return tr('future', {day: asOf, from: rule.effective_date, n});
    if (rule.status === 'in_force') return tr('covered', {day: asOf, n});
    return tr('uncertain', {n});
  }
  function answerHtml(row) {
    return row ? `<p>${context.st(row.result)} ${esc(row.rule.key_value || '')}</p><p>${esc(row.rule.requirement)}</p><p class="hint">${esc(row.explanation)}</p>` : `<p class="muted">${esc(tr('no_answer'))}</p>`;
  }
  function previewHtml(data) {
    const p = data.preview; if (!p) return '';
    const applied = data.job.status === 'applied';
    return `<section class="import-preview"><h2>${esc(tr('preview'))}</h2>${p.rules.map(r => {
      const scope = p.rule_scopes?.find(s => s.team_rule_id === r.after.team_rule_id);
      return `<article class="import-rule"><h3>${esc(r.after.title || r.after.citation)}</h3><p class="hint">${esc(r.after.jurisdiction)} · ${esc(context.t('c_' + r.after.category))}</p><p>${context.st(r.after.status, 's')}${r.after.effective_date ? ` · ${esc(tr('f_effective_date'))} ${esc(r.after.effective_date)}` : ''}</p><p class="import-key">${esc(r.after.requirement)}</p>${r.after.key_value ? `<p>${esc(r.after.key_value)}</p>` : ''}<p class="note">${esc(scopeText(r.after, scope, p.as_of))}</p>${scope ? idsHtml(scope.affected_address_ids, scope.as_of, applied) : ''}
        <details class="fold"><summary>${esc(tr('details'))}</summary><div class="import-compare"><section><h4>${esc(tr('before'))}</h4>${ruleDetails(r.before, r.changed_fields)}</section><section><h4>${esc(tr('after'))}</h4>${ruleDetails(r.after, r.changed_fields)}</section></div>${!r.changed_fields.length ? `<p class="hint">${esc(tr('unchanged'))}</p>` : ''}</details></article>`;
    }).join('')}
      ${p.change_cases?.length ? `<h3>${esc(tr('cases'))}</h3>${p.change_cases.map(c => `<article class="import-case"><h4>${esc(c.test.test_id)} · ${esc(tr('case_' + c.test.test_id))}</h4><p>${esc(c.test.type === 'as_of' ? tr('dates', {before: c.query_dates.as_of_before, after: c.query_dates.as_of_after}) : tr('on_day', {day: c.query_dates.as_of}))}</p>${c.transitions.map(change => `<p>${context.st(change.before)} → ${context.st(change.after)} · ${change.addresses}</p>`).join('')}<p>${esc(tr('affected', {n: c.affected_address_ids.length}))} · ${esc(tr('review', {n: c.conflict_flag_address_ids.length}))}</p>${c.missing_rules.length ? `<p class="note caution">${esc(tr('missing_rules'))}</p>` : ''}${idsHtml(c.affected_address_ids, c.query_dates.as_of_after || c.query_dates.as_of, applied)}</article>`).join('')}` : ''}
      ${p.preserved_rules.length ? `<p class="hint">${esc(tr('preserve'))}</p>` : ''}${p.warnings.length ? `<details class="fold import-warnings"><summary>${esc(tr('warn'))} (${p.warnings.length})</summary><ul>${p.warnings.map(w => `<li>${esc(w)}</li>`).join('')}</ul></details>` : ''}
      <details class="fold import-records"><summary>${esc(tr('record_changes', {day: p.as_of, n: p.affected.length}))}</summary><p class="hint">${esc(tr('records_hint'))}</p>${!p.affected.length ? `<p>${esc(tr('none'))}</p>` : ''}<div class="scroll"><table class="tally"><thead><tr><th>${esc(tr('city'))}</th><th>${esc(tr('addresses'))}</th><th>${esc(tr('flagged'))}</th></tr></thead><tbody>${p.cities.map(c => `<tr><th>${esc(c.city)}</th><td>${c.affected} / ${c.total}</td><td>${c.flagged}</td></tr>`).join('')}</tbody></table></div>${p.affected.map(a => `<details class="import-address"><summary>${esc(a.street_address || a.address_id)} · ${esc(a.city)} ${a.flagged ? `<span class="row-flag">${esc(tr('flagged'))}</span>` : ''}</summary>${a.changes.map(c => `<div class="import-compare"><section><h4>${esc(tr('before'))}</h4>${answerHtml(c.before)}</section><section><h4>${esc(tr('after'))}</h4>${answerHtml(c.after)}</section></div>`).join('')}</details>`).join('')}</details>
    </section>`;
  }
  function detailHtml(data) {
    const {job, input} = data;
    return `<section class="import-job"><div id="import-state" role="status" aria-live="polite"><p class="import-stage">${esc(tr(job.status === 'running' ? job.stage : job.status))}</p><p class="hint">${esc(tr('progress', job.progress))}</p>${job.status === 'running' ? `<p class="hint">${esc(tr('live'))}</p>` : ''}</div>${job.error ? `<p class="note review" role="alert">${esc(job.error)}</p>` : ''}<p id="import-action-error" class="note review" role="alert" hidden></p>
      ${job.status === 'applied' ? `<p class="note">${esc(tr('applied_hint'))}</p>` : ''}${job.status === 'ready' || job.status === 'applied' ? previewHtml(data) : ''}
      <p class="actions">${job.status === 'running' ? `<button class="btn" data-import-action="refresh">${esc(tr('refresh'))}</button>` : ''}${job.status === 'failed' ? `<button class="btn" data-import-action="retry">${esc(tr('retry'))}</button>` : ''}${job.status === 'ready' ? `<button class="btn primary" data-import-action="apply">${esc(tr('apply'))}</button><button class="btn" data-import-action="preview">${esc(tr('recompare'))}</button>` : ''}</p>
      <details class="fold"><summary>${esc(tr('raw'))}</summary><p class="hint">${esc(tr('extra'))}</p>${input.source_url ? `<p class="hint">${esc(input.source_url)}</p>` : ''}<pre class="import-raw">${esc(input.text)}</pre></details>
    </section>`;
  }
  async function render(params, isCurrent) {
    const current = ++generation; clearTimeout(timer);
    const alive = () => current === generation && isCurrent();
    const list = await request('/api/imports'); if (!alive()) return;
    const detail = params.id ? await request('/api/imports/' + encodeURIComponent(params.id)) : null; if (!alive()) return;
    view().innerHTML = `<header class="page-head"><div class="import-heading"><h1>${esc(tr('title'))}</h1><a class="btn" href="#/changes">${esc(tr('back'))}</a></div><p>${esc(tr('lead'))}</p></header>${detail ? `<p class="actions"><a class="btn" href="#/imports">${esc(tr('another'))}</a></p><div id="import-detail">${detailHtml(detail)}</div>` : formHtml(list)}${historyHtml(list)}`;
    if (!detail) {bindForm(alive); return;}
    const url = '/api/imports/' + detail.job.id;
    let refreshSequence = 0;
    const refresh = async () => {
      const sequence = ++refreshSequence;
      const updated = await request(url); if (!alive() || sequence !== refreshSequence) return;
      const old = detail.job; Object.assign(detail, updated);
      if (updated.job.status === 'running' && old.status === 'running') $('#import-state').innerHTML = `<p class="import-stage">${esc(tr(updated.job.stage))}</p><p class="hint">${esc(tr('progress', updated.job.progress))}</p><p class="hint">${esc(tr('live'))}</p>`;
      else $('#import-detail').innerHTML = detailHtml(updated);
      const historyStatus = $(`[data-job-status="${updated.job.id}"]`), historyTitle = $(`[data-job-title="${updated.job.id}"]`);
      if (historyStatus) historyStatus.textContent = [updated.job.jurisdiction, tr(updated.job.status === 'running' ? updated.job.stage : updated.job.status)].filter(Boolean).join(' · ');
      if (historyTitle) historyTitle.textContent = updated.job.title;
      if (updated.job.status === 'running') timer = setTimeout(poll, 1500);
    };
    const poll = () => refresh().catch(error => {if (alive()) {const box = $('#import-action-error'); box.hidden = false; box.textContent = tr('poll_error', {msg: error.message}); timer = setTimeout(poll, 3000);}});
    $('#import-detail').addEventListener('click', async event => {
      const button = event.target.closest('[data-import-action]'); if (!button) return;
      const action = button.dataset.importAction; button.disabled = true; refreshSequence++; clearTimeout(timer);
      try {if (action !== 'refresh') await request(url + '/' + action, {}); await refresh();}
      catch (error) {if (alive()) {const box = $('#import-action-error'); box.hidden = false; box.textContent = error.message;}}
      finally {button.disabled = false;}
    });
    if (detail.job.status === 'running') timer = setTimeout(poll, 1500);
  }
  return {render, stop() {generation++; clearTimeout(timer);}};
}
