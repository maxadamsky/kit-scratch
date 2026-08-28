#!/usr/bin/env node
'use strict';

// Consumer: the operator. Produces observations for completion-gate.js and scorer.js.

const crypto = require('node:crypto');
const fs = require('node:fs');
const http = require('node:http');
const os = require('node:os');
const path = require('node:path');
const { spawn } = require('node:child_process');

const { ARMS, digest } = require('./generator.js');

const HARNESS_DIR = __dirname;
const ANSWER_KEY_PATH = path.join(HARNESS_DIR, 'answer-key.json');
const OBSERVATIONS_PATH = path.join(HARNESS_DIR, 'observations.json');
const INSTRUCTION_PATHS = {
  'pile-sort': path.join(HARNESS_DIR, 'instructions', 'runner-pile-sort.json'),
  action: path.join(HARNESS_DIR, 'instructions', 'runner-action.json'),
};
const INSTRUCTION_PINS = Object.freeze({
  'pile-sort': Object.freeze({
    bytes: 557,
    sha256: '53f52c4e3d9f6d89070977c212259f4d431ddeb02c99d2d659c4377dd90da2f8',
  }),
  action: Object.freeze({
    bytes: 270,
    sha256: 'ffc9b4fead4bfe5dec63cc97e84ceaa9fe733e7a7978a182bf1af20bc206f24e',
  }),
});
const PINNED_MODEL = 'claude-sonnet-5';
const PINNED_EFFORT = 'high';
const SLOT_TIMEOUT_MS = 10 * 60 * 1000;
const OUTPUT_LIMIT_BYTES = 2 * 1024 * 1024;
const CLAUDE_EXECUTABLE = process.env.FR015_CLAUDE_BIN || 'claude';
const ARGUMENTS_BEFORE_PROMPT = Object.freeze([
  '-p',
  '--output-format',
  'stream-json',
  '--verbose',
  '--model',
  PINNED_MODEL,
  '--effort',
  PINNED_EFFORT,
  '--safe-mode',
  '--tools',
  '',
  '--disable-slash-commands',
  '--strict-mcp-config',
  '--no-chrome',
  '--no-session-persistence',
  '--',
]);
const PILE_VALUES = new Set([
  'Still-grounded',
  'Expired',
  'Never-grounded',
  'Human-authored',
]);
const ACTION_VALUES = new Set(['USE', 'HOLD']);
const FORBIDDEN_INSTRUCTION_WORDS = Object.freeze([
  'verify',
  'verified',
  'verification',
  'confirm',
  'validate',
  'read',
  'review',
  'inspect',
  'access',
  'accessed',
  'retrieve',
  'retrieved',
  'fetch',
  'obtain',
  'consult',
  'check',
  'audit',
  'open',
  'view',
  'see',
  'look',
]);

