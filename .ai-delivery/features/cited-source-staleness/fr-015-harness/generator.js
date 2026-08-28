#!/usr/bin/env node
'use strict';

// Consumers: the operator and runner.js, before generation and at run preflight.

const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');

const HARNESS_DIR = __dirname;
const BASE_PATH = path.resolve(HARNESS_DIR, '../../../conventions.md');
const FIXTURE_DIR = path.join(HARNESS_DIR, 'fixtures');
const BASE_MD5 = '62de1a25fbf1e3896645278f1d2609cc';
const BASE_DATE = '2026-08-12';
const FIXTURE_CONSUMER_LINE = '# Consumer: runner.js';
const PLACEHOLDER_TOKEN = '<READ-EVENT>:';
const OLD_DATES = [
  '2023-09-14',
  '2024-01-23',
  '2024-04-08',
  '2023-11-30',
];
const RECENT_DATES = [
  '2026-08-14',
  '2026-08-18',
  '2026-08-21',
  '2026-08-25',
];
const CONTROL_CYCLE = ['ungrounded', 'unreachable', 'bare'];
const ARMS = [
  { id: 'A', token: 'verified:', file: 'runner-arm-a.md' },
  { id: 'B', token: 'read_on:', file: 'runner-arm-b.md' },
  { id: 'C', token: 'accessed:', file: 'runner-arm-c.md' },
  { id: 'D', token: 'retrieved:', file: 'runner-arm-d.md' },
];

function fail(message) {
  throw new Error(message);
}

function digest(algorithm, bytes) {
  return crypto.createHash(algorithm).update(bytes).digest('hex');
}

function countOccurrences(text, needle) {
  let count = 0;
  let offset = 0;
  while (true) {
    const found = text.indexOf(needle, offset);
    if (found === -1) return count;
    count += 1;
    offset = found + needle.length;
  }
}

function validateBaseBytes(bytes) {
  const actualMd5 = digest('md5', bytes);
  if (actualMd5 !== BASE_MD5) {
    fail(`base MD5 mismatch: expected ${BASE_MD5}, got ${actualMd5}`);
  }
  const text = bytes.toString('utf8');
  if (!text.startsWith('---\n')) fail('base does not begin with YAML ---');
  if (!text.endsWith('\n')) fail('base does not end with LF');
  if (text.includes('\r')) fail('base contains CR bytes');
  return text;
}

function readPinnedBase() {
  return validateBaseBytes(fs.readFileSync(BASE_PATH));
}

function parseAnnotatedRows(baseText) {
  const lines = baseText.split('\n');
  const annotationPattern = new RegExp(
    `^  \\[source: (.+) · tier: ([^ ·]+) · verified: ${BASE_DATE}\\]$`,
  );
  const rows = [];
  const usedBulletLines = new Set();

  for (let lineIndex = 0; lineIndex < lines.length; lineIndex += 1) {
    const match = lines[lineIndex].match(annotationPattern);
    if (!match) continue;

    let bulletLineIndex = lineIndex - 1;
    while (bulletLineIndex >= 0 && !lines[bulletLineIndex].startsWith('- ')) {
      bulletLineIndex -= 1;
    }
    if (bulletLineIndex < 0) {
      fail(`annotation at line ${lineIndex + 1} has no owning bullet`);
    }
    if (usedBulletLines.has(bulletLineIndex)) {
      fail(`bullet at line ${bulletLineIndex + 1} owns more than one annotation`);
    }
    usedBulletLines.add(bulletLineIndex);

    const number = rows.length + 1;
    rows.push({
      id: `C${String(number).padStart(2, '0')}`,
      index: number - 1,
      annotationLineIndex: lineIndex,
      baseAnnotationLine: lineIndex + 1,
      bulletLineIndex,
      baseBulletLine: bulletLineIndex + 1,
      source: match[1],
      tier: match[2],
    });
  }

  if (rows.length !== 41) fail(`expected 41 annotations, got ${rows.length}`);
  return rows;
}

