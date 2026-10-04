import assert from 'node:assert/strict';
import {test} from 'node:test';
import {LookupEngine} from '../../dist/lookup/engine.js';

test('RSO value expiry retains coverage decisions and marks the missing current percentage', () => {
  const engine = LookupEngine.fromFiles();
  const rso = engine.by_id['r-0154'];
  assert.equal(rso.valid_through, null);
  const ids = Object.keys(engine.addresses).filter(id => engine.addresses[id].legal_city === 'Los Angeles, CA');
  assert.equal(ids.length, 80);
  const counts = {};
  for (const id of ids) {
    const before = engine.lookup(id, '2026-06-30').find(r => r.team_rule_id === 'r-0154');
    const [rows, trace] = engine.evaluate(id, '2026-07-01');
    const after = rows.find(r => r.team_rule_id === 'r-0154');
    assert.equal(after?.result, before?.result);
    if (after) {
      assert.match(after.explanation, /current annual allowable rent increase percentage is not stated/);
      assert.doesNotMatch(before.explanation, /current annual allowable rent increase percentage is not stated/);
      assert.ok(trace.rules.find(r => r.team_rule_id === 'r-0154').missing_facts.some(f => f.field === 'current_value'));
      counts[after.result] = (counts[after.result] || 0) + 1;
    }
  }
  assert.deepEqual(counts, {applies: 47, unknown: 33});
  const exported = engine.exportedRules('2026-10-01').find(r => r.team_rule_id === 'r-0154');
  assert.equal(exported.value_status, 'missing_current_value');
  assert.doesNotMatch(exported.key_value, /3%/);
  assert.match(exported.requirement, /current annual allowable rent increase percentage is not stated/);
  assert.equal(engine.exportedRules('2026-06-30').find(r => r.team_rule_id === 'r-0154').value_status, undefined);
  // Genuine rule expiry still excludes a rule.
  const expired = {...rso, value_valid_through: null, valid_through: '2026-06-30'};
  const oldEngine = new LookupEngine([expired], engine.addresses, [], []);
  for (const id of ids) assert.equal(oldEngine.lookup(id, '2026-07-01').length, 0);
});

test('web rule details mark value gaps, and the correction cannot replace a new percentage', async () => {
  const {ruleView} = await import('../../dist/web/server.js');
  const {matches} = await import('../../dist/lookup/common.js');
  const {readJson} = await import('../../dist/util.js');
  const {ROOT} = await import('../../dist/lookup/common.js');
  const correction = readJson(ROOT + '/lookup/coverage_facts.json').find(r => r.id === 'la-rso-annual-value-period');
  const raw = readJson(ROOT + '/work/rules_enriched.json').find(r => r.team_rule_id === 'r-0154');
  assert.equal(matches(raw, correction.match), true);
  assert.equal(matches({...raw, key_value: 'new annual percentage'}, correction.match), false);
  assert.equal(matches({...raw, valid_through: '2027-06-30'}, correction.match), false);
  const engine = LookupEngine.fromFiles();
  const view = ruleView(engine.by_id['r-0154'], '2026-07-01', engine, {});
  assert.equal(view.value_status, 'missing_current_value');
  assert.match(view.requirement, /current annual allowable rent increase percentage is not stated/);
  assert.equal(ruleView(engine.by_id['r-0154'], '2026-06-30', engine, {}).value_status, undefined);
});