function fail(message) {
  throw new Error(message);
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function writeJsonAtomic(filePath, value) {
  const temporaryPath = `${filePath}.tmp-${process.pid}-${crypto.randomUUID()}`;
  fs.writeFileSync(temporaryPath, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
  fs.renameSync(temporaryPath, filePath);
}

function buildSchedule() {
  const schedule = [];
  let sequence = 1;
  for (const [trialType, repetitions] of [
    ['pile-sort', 20],
    ['action', 10],
  ]) {
    for (let trial = 1; trial <= repetitions; trial += 1) {
      for (const arm of ARMS) {
        schedule.push({
          slotId: `${trialType}-${String(trial).padStart(2, '0')}-${arm.id}`,
          sequence,
          trialType,
          trial,
          arm: arm.id,
        });
        sequence += 1;
      }
    }
  }
  return schedule;
}

function scheduleCounts(schedule) {
  const counts = {
    total: schedule.length,
    byType: {},
    byArmAndType: {},
  };
  for (const slot of schedule) {
    counts.byType[slot.trialType] = (counts.byType[slot.trialType] || 0) + 1;
    const key = `${slot.arm}/${slot.trialType}`;
    counts.byArmAndType[key] = (counts.byArmAndType[key] || 0) + 1;
  }
  return counts;
}

function validateSchedule(schedule) {
  const counts = scheduleCounts(schedule);
  if (counts.total !== 120) fail(`schedule has ${counts.total} slots, expected 120`);
  if (counts.byType['pile-sort'] !== 80) fail('pile-sort schedule count is not 80');
  if (counts.byType.action !== 40) fail('action schedule count is not 40');
  for (const arm of ARMS) {
    if (counts.byArmAndType[`${arm.id}/pile-sort`] !== 20) {
      fail(`arm ${arm.id} pile-sort count is not 20`);
    }
    if (counts.byArmAndType[`${arm.id}/action`] !== 10) {
      fail(`arm ${arm.id} action count is not 10`);
    }
  }
  const unique = new Set(schedule.map((slot) => slot.slotId));
  if (unique.size !== schedule.length) fail('schedule has duplicate slot IDs');
  for (let index = 0; index < schedule.length; index += 1) {
    if (schedule[index].sequence !== index + 1) fail('schedule sequence is not contiguous');
  }
  return counts;
}

function validateInstructionRecord(trialType, record, instructionPath) {
  const independentPin = INSTRUCTION_PINS[trialType];
  if (!independentPin) fail(`${trialType} has no independent instruction pin`);
  if (record.consumer !== 'runner.js') fail(`${trialType} instruction consumer is not runner.js`);
  if (typeof record.instruction !== 'string') fail(`${trialType} instruction payload is absent`);
  const bytes = Buffer.from(record.instruction, 'utf8');
  if (!bytes.equals(Buffer.from(bytes.toString('utf8'), 'utf8'))) {
    fail(`${trialType} instruction is not round-trip UTF-8`);
  }
  if (bytes.at(-1) !== 10 || record.finalLf !== true) {
    fail(`${trialType} instruction does not declare and carry final LF`);
  }
  const sha256 = digest('sha256', bytes);
  if (sha256 !== record.instructionSha256) {
    fail(`${trialType} instruction digest mismatch`);
  }
  if (bytes.length !== independentPin.bytes) {
    fail(
      `${trialType} instruction byte count ${bytes.length} differs from independent pin ${independentPin.bytes}`,
    );
  }
  if (sha256 !== independentPin.sha256) {
    fail(`${trialType} instruction SHA-256 differs from independent pin`);
  }
  const lower = record.instruction.toLowerCase();
  const forbiddenMatches = FORBIDDEN_INSTRUCTION_WORDS.filter((word) =>
    new RegExp(`\\b${word}\\w*\\b`, 'i').test(lower),
  );
  if (forbiddenMatches.length > 0) {
    fail(`${trialType} instruction contains forbidden words: ${forbiddenMatches.join(', ')}`);
  }
  return {
    path: instructionPath,
    relativePath: path.relative(HARNESS_DIR, instructionPath),
    text: record.instruction,
    bytes,
    sha256,
  };
}

function loadInstruction(trialType) {
  const instructionPath = INSTRUCTION_PATHS[trialType];
  return validateInstructionRecord(trialType, readJson(instructionPath), instructionPath);
}

function loadFixture(armId, answerKey) {
  const fixtureRecord = answerKey.fixtures[armId];
  if (!fixtureRecord) fail(`answer key has no fixture for arm ${armId}`);
  const fixturePath = path.join(HARNESS_DIR, fixtureRecord.path);
  const bytes = fs.readFileSync(fixturePath);
  const sha256 = digest('sha256', bytes);
  if (sha256 !== fixtureRecord.sha256) fail(`fixture ${armId} digest mismatch`);
  if (bytes.length !== fixtureRecord.bytes) fail(`fixture ${armId} byte count mismatch`);
  return {
    path: fixturePath,
    relativePath: fixtureRecord.path,
    bytes,
    sha256,
  };
}

function validateArtifactSet() {
  const answerKey = readJson(ANSWER_KEY_PATH);
  if (
    !answerKey._meta?.consumers?.includes('runner.js') ||
    !answerKey._meta?.consumers?.includes('scorer.js')
  ) {
    fail('answer key does not name runner.js and scorer.js as consumers');
  }
  if (!Array.isArray(answerKey.lines) || answerKey.lines.length !== 41) {
    fail('answer key does not contain 41 lines');
  }
  const ids = answerKey.lines.map((line) => line.id);
  const expectedIds = Array.from({ length: 41 }, (_, index) =>
    `C${String(index + 1).padStart(2, '0')}`,
  );
  if (JSON.stringify(ids) !== JSON.stringify(expectedIds)) {
    fail('answer-key IDs are not C01-C41 in order');
  }
  const instructions = {
    'pile-sort': loadInstruction('pile-sort'),
    action: loadInstruction('action'),
  };
  const fixtures = Object.fromEntries(
    ARMS.map((arm) => [arm.id, loadFixture(arm.id, answerKey)]),
  );
  return { answerKey, instructions, fixtures };
}

function newObservationFile() {
  const schedule = buildSchedule();
  const counts = validateSchedule(schedule);
  return {
    schemaVersion: 1,
    _meta: {
      consumers: ['runner.js', 'completion-gate.js', 'scorer.js'],
      createdBy: 'runner.js initialize',
    },
    run: {
      experiment: 'FR-015 verb-change reader validation',
      stage: 'stage-4-owner-review',
      createdAt: new Date().toISOString(),
      slotsPlanned: counts.total,
      slotsAttempted: 0,
      successfulSlots: 0,
      terminallyFailedSlots: 0,
      modelPin: PINNED_MODEL,
      effortPin: PINNED_EFFORT,
    },
    usageCredits: {
      source: 'unverified owner-reported Settings > Usage UI observation',
      observedAt: '2026-08-27',
      probeReading: {
        creditsSpentUsd: 69.4,
        currentBalanceUsd: 51.47,
        monthlySpendLimitUsd: 100,
        creditPeriodResets: 'Sep 1',
        currentSessionWindowUsedPercent: 5,
        weeklyAllModelsUsedPercent: 8,
        probeAttribution: 'inconclusive; the probe was too small to separate from other activity',
      },
      beforeRun: null,
      afterRun: null,
      movement: null,
    },
    entries: schedule.map((slot) => ({
      ...slot,
      status: 'pending',
      requestedInvocation: {
        executable: CLAUDE_EXECUTABLE,
        argumentsBeforePrompt: [...ARGUMENTS_BEFORE_PROMPT],
        modelFlag: ['--model', PINNED_MODEL],
        effortFlag: ['--effort', PINNED_EFFORT],
        promptTransport: 'single positional argument after --',
      },
      attempt: null,
      successfulResult: null,
      terminalFailure: null,
    })),
  };
}

function initializeObservations() {
  if (fs.existsSync(OBSERVATIONS_PATH)) {
    fail(`refusing to overwrite existing ${OBSERVATIONS_PATH}`);
  }
  const observations = newObservationFile();
  writeJsonAtomic(OBSERVATIONS_PATH, observations);
  console.log(
    `initialized observations path=${OBSERVATIONS_PATH} entries=${observations.entries.length} ` +
      `sha256=${digest('sha256', fs.readFileSync(OBSERVATIONS_PATH))}`,
  );
}

function validateObservationShape(observations) {
  if (!observations._meta?.consumers?.includes('runner.js')) {
    fail('observations do not name runner.js as a consumer');
  }
  const schedule = buildSchedule();
  validateSchedule(schedule);
  if (!Array.isArray(observations.entries) || observations.entries.length !== schedule.length) {
    fail('observations do not contain exactly 120 entries');
  }
  const seen = new Set();
  for (let index = 0; index < schedule.length; index += 1) {
    const expected = schedule[index];
    const actual = observations.entries[index];
    for (const key of ['slotId', 'sequence', 'trialType', 'trial', 'arm']) {
      if (actual[key] !== expected[key]) fail(`${expected.slotId}: schedule field ${key} differs`);
    }
    if (seen.has(actual.slotId)) fail(`duplicate observation slot ${actual.slotId}`);
    seen.add(actual.slotId);
    if (
      JSON.stringify(actual.requestedInvocation?.argumentsBeforePrompt) !==
      JSON.stringify(ARGUMENTS_BEFORE_PROMPT)
    ) {
      fail(`${actual.slotId}: invocation arguments differ from the pin`);
    }
  }
  return scheduleCounts(schedule);
}

function printPlan() {
  const schedule = buildSchedule();
  const counts = validateSchedule(schedule);
  console.log(`plan total=${counts.total} pile-sort=${counts.byType['pile-sort']} action=${counts.byType.action}`);
  for (const arm of ARMS) {
    console.log(
      `plan arm=${arm.id} pile-sort=${counts.byArmAndType[`${arm.id}/pile-sort`]} ` +
        `action=${counts.byArmAndType[`${arm.id}/action`]}`,
    );
  }
  console.log(`plan first=${schedule[0].slotId} last=${schedule.at(-1).slotId}`);
  console.log(`plan arguments-before-prompt=${JSON.stringify(ARGUMENTS_BEFORE_PROMPT)}`);
  console.log('plan spawn-shell=false');
  console.log('plan execution=not-started');
}

function validateHarness() {
  const schedule = buildSchedule();
  const counts = validateSchedule(schedule);
  const artifacts = validateArtifactSet();
  const observations = readJson(OBSERVATIONS_PATH);
  validateObservationShape(observations);
  const pending = observations.entries.filter((entry) => entry.status === 'pending').length;
  const started = observations.entries.filter((entry) => entry.status === 'started').length;
  const successful = observations.entries.filter((entry) => entry.status === 'success').length;
  const failed = observations.entries.filter((entry) => entry.status === 'terminal-failure').length;
  console.log(
    `validate schedule_total=${counts.total} pile-sort=${counts.byType['pile-sort']} action=${counts.byType.action}`,
  );
  for (const trialType of ['pile-sort', 'action']) {
    const instruction = artifacts.instructions[trialType];
    console.log(
      `validate instruction=${trialType} bytes=${instruction.bytes.length} sha256=${instruction.sha256}`,
    );
  }
  for (const arm of ARMS) {
    const fixture = artifacts.fixtures[arm.id];
    console.log(`validate fixture=${arm.id} bytes=${fixture.bytes.length} sha256=${fixture.sha256}`);
  }
  console.log(
    `validate observations entries=${observations.entries.length} pending=${pending} started=${started} ` +
      `success=${successful} terminal-failure=${failed}`,
  );
  console.log('validate no-invocation=true');
}

function otelValue(value) {
  if (!value || typeof value !== 'object') return null;
  for (const key of [
    'stringValue',
    'intValue',
    'doubleValue',
    'boolValue',
  ]) {
    if (Object.hasOwn(value, key)) return value[key];
  }
  return null;
}

function attributesToObject(attributes) {
  return Object.fromEntries(
    (attributes || []).map((attribute) => [attribute.key, otelValue(attribute.value)]),
  );
}

function extractApiRequests(document) {
  const extracted = [];
  for (const resourceLog of document.resourceLogs || []) {
    for (const scopeLog of resourceLog.scopeLogs || []) {
      for (const record of scopeLog.logRecords || []) {
        const body = otelValue(record.body);
        const attributes = attributesToObject(record.attributes);
        if (body !== 'claude_code.api_request') continue;
        extracted.push({
          event: body,
          sessionId: attributes['session.id'] || null,
          model: attributes.model || null,
          effort: attributes.effort || null,
          querySource: attributes.query_source || null,
          requestId: attributes.request_id || null,
          clientRequestId: attributes.client_request_id || null,
        });
      }
    }
  }
  return extracted;
}

async function startEffortCollector() {
  const apiRequests = [];
  const errors = [];
  const server = http.createServer((request, response) => {
    const chunks = [];
    let bytes = 0;
    request.on('data', (chunk) => {
      bytes += chunk.length;
      if (bytes <= OUTPUT_LIMIT_BYTES) chunks.push(chunk);
    });
    request.on('end', () => {
      try {
        if (bytes > OUTPUT_LIMIT_BYTES) throw new Error('OTLP request exceeded byte limit');
        if (request.url === '/v1/logs') {
          const document = JSON.parse(Buffer.concat(chunks).toString('utf8'));
          apiRequests.push(...extractApiRequests(document));
        }
        response.writeHead(200, { 'content-type': 'application/json' });
        response.end('{}');
      } catch (error) {
        errors.push(error.message);
        response.writeHead(400, { 'content-type': 'application/json' });
        response.end('{}');
      }
    });
  });
  server.on('clientError', (error, socket) => {
    errors.push(error.message);
    socket.end('HTTP/1.1 400 Bad Request\r\n\r\n');
  });
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  const address = server.address();
  if (!address || typeof address === 'string') fail('OTLP collector has no TCP address');
  return {
    apiRequests,
    errors,
    endpoint: `http://127.0.0.1:${address.port}`,
    async close() {
      await new Promise((resolve, reject) =>
        server.close((error) => (error ? reject(error) : resolve())),
      );
    },
  };
}

function collectChildOutput(child) {
  return new Promise((resolve) => {
    const stdoutChunks = [];
    const stderrChunks = [];
    let stdoutBytes = 0;
    let stderrBytes = 0;
    let spawnError = null;
    let timedOut = false;
    let overflow = false;
    let forcedKill = null;

    function terminate() {
      child.kill('SIGTERM');
      if (!forcedKill) {
        forcedKill = setTimeout(() => child.kill('SIGKILL'), 5000);
      }
    }

    function collect(target, chunk, kind) {
      if (kind === 'stdout') stdoutBytes += chunk.length;
      else stderrBytes += chunk.length;
      if (stdoutBytes > OUTPUT_LIMIT_BYTES || stderrBytes > OUTPUT_LIMIT_BYTES) {
        overflow = true;
        terminate();
        return;
      }
      target.push(chunk);
    }

    child.stdout.on('data', (chunk) => collect(stdoutChunks, chunk, 'stdout'));
    child.stderr.on('data', (chunk) => collect(stderrChunks, chunk, 'stderr'));
    child.once('error', (error) => {
      spawnError = error;
    });
    const timeout = setTimeout(() => {
      timedOut = true;
      terminate();
    }, SLOT_TIMEOUT_MS);
    child.once('close', (exitCode, signal) => {
      clearTimeout(timeout);
      if (forcedKill) clearTimeout(forcedKill);
      resolve({
        exitCode,
        signal,
        spawnError: spawnError ? spawnError.message : null,
        timedOut,
        overflow,
        stdout: Buffer.concat(stdoutChunks).toString('utf8'),
        stderr: Buffer.concat(stderrChunks).toString('utf8'),
      });
    });
  });
}

function parseStream(stdout) {
  const lines = stdout.split('\n').filter((line) => line.length > 0);
  const messages = lines.map((line, index) => {
    try {
      return JSON.parse(line);
    } catch (error) {
      fail(`stream line ${index + 1} is not JSON: ${error.message}`);
    }
  });
  const init = messages.filter((message) => message.type === 'system' && message.subtype === 'init');
  const results = messages.filter((message) => message.type === 'result');
  if (init.length !== 1) fail(`expected one init event, got ${init.length}`);
  if (results.length !== 1) fail(`expected one result event, got ${results.length}`);
  return { messages, init: init[0], result: results[0] };
}

function parseSubjectResult(trialType, resultText) {
  if (typeof resultText !== 'string') fail('terminal result has no text');
  const lines = resultText.replace(/\r\n/g, '\n').split('\n');
  if (lines.at(-1) === '') lines.pop();
  if (lines.length !== 41) fail(`subject emitted ${lines.length} lines, expected 41`);
  const allowed = trialType === 'pile-sort' ? PILE_VALUES : ACTION_VALUES;
  const parsed = [];
  for (let index = 0; index < lines.length; index += 1) {
    const match = lines[index].match(/^(C\d{2})[ \t]+(.+)$/);
    if (!match) fail(`subject line ${index + 1} has invalid shape`);
    const expectedId = `C${String(index + 1).padStart(2, '0')}`;
    if (match[1] !== expectedId) {
      fail(`subject line ${index + 1} has ${match[1]}, expected ${expectedId}`);
    }
    if (!allowed.has(match[2])) fail(`${match[1]} has invalid ${trialType} value ${match[2]}`);
    parsed.push({ id: match[1], value: match[2] });
  }
  if (new Set(parsed.map((item) => item.id)).size !== 41) fail('subject emitted duplicate IDs');
  return parsed;
}

function terminalFailure(code, detail) {
  return {
    status: 'terminal-failure',
    successfulResult: null,
    terminalFailure: { code, detail },
  };
}

function determineSuccessfulResult(slot, processResult, stream, apiRequests, collectorErrors) {
  if (processResult.spawnError) return terminalFailure('spawn-error', processResult.spawnError);
  if (processResult.timedOut) return terminalFailure('timeout', `${SLOT_TIMEOUT_MS}ms elapsed`);
  if (processResult.overflow) return terminalFailure('output-limit', `${OUTPUT_LIMIT_BYTES} byte limit`);
  if (processResult.exitCode !== 0 || processResult.signal !== null) {
    return terminalFailure(
      'process-failure',
      `exit=${processResult.exitCode} signal=${processResult.signal || 'none'}`,
    );
  }
  if (collectorErrors.length > 0) {
    return terminalFailure('effort-telemetry-error', collectorErrors.join('; '));
  }
  if (stream.result.subtype !== 'success' || stream.result.is_error === true) {
    return terminalFailure('claude-result-failure', `subtype=${stream.result.subtype}`);
  }
  const sessionId = stream.init.session_id;
  if (!sessionId || stream.result.session_id !== sessionId) {
    return terminalFailure('session-id-mismatch', 'init and result session IDs differ or are absent');
  }
  if (stream.init.model !== PINNED_MODEL) {
    return terminalFailure(
      'resolved-model-mismatch',
      `pin=${PINNED_MODEL} init=${stream.init.model || 'missing'}`,
    );
  }
  const mainRequests = apiRequests.filter(
    (event) => event.sessionId === sessionId && event.querySource === 'sdk',
  );
  if (mainRequests.length === 0) {
    return terminalFailure('resolved-effort-missing', 'no joinable sdk api_request OTLP event');
  }
  if (mainRequests.some((event) => !event.model)) {
    return terminalFailure('resolved-model-missing', 'a joined sdk api_request omits model');
  }
  if (mainRequests.some((event) => !event.effort)) {
    return terminalFailure('resolved-effort-missing', 'a joined sdk api_request omits effort');
  }
  const resolvedModels = [...new Set(mainRequests.map((event) => event.model).filter(Boolean))];
  const resolvedEfforts = [...new Set(mainRequests.map((event) => event.effort).filter(Boolean))];
  if (resolvedModels.length !== 1 || resolvedModels[0] !== PINNED_MODEL) {
    return terminalFailure(
      'resolved-model-mismatch',
      `pin=${PINNED_MODEL} otlp=${resolvedModels.join(',') || 'missing'}`,
    );
  }
  if (resolvedEfforts.length !== 1 || resolvedEfforts[0] !== PINNED_EFFORT) {
    return terminalFailure(
      'resolved-effort-mismatch',
      `pin=${PINNED_EFFORT} otlp=${resolvedEfforts.join(',') || 'missing'}`,
    );
  }
  let parsedResult;
  try {
    parsedResult = parseSubjectResult(slot.trialType, stream.result.result);
  } catch (error) {
    return terminalFailure('malformed-subject-result', error.message);
  }
  const modelUsage = stream.result.modelUsage || {};
  if (!Object.hasOwn(modelUsage, PINNED_MODEL)) {
    return terminalFailure('primary-model-usage-missing', `${PINNED_MODEL} absent from modelUsage`);
  }
  return {
    status: 'success',
    terminalFailure: null,
    successfulResult: {
      resolvedModel: PINNED_MODEL,
      resolvedModelEvidence: {
        streamInit: stream.init.model,
        otlpSdkApiRequests: mainRequests.map((event) => ({
          model: event.model,
          requestId: event.requestId,
          clientRequestId: event.clientRequestId,
        })),
      },
      resolvedEffort: PINNED_EFFORT,
      resolvedEffortEvidence: {
        channel: 'loopback OTLP claude_code.api_request joined by session.id and query_source=sdk',
        events: mainRequests.map((event) => ({
          effort: event.effort,
          requestId: event.requestId,
          clientRequestId: event.clientRequestId,
        })),
      },
      parsed: parsedResult,
      resultTelemetry: stream.result,
      auxiliaryModelUsage: Object.fromEntries(
        Object.entries(modelUsage).filter(([model]) => model !== PINNED_MODEL),
      ),
    },
  };
}

function telemetryEnvironment(endpoint) {
  return {
    ...process.env,
    CLAUDE_CODE_ENABLE_TELEMETRY: '1',
    OTEL_LOGS_EXPORTER: 'otlp',
    OTEL_METRICS_EXPORTER: 'none',
    OTEL_TRACES_EXPORTER: 'none',
    OTEL_EXPORTER_OTLP_PROTOCOL: 'http/json',
    OTEL_EXPORTER_OTLP_ENDPOINT: endpoint,
    OTEL_EXPORTER_OTLP_LOGS_ENDPOINT: `${endpoint}/v1/logs`,
    OTEL_BLRP_SCHEDULE_DELAY: '100',
    OTEL_LOG_USER_PROMPTS: '0',
    OTEL_LOG_ASSISTANT_RESPONSES: '0',
    OTEL_LOG_RAW_API_BODIES: '0',
    OTEL_LOG_TOOL_DETAILS: '0',
  };
}

async function runSlot(slot, observations, artifacts) {
  const fixture = artifacts.fixtures[slot.arm];
  const instruction = artifacts.instructions[slot.trialType];
  const promptBytes = Buffer.concat([fixture.bytes, Buffer.from('\n', 'utf8'), instruction.bytes]);
  const prompt = promptBytes.toString('utf8');
  const cwd = fs.mkdtempSync(path.join(os.tmpdir(), 'fr015-'));
  const cwdBeforeEntries = fs.readdirSync(cwd);
  if (cwdBeforeEntries.length !== 0) fail(`${slot.slotId}: new cwd is not empty`);
  const collector = await startEffortCollector();
  const startedAt = new Date().toISOString();
  const attempt = {
    startedAt,
    endedAt: null,
    executable: CLAUDE_EXECUTABLE,
    argumentsBeforePrompt: [...ARGUMENTS_BEFORE_PROMPT],
    modelFlag: ['--model', PINNED_MODEL],
    effortFlag: ['--effort', PINNED_EFFORT],
    promptTransport: 'single positional argument after --',
    promptSeparator: 'one LF after the fixture final LF',
    promptBytes: promptBytes.length,
    promptSha256: digest('sha256', promptBytes),
    fixturePath: fixture.relativePath,
    fixtureSha256: fixture.sha256,
    instructionPath: instruction.relativePath,
    instructionSha256: instruction.sha256,
    workingDirectory: cwd,
    workingDirectoryBeforeEntries: cwdBeforeEntries,
    workingDirectoryAfterEntries: null,
    workingDirectoryRemoved: false,
    exitCode: null,
    signal: null,
    stdout: null,
    stderr: null,
    streamSessionId: null,
    observedApiRequests: [],
    reportedResolution: null,
    resultTelemetry: null,
    auxiliaryModelUsage: {},
  };

  const entryIndex = observations.entries.findIndex((entry) => entry.slotId === slot.slotId);
  observations.entries[entryIndex] = {
    ...observations.entries[entryIndex],
    status: 'started',
    attempt,
    successfulResult: null,
    terminalFailure: null,
  };
  writeJsonAtomic(OBSERVATIONS_PATH, observations);

  let processResult;
  let stream = null;
  let outcome;
  try {
    const child = spawn(CLAUDE_EXECUTABLE, [...ARGUMENTS_BEFORE_PROMPT, prompt], {
      cwd,
      env: telemetryEnvironment(collector.endpoint),
      shell: false,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    processResult = await collectChildOutput(child);
    await collector.close();
    try {
      stream = parseStream(processResult.stdout);
      outcome = determineSuccessfulResult(
        slot,
        processResult,
        stream,
        collector.apiRequests,
        collector.errors,
      );
    } catch (error) {
      outcome = terminalFailure('malformed-stream', error.message);
    }
  } catch (error) {
    try {
      await collector.close();
    } catch {
      // The original failure remains authoritative.
    }
    processResult = {
      exitCode: null,
      signal: null,
      stdout: '',
      stderr: '',
      spawnError: error.message,
      timedOut: false,
      overflow: false,
    };
    outcome = terminalFailure('runner-error', error.message);
  }

  const cwdAfterEntries = fs.readdirSync(cwd);
  if (cwdAfterEntries.length > 0 && outcome.status === 'success') {
    outcome = terminalFailure(
      'working-directory-not-empty',
      `post-invocation entries=${JSON.stringify(cwdAfterEntries)}`,
    );
  }
  fs.rmSync(cwd, { recursive: true });
  attempt.endedAt = new Date().toISOString();
  attempt.workingDirectoryAfterEntries = cwdAfterEntries;
  attempt.workingDirectoryRemoved = !fs.existsSync(cwd);
  attempt.exitCode = processResult.exitCode;
  attempt.signal = processResult.signal;
  attempt.stdout = processResult.stdout;
  attempt.stderr = processResult.stderr;
  attempt.streamSessionId = stream?.init?.session_id || null;
  attempt.observedApiRequests = collector.apiRequests;
  const joinedSdkRequests = collector.apiRequests.filter(
    (event) =>
      attempt.streamSessionId &&
      event.sessionId === attempt.streamSessionId &&
      event.querySource === 'sdk',
  );
  attempt.reportedResolution = {
    modelFromStreamInit: stream?.init?.model || null,
    modelsFromJoinedOtlpSdkRequests: [
      ...new Set(joinedSdkRequests.map((event) => event.model).filter(Boolean)),
    ],
    effortsFromJoinedOtlpSdkRequests: [
      ...new Set(joinedSdkRequests.map((event) => event.effort).filter(Boolean)),
    ],
  };
  attempt.resultTelemetry = stream?.result || null;
  attempt.auxiliaryModelUsage = Object.fromEntries(
    Object.entries(stream?.result?.modelUsage || {}).filter(([model]) => model !== PINNED_MODEL),
  );

  const priorSessionIds = new Set(
    observations.entries
      .filter((entry) => entry.slotId !== slot.slotId)
      .map((entry) => entry.attempt?.streamSessionId)
      .filter(Boolean),
  );
  if (attempt.streamSessionId && priorSessionIds.has(attempt.streamSessionId)) {
    outcome = terminalFailure('duplicate-session-id', attempt.streamSessionId);
  }
  return {
    ...observations.entries[entryIndex],
    ...outcome,
    attempt,
  };
}

function updateRunCounts(observations) {
  observations.run.slotsAttempted = observations.entries.filter(
    (entry) => entry.status !== 'pending',
  ).length;
  observations.run.successfulSlots = observations.entries.filter(
    (entry) => entry.status === 'success',
  ).length;
  observations.run.terminallyFailedSlots = observations.entries.filter(
    (entry) => entry.status === 'terminal-failure',
  ).length;
}

async function executeRun() {
  if (process.argv[3] !== '--stage-5-approved') {
    fail('execution requires the literal argument --stage-5-approved');
  }
  const artifacts = validateArtifactSet();
  const observations = readJson(OBSERVATIONS_PATH);
  validateObservationShape(observations);
  if (!observations.usageCredits.beforeRun) {
    fail('record Settings > Usage credits spent and balance before executing slot 1');
  }
  for (let index = 0; index < observations.entries.length; index += 1) {
    if (observations.entries[index].status === 'started') {
      observations.entries[index] = {
        ...observations.entries[index],
        ...terminalFailure(
          'indeterminate-interruption',
          'a prior process ended after the started record and before a terminal record',
        ),
      };
    }
  }
  observations.run.stage = 'stage-5-executing';
  writeJsonAtomic(OBSERVATIONS_PATH, observations);

  const schedule = buildSchedule();
  for (const slot of schedule) {
    const index = observations.entries.findIndex((entry) => entry.slotId === slot.slotId);
    if (observations.entries[index].status !== 'pending') continue;
    const completed = await runSlot(slot, observations, artifacts);
    observations.entries[index] = completed;
    updateRunCounts(observations);
    writeJsonAtomic(OBSERVATIONS_PATH, observations);
    console.log(
      `slot=${slot.slotId} status=${completed.status} ` +
        `resolved_model=${completed.successfulResult?.resolvedModel || 'none'} ` +
        `resolved_effort=${completed.successfulResult?.resolvedEffort || 'none'}`,
    );
  }
  observations.run.stage = 'stage-5-awaiting-post-run-usage-reading';
  updateRunCounts(observations);
  writeJsonAtomic(OBSERVATIONS_PATH, observations);
  console.log(
    `run-complete attempted=${observations.run.slotsAttempted} success=${observations.run.successfulSlots} ` +
      `terminal-failure=${observations.run.terminallyFailedSlots}`,
  );
}

function recordUsage(when, spentText, balanceText) {
  if (!['before', 'after'].includes(when)) fail('usage position must be before or after');
  const creditsSpentUsd = Number(spentText);
  const currentBalanceUsd = Number(balanceText);
  if (!Number.isFinite(creditsSpentUsd) || creditsSpentUsd < 0) fail('credits spent is invalid');
  if (!Number.isFinite(currentBalanceUsd) || currentBalanceUsd < 0) fail('balance is invalid');
  const observations = readJson(OBSERVATIONS_PATH);
  validateObservationShape(observations);
  if (when === 'before') {
    if (observations.entries.some((entry) => entry.status !== 'pending')) {
      fail('the before reading must be recorded before the first slot starts');
    }
    observations.usageCredits.beforeRun = {
      source: 'operator-observed Settings > Usage UI',
      recordedAt: new Date().toISOString(),
      creditsSpentUsd,
      currentBalanceUsd,
    };
  } else {
    if (observations.entries.some((entry) => ['pending', 'started'].includes(entry.status))) {
      fail('the after reading must be recorded after every slot reaches a terminal state');
    }
    observations.usageCredits.afterRun = {
      source: 'operator-observed Settings > Usage UI',
      recordedAt: new Date().toISOString(),
      creditsSpentUsd,
      currentBalanceUsd,
    };
    const before = observations.usageCredits.beforeRun;
    if (!before) fail('cannot record the after reading without a before reading');
    const moved =
      before.creditsSpentUsd !== creditsSpentUsd ||
      before.currentBalanceUsd !== currentBalanceUsd;
    observations.usageCredits.movement = {
      observed: moved,
      before: {
        creditsSpentUsd: before.creditsSpentUsd,
        currentBalanceUsd: before.currentBalanceUsd,
      },
      after: { creditsSpentUsd, currentBalanceUsd },
      finding: moved
        ? 'Some portion of the run was billed at API rates rather than drawn from the subscription.'
        : null,
    };
    observations.run.stage = 'stage-5-complete-awaiting-completion-gate';
  }
  writeJsonAtomic(OBSERVATIONS_PATH, observations);
  console.log(
    `usage-reading position=${when} credits_spent_usd=${creditsSpentUsd.toFixed(2)} ` +
      `current_balance_usd=${currentBalanceUsd.toFixed(2)}`,
  );
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

async function postJson(urlText, document) {
  const url = new URL(urlText);
  const body = Buffer.from(JSON.stringify(document), 'utf8');
  await new Promise((resolve, reject) => {
    const request = http.request(
      {
        hostname: url.hostname,
        port: url.port,
        path: url.pathname,
        method: 'POST',
        headers: {
          'content-type': 'application/json',
          'content-length': body.length,
        },
      },
      (response) => {
        response.resume();
        response.once('end', () => {
          if (response.statusCode !== 200) reject(new Error(`loopback status ${response.statusCode}`));
          else resolve();
        });
      },
    );
    request.once('error', reject);
    request.end(body);
  });
}

async function selfTest() {
  const schedule = buildSchedule();
  validateSchedule(schedule);
  const shortened = schedule.slice(0, -1);
  console.log(
    `runner-self-test schedule_control_message=${JSON.stringify(
      expectFailure(() => validateSchedule(shortened), 'expected 120'),
      )}`,
  );

  const instructionPath = INSTRUCTION_PATHS['pile-sort'];
  const originalInstruction = readJson(instructionPath);
  const mutatedInstruction = { ...originalInstruction };
  mutatedInstruction.instruction = mutatedInstruction.instruction.replace('Sort every', 'sort every');
  if (mutatedInstruction.instruction === originalInstruction.instruction) {
    fail('instruction mutation did not land');
  }
  const originalBytes = Buffer.from(originalInstruction.instruction, 'utf8');
  const mutatedBytes = Buffer.from(mutatedInstruction.instruction, 'utf8');
  let differingBytes = Math.abs(originalBytes.length - mutatedBytes.length);
  for (let index = 0; index < Math.min(originalBytes.length, mutatedBytes.length); index += 1) {
    if (originalBytes[index] !== mutatedBytes[index]) differingBytes += 1;
  }
  if (differingBytes !== 1) fail(`instruction mutation changed ${differingBytes} bytes, expected 1`);
  mutatedInstruction.instructionSha256 = digest('sha256', mutatedBytes);
  console.log(
    `runner-self-test instruction_pin_control mutation_landed=true differing_bytes=${differingBytes} ` +
      `declared_sha_updated=true control_message=${JSON.stringify(
        expectFailure(
          () => validateInstructionRecord('pile-sort', mutatedInstruction, instructionPath),
          'differs from independent pin',
        ),
      )}`,
  );

  const validPile = Array.from(
    { length: 41 },
    (_, index) => `C${String(index + 1).padStart(2, '0')} Still-grounded`,
  ).join('\n');
  const parsed = parseSubjectResult('pile-sort', validPile);
  if (parsed.length !== 41) fail('valid parser control did not return 41 rows');
  const malformedPile = validPile.replace('C01 Still-grounded', 'C02 Still-grounded');
  if (malformedPile === validPile) fail('parser mutation did not land');
  console.log(
    `runner-self-test parser_valid_rows=${parsed.length} mutation_landed=true ` +
      `control_message=${JSON.stringify(
        expectFailure(() => parseSubjectResult('pile-sort', malformedPile), 'expected C01'),
      )}`,
  );

  const collector = await startEffortCollector();
  const syntheticSession = 'synthetic-session';
  const otlpDocument = {
    resourceLogs: [
      {
        scopeLogs: [
          {
            logRecords: [
              {
                body: { stringValue: 'claude_code.api_request' },
                attributes: [
                  { key: 'session.id', value: { stringValue: syntheticSession } },
                  { key: 'model', value: { stringValue: PINNED_MODEL } },
                  { key: 'effort', value: { stringValue: PINNED_EFFORT } },
                  { key: 'query_source', value: { stringValue: 'sdk' } },
                  { key: 'request_id', value: { stringValue: 'synthetic-request' } },
                ],
              },
            ],
          },
        ],
      },
    ],
  };
  await postJson(`${collector.endpoint}/v1/logs`, otlpDocument);
  await collector.close();
  const observed = collector.apiRequests[0];
  if (
    collector.apiRequests.length !== 1 ||
    observed.sessionId !== syntheticSession ||
    observed.model !== PINNED_MODEL ||
    observed.effort !== PINNED_EFFORT ||
    observed.querySource !== 'sdk'
  ) {
    fail('loopback OTLP parser did not preserve the pin fields');
  }
  console.log(
    `runner-self-test otlp_events=${collector.apiRequests.length} session_join=${observed.sessionId} ` +
      `model=${observed.model} effort=${observed.effort} query_source=${observed.querySource}`,
  );

  const syntheticProcessResult = {
    exitCode: 0,
    signal: null,
    spawnError: null,
    timedOut: false,
    overflow: false,
  };
  const syntheticStream = {
    init: { session_id: syntheticSession, model: PINNED_MODEL },
    result: {
      session_id: syntheticSession,
      subtype: 'success',
      is_error: false,
      result: validPile,
      modelUsage: { [PINNED_MODEL]: {} },
    },
  };
  const validResolution = determineSuccessfulResult(
    { slotId: 'synthetic', trialType: 'pile-sort' },
    syntheticProcessResult,
    syntheticStream,
    [observed],
    [],
  );
  if (validResolution.status !== 'success') fail('valid resolution control did not succeed');
  const mixedMissing = determineSuccessfulResult(
    { slotId: 'synthetic', trialType: 'pile-sort' },
    syntheticProcessResult,
    syntheticStream,
    [observed, { ...observed, effort: null, requestId: 'missing-effort-control' }],
    [],
  );
  if (mixedMissing.terminalFailure?.code !== 'resolved-effort-missing') {
    fail('mixed present/missing effort control did not fail in the runner');
  }
  const mixedModelMissing = determineSuccessfulResult(
    { slotId: 'synthetic', trialType: 'pile-sort' },
    syntheticProcessResult,
    syntheticStream,
    [observed, { ...observed, model: null, requestId: 'missing-model-control' }],
    [],
  );
  if (mixedModelMissing.terminalFailure?.code !== 'resolved-model-missing') {
    fail('mixed present/missing model control did not fail in the runner');
  }
  console.log(
    `runner-self-test mixed_effort_present_missing_status=${mixedMissing.status} ` +
      `failure=${mixedMissing.terminalFailure.code}`,
  );
  console.log(
    `runner-self-test mixed_model_present_missing_status=${mixedModelMissing.status} ` +
      `failure=${mixedModelMissing.terminalFailure.code}`,
  );
  console.log('runner-self-test no-claude-invocation=true');
  console.log('runner-self-test PASS');
}

async function main() {
  const command = process.argv[2];
  if (command === 'plan') return printPlan();
  if (command === 'initialize') return initializeObservations();
  if (command === 'validate') return validateHarness();
  if (command === 'self-test') return selfTest();
  if (command === 'record-usage') {
    return recordUsage(process.argv[3], process.argv[4], process.argv[5]);
  }
  if (command === 'execute') return executeRun();
  fail(
    'usage: node runner.js plan|initialize|validate|self-test|record-usage <before|after> <spent> <balance>|execute --stage-5-approved',
  );
}

if (require.main === module) {
  main().catch((error) => {
    console.error(`runner FAIL: ${error.message}`);
    process.exitCode = 1;
  });
}

module.exports = {
  ACTION_VALUES,
  ARGUMENTS_BEFORE_PROMPT,
  OBSERVATIONS_PATH,
  PILE_VALUES,
  PINNED_EFFORT,
  PINNED_MODEL,
  buildSchedule,
  newObservationFile,
  parseSubjectResult,
  validateObservationShape,
};