function isUnreachableEligible(row) {
  return row.tier === '1-docs' || row.tier === '2-context7';
}

function resolveControlStates(rows) {
  const controls = rows.filter((row) => row.index % 3 === 2);
  const states = controls.map((_, index) => CONTROL_CYCLE[index % CONTROL_CYCLE.length]);
  const swaps = [];

  for (let index = 0; index < controls.length; index += 1) {
    if (states[index] !== 'unreachable' || isUnreachableEligible(controls[index])) continue;
    const replacementIndex = controls.findIndex(
      (candidate, candidateIndex) =>
        candidateIndex > index &&
        states[candidateIndex] === 'bare' &&
        isUnreachableEligible(candidate),
    );
    if (replacementIndex === -1) {
      fail(`no eligible later bare control can swap with ${controls[index].id}`);
    }
    states[index] = 'bare';
    states[replacementIndex] = 'unreachable';
    swaps.push(`${controls[index].id}<->${controls[replacementIndex].id}`);
  }

  const stateById = new Map();
  controls.forEach((row, index) => stateById.set(row.id, states[index]));
  const ineligible = controls.filter(
    (row) => stateById.get(row.id) === 'unreachable' && !isUnreachableEligible(row),
  );
  if (ineligible.length > 0) {
    fail(`ineligible unreachable controls: ${ineligible.map((row) => row.id).join(', ')}`);
  }
  if (swaps.join(',') !== 'C15<->C18,C24<->C27') {
    fail(`unexpected control resolution: ${swaps.join(',')}`);
  }
  return { stateById, swaps };
}

function assignStates(rows) {
  const { stateById, swaps } = resolveControlStates(rows);
  let oldCursor = 0;
  let recentCursor = 0;

  const assigned = rows.map((row) => {
    let state;
    if (row.index % 3 === 0) state = 'old-grounded';
    if (row.index % 3 === 1) state = 'recent-grounded';
    if (row.index % 3 === 2) state = stateById.get(row.id);

    let date = null;
    if (state === 'old-grounded' || state === 'unreachable') {
      date = OLD_DATES[oldCursor % OLD_DATES.length];
      oldCursor += 1;
    } else if (state === 'recent-grounded') {
      date = RECENT_DATES[recentCursor % RECENT_DATES.length];
      recentCursor += 1;
    }
    return { ...row, state, date };
  });

  if (oldCursor !== 18) fail(`expected 18 old-date cursor uses, got ${oldCursor}`);
  if (recentCursor !== 14) fail(`expected 14 recent-date cursor uses, got ${recentCursor}`);
  return { rows: assigned, swaps };
}

function annotationFor(row, armToken) {
  if (row.state === 'bare') return null;
  if (row.state === 'ungrounded') {
    return '  [source: none · tier: 3-model · ungrounded]';
  }
  if (row.state === 'unreachable') {
    return `  [source: ${row.source} · tier: ${row.tier} · unreachable: ${row.date}]`;
  }
  return `  [source: ${row.source} · tier: ${row.tier} · ${armToken} ${row.date}]`;
}

function countStates(rows) {
  const counts = {};
  for (const row of rows) counts[row.state] = (counts[row.state] || 0) + 1;
  return counts;
}

function generateFixture(baseText, arm) {
  const parsedRows = parseAnnotatedRows(baseText);
  const { rows, swaps } = assignStates(parsedRows);
  const lines = baseText.split('\n');

  for (const row of rows) {
    lines[row.bulletLineIndex] =
      `- [${row.id}] ` + lines[row.bulletLineIndex].slice(2);
    lines[row.annotationLineIndex] = annotationFor(row, arm.token);
  }

  const transformed = lines.filter((line) => line !== null);
  transformed.splice(1, 0, FIXTURE_CONSUMER_LINE);
  const text = transformed.join('\n');
  const stateCounts = countStates(rows);

  const expectedStateCounts = {
    'old-grounded': 14,
    'recent-grounded': 14,
    ungrounded: 5,
    unreachable: 4,
    bare: 4,
  };
  for (const [state, expected] of Object.entries(expectedStateCounts)) {
    if (stateCounts[state] !== expected) {
      fail(`${arm.id}: expected ${expected} ${state}, got ${stateCounts[state] || 0}`);
    }
  }
  if (countOccurrences(text, '[C') !== 41) fail(`${arm.id}: identifier count is not 41`);
  if (countOccurrences(text, ` · ${arm.token} `) !== 28) {
    fail(`${arm.id}: own arm-token count is not 28`);
  }
  if (countOccurrences(text, ' · unreachable: ') !== 4) {
    fail(`${arm.id}: unreachable count is not 4`);
  }
  if (countOccurrences(text, ' · ungrounded]') !== 5) {
    fail(`${arm.id}: ungrounded count is not 5`);
  }
  if (countOccurrences(text, FIXTURE_CONSUMER_LINE) !== 1) {
    fail(`${arm.id}: consumer marker count is not 1`);
  }
  if (!text.startsWith('---\n')) fail(`${arm.id}: fixture no longer begins with YAML ---`);
  if (!text.endsWith('\n')) fail(`${arm.id}: fixture no longer ends with LF`);

  return { arm, text, bytes: Buffer.from(text, 'utf8'), rows, swaps, stateCounts };
}

function buildAllFixtures() {
  const baseText = readPinnedBase();
  return new Map(ARMS.map((arm) => [arm.id, generateFixture(baseText, arm)]));
}

function mapsByteEqual(left, right) {
  if (left.size !== right.size) return false;
  for (const arm of ARMS) {
    if (!left.has(arm.id) || !right.has(arm.id)) return false;
    if (!left.get(arm.id).bytes.equals(right.get(arm.id).bytes)) return false;
  }
  return true;
}

function differingByteCount(left, right) {
  const common = Math.min(left.length, right.length);
  let count = Math.abs(left.length - right.length);
  for (let index = 0; index < common; index += 1) {
    if (left[index] !== right[index]) count += 1;
  }
  return count;
}

function normalizeFixture(fixtureBytes, arm) {
  const text = fixtureBytes.toString('utf8');
  const ownNeedle = ` · ${arm.token} `;
  const ownCount = countOccurrences(text, ownNeedle);
  if (ownCount !== 28) fail(`${arm.id}: expected 28 own tokens, got ${ownCount}`);
  for (const other of ARMS) {
    if (other.id === arm.id) continue;
    const foreignCount = countOccurrences(text, ` · ${other.token} `);
    if (foreignCount !== 0) {
      fail(`${arm.id}: found ${foreignCount} foreign ${other.id} tokens`);
    }
  }
  const escapedToken = arm.token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const annotationPattern = new RegExp(
    `^(  \\[source: .+ · tier: [^ ·]+ · )${escapedToken} (\\d{4}-\\d{2}-\\d{2}\\])$`,
  );
  let replacements = 0;
  const normalizedText = text
    .split('\n')
    .map((line) => {
      if (!annotationPattern.test(line)) return line;
      replacements += 1;
      return line.replace(annotationPattern, `$1${PLACEHOLDER_TOKEN} $2`);
    })
    .join('\n');
  if (replacements !== 28) {
    fail(`${arm.id}: expected 28 slot-three replacements, got ${replacements}`);
  }
  return {
    bytes: Buffer.from(normalizedText, 'utf8'),
    replacements,
  };
}

function normalizedMap(rawMap) {
  return new Map(
    ARMS.map((arm) => {
      const fixture = rawMap.get(arm.id);
      const normalized = normalizeFixture(fixture.bytes || fixture, arm);
      return [arm.id, { ...normalized, arm }];
    }),
  );
}

function normalizedMapsEqual(normalized) {
  const reference = normalized.get('A').bytes;
  return ARMS.every((arm) => reference.equals(normalized.get(arm.id).bytes));
}

function oneByteMutation(bytes) {
  const marker = Buffer.from('Consumer', 'utf8');
  const index = bytes.indexOf(marker);
  if (index === -1) fail('mutation marker not found');
  const mutated = Buffer.from(bytes);
  mutated[index] ^= 1;
  const differences = differingByteCount(bytes, mutated);
  if (differences !== 1) fail(`mutation changed ${differences} bytes, expected 1`);
  if (mutated[index] === bytes[index]) fail('mutation did not land');
  return { mutated, index, differences };
}

function runDeterminismCheck() {
  const first = buildAllFixtures();
  const second = buildAllFixtures();
  const equal = mapsByteEqual(first, second);
  console.log(`determinism regenerated-byte-identical=${equal}`);
  for (const arm of ARMS) {
    const firstBytes = first.get(arm.id).bytes;
    const secondBytes = second.get(arm.id).bytes;
    console.log(
      `determinism arm=${arm.id} first_bytes=${firstBytes.length} second_bytes=${secondBytes.length} ` +
        `first_sha256=${digest('sha256', firstBytes)} second_sha256=${digest('sha256', secondBytes)}`,
    );
  }
  if (!equal) fail('regenerated fixtures are not byte-identical');

  const mutation = oneByteMutation(second.get('A').bytes);
  const controlled = new Map(second);
  controlled.set('A', { ...second.get('A'), bytes: mutation.mutated });
  const controlEqual = mapsByteEqual(first, controlled);
  console.log(
    `determinism-control mutation_landed=true index=${mutation.index} ` +
      `differing_bytes=${mutation.differences} regenerated-byte-identical=${controlEqual}`,
  );
  if (controlEqual) fail('determinism comparator did not detect one-byte control');
  console.log('determinism PASS');
}

function expectFailure(operation, fragment) {
  try {
    operation();
  } catch (error) {
    if (!error.message.includes(fragment)) {
      fail(`control threw ${JSON.stringify(error.message)}, expected ${JSON.stringify(fragment)}`);
    }
    return error.message;
  }
  fail(`control did not fail for ${fragment}`);
}

function runSelfTest() {
  const baseBytes = fs.readFileSync(BASE_PATH);
  const baseText = validateBaseBytes(baseBytes);
  const parsed = parseAnnotatedRows(baseText);
  console.log(`generator-self-test base_annotations=${parsed.length}`);

  const digestIndex = baseBytes.indexOf(Buffer.from('schema_version', 'utf8'));
  if (digestIndex === -1) fail('digest-control marker is absent');
  const digestMutated = Buffer.from(baseBytes);
  digestMutated[digestIndex] ^= 1;
  const digestMutation = {
    mutated: digestMutated,
    differences: differingByteCount(baseBytes, digestMutated),
  };
  if (digestMutation.differences !== 1) fail('digest mutation did not change exactly one byte');
  console.log(
    `generator-self-test digest_mutation_landed=true differing_bytes=${digestMutation.differences} ` +
      `message=${JSON.stringify(expectFailure(() => validateBaseBytes(digestMutation.mutated), 'base MD5 mismatch'))}`,
  );

  const marker = Buffer.from('  [source:', 'utf8');
  const annotationIndex = baseBytes.indexOf(marker);
  if (annotationIndex === -1) fail('annotation marker for parser control is absent');
  const parserMutation = Buffer.from(baseBytes);
  parserMutation[annotationIndex + 9] ^= 1;
  const parserDifferences = differingByteCount(baseBytes, parserMutation);
  if (parserDifferences !== 1) fail('parser mutation did not change exactly one byte');
  console.log(
    `generator-self-test parser_mutation_landed=true differing_bytes=${parserDifferences} ` +
      `message=${JSON.stringify(
        expectFailure(() => parseAnnotatedRows(parserMutation.toString('utf8')), 'expected 41 annotations'),
      )}`,
  );

  const controls = parsed.filter((row) => row.index % 3 === 2);
  const literalStates = controls.map((_, index) => CONTROL_CYCLE[index % CONTROL_CYCLE.length]);
  const literalIneligible = controls
    .filter(
      (row, index) => literalStates[index] === 'unreachable' && !isUnreachableEligible(row),
    )
    .map((row) => row.id);
  if (literalIneligible.join(',') !== 'C15,C24') {
    fail(`literal eligibility control returned ${literalIneligible.join(',')}`);
  }
  const resolved = resolveControlStates(parsed);
  const resolvedIneligible = controls
    .filter(
      (row) => resolved.stateById.get(row.id) === 'unreachable' && !isUnreachableEligible(row),
    )
    .map((row) => row.id);
  if (resolvedIneligible.length !== 0) fail('resolved control map still has ineligible rows');
  console.log(
    `generator-self-test literal_ineligible=${literalIneligible.join(',')} ` +
      `resolved_ineligible=${resolvedIneligible.length} swaps=${resolved.swaps.join(',')}`,
  );
  console.log('generator-self-test PASS');
}

function writeFixtures() {
  const fixtures = buildAllFixtures();
  fs.mkdirSync(FIXTURE_DIR, { recursive: true });
  for (const arm of ARMS) {
    const fixture = fixtures.get(arm.id);
    const outputPath = path.join(FIXTURE_DIR, arm.file);
    fs.writeFileSync(outputPath, fixture.bytes);
    console.log(
      `generated arm=${arm.id} path=${outputPath} bytes=${fixture.bytes.length} ` +
        `sha256=${digest('sha256', fixture.bytes)}`,
    );
  }
  console.log(`control-resolution swaps=${fixtures.get('A').swaps.join(',')}`);
}

function readFixtureMap() {
  const fixtures = new Map();
  for (const arm of ARMS) {
    const fixturePath = path.join(FIXTURE_DIR, arm.file);
    fixtures.set(arm.id, { arm, bytes: fs.readFileSync(fixturePath) });
  }
  return fixtures;
}

function runGate2() {
  const raw = readFixtureMap();
  const normalized = normalizedMap(raw);
  const equal = normalizedMapsEqual(normalized);
  for (const arm of ARMS) {
    const item = normalized.get(arm.id);
    console.log(
      `gate-2 arm=${arm.id} replacements=${item.replacements} normalized_bytes=${item.bytes.length} ` +
        `normalized_sha256=${digest('sha256', item.bytes)}`,
    );
  }
  console.log(`gate-2 normalized-byte-identical=${equal}`);
  if (!equal) fail('Gate 2 normalized fixtures differ');

  const mutation = oneByteMutation(raw.get('D').bytes);
  const controlledRaw = new Map(raw);
  controlledRaw.set('D', { ...raw.get('D'), bytes: mutation.mutated });
  const controlledNormalized = normalizedMap(controlledRaw);
  const controlEqual = normalizedMapsEqual(controlledNormalized);
  console.log(
    `gate-2-control mutation_landed=true arm=D index=${mutation.index} ` +
      `differing_bytes=${mutation.differences} normalized-byte-identical=${controlEqual}`,
  );
  if (controlEqual) fail('Gate 2 comparator did not detect one-byte control');
  console.log('gate-2 PASS');
}

function main() {
  const command = process.argv[2];
  if (command === '--self-test') return runSelfTest();
  if (command === '--determinism') return runDeterminismCheck();
  if (command === '--generate') return writeFixtures();
  if (command === '--gate-2') return runGate2();
  fail('usage: node generator.js --self-test|--determinism|--generate|--gate-2');
}

if (require.main === module) {
  try {
    main();
  } catch (error) {
    console.error(`generator FAIL: ${error.message}`);
    process.exitCode = 1;
  }
}

module.exports = {
  ARMS,
  BASE_MD5,
  BASE_PATH,
  FIXTURE_DIR,
  buildAllFixtures,
  digest,
  normalizeFixture,
  runGate2,
};
