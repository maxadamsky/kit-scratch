#!/usr/bin/env node
'use strict';

// Consumers: scorer.js and the operator after all 120 logical slots terminate.

const fs = require('node:fs');

const {
  ACTION_VALUES,
  OBSERVATIONS_PATH,
  PILE_VALUES,
  PINNED_EFFORT,
  PINNED_MODEL,
  buildSchedule,
  newObservationFile,
  validateObservationShape,
} = require('./runner.js');

function fail(message) {
  throw new Error(message);
}

function validateParsedResult(entry) {
  const parsed = entry.successfulResult?.parsed;
  if (!Array.isArray(parsed) || parsed.length !== 41) {
    fail(`${entry.slotId}: successful result does not contain 41 parsed lines`);
  }
  const allowed = entry.trialType === 'pile-sort' ? PILE_VALUES : ACTION_VALUES;
  const seen = new Set();
  for (let index = 0; index < parsed.length; index += 1) {
    const expectedId = `C${String(index + 1).padStart(2, '0')}`;
    if (parsed[index].id !== expectedId) {
      fail(`${entry.slotId}: parsed position ${index + 1} is not ${expectedId}`);
    }
    if (seen.has(parsed[index].id)) fail(`${entry.slotId}: duplicate ${parsed[index].id}`);
    seen.add(parsed[index].id);
    if (!allowed.has(parsed[index].value)) {
      fail(`${entry.slotId}: invalid parsed value ${parsed[index].value}`);
    }
  }
}

function assertComplete(observations, options = {}) {
  const { requireUsageReadings = true } = options;
  validateObservationShape(observations);
  if (
    !observations._meta?.consumers?.includes('completion-gate.js') ||
    !observations._meta?.consumers?.includes('scorer.js')
  ) {
    fail('observations do not name completion-gate.js and scorer.js as consumers');
  }
  const schedule = buildSchedule();
  const sessionIds = new Set();
  const workingDirectories = new Set();

  for (let index = 0; index < schedule.length; index += 1) {
    const slot = schedule[index];
    const entry = observations.entries[index];
    if (entry.status !== 'success' || entry.successfulResult === null) {
      fail(
        `${slot.slotId}: no successful result (status=${entry.status || 'missing'})`,
      );
    }
    if (entry.terminalFailure !== null) {
      fail(`${slot.slotId}: success entry also carries a terminal failure`);
    }
    if (entry.successfulResult.resolvedModel !== PINNED_MODEL) {
      fail(
        `${slot.slotId}: resolved model ${entry.successfulResult.resolvedModel || 'missing'} ` +
          `differs from ${PINNED_MODEL}`,
      );
    }
    if (entry.successfulResult.resolvedEffort !== PINNED_EFFORT) {
      fail(
        `${slot.slotId}: resolved effort ${entry.successfulResult.resolvedEffort || 'missing'} ` +
          `differs from ${PINNED_EFFORT}`,
      );
    }
    const effortEvents = entry.successfulResult.resolvedEffortEvidence?.events;
    if (
      !Array.isArray(effortEvents) ||
      effortEvents.length === 0 ||
      effortEvents.some((event) => event.effort !== PINNED_EFFORT)
    ) {
      fail(`${slot.slotId}: resolved effort lacks matching per-invocation OTLP evidence`);
    }
    const streamModel = entry.successfulResult.resolvedModelEvidence?.streamInit;
    const otlpModels = entry.successfulResult.resolvedModelEvidence?.otlpSdkApiRequests;
    if (
      streamModel !== PINNED_MODEL ||
      !Array.isArray(otlpModels) ||
      otlpModels.length === 0 ||
      otlpModels.some((event) => event.model !== PINNED_MODEL)
    ) {
      fail(`${slot.slotId}: resolved model lacks matching stream and OTLP evidence`);
    }
    const sessionId = entry.attempt?.streamSessionId;
    if (!sessionId) fail(`${slot.slotId}: stream session ID is missing`);
    if (sessionIds.has(sessionId)) fail(`${slot.slotId}: stream session ID is duplicated`);
    sessionIds.add(sessionId);
    const workingDirectory = entry.attempt?.workingDirectory;
    if (!workingDirectory) fail(`${slot.slotId}: working directory path is missing`);
    if (workingDirectories.has(workingDirectory)) {
      fail(`${slot.slotId}: working directory path is duplicated`);
    }
    workingDirectories.add(workingDirectory);
    if (entry.attempt.workingDirectoryBeforeEntries?.length !== 0) {
      fail(`${slot.slotId}: working directory was not empty before invocation`);
    }
    if (entry.attempt.workingDirectoryAfterEntries?.length !== 0) {
      fail(`${slot.slotId}: working directory was not empty after invocation`);
    }
    if (entry.attempt.workingDirectoryRemoved !== true) {
      fail(`${slot.slotId}: working directory removal was not recorded`);
    }
    validateParsedResult(entry);
  }

  if (requireUsageReadings) {
    if (!observations.usageCredits?.beforeRun) fail('pre-run usage-credit reading is missing');
    if (!observations.usageCredits?.afterRun) fail('post-run usage-credit reading is missing');
    if (!observations.usageCredits?.movement) fail('usage-credit movement observation is missing');
  }
  return {
    slots: schedule.length,
    uniqueSessionIds: sessionIds.size,
    uniqueWorkingDirectories: workingDirectories.size,
    usageReadingsPresent: Boolean(
      observations.usageCredits?.beforeRun && observations.usageCredits?.afterRun,
    ),
  };
}

function syntheticSuccessfulObservations() {
  const observations = newObservationFile();
  observations.usageCredits.beforeRun = {
    source: 'synthetic control',
    recordedAt: '2026-08-27T00:00:00.000Z',
    creditsSpentUsd: 1,
    currentBalanceUsd: 2,
  };
  observations.usageCredits.afterRun = {
    source: 'synthetic control',
    recordedAt: '2026-08-27T01:00:00.000Z',
    creditsSpentUsd: 1,
    currentBalanceUsd: 2,
  };
  observations.usageCredits.movement = {
    observed: false,
    before: { creditsSpentUsd: 1, currentBalanceUsd: 2 },
    after: { creditsSpentUsd: 1, currentBalanceUsd: 2 },
    finding: null,
  };
  for (const entry of observations.entries) {
    const allowedValue = entry.trialType === 'pile-sort' ? 'Still-grounded' : 'USE';
    const sessionId = `synthetic-${String(entry.sequence).padStart(3, '0')}`;
    entry.status = 'success';
    entry.terminalFailure = null;
    entry.attempt = {
      streamSessionId: sessionId,
      workingDirectory: `/synthetic/fr015-${String(entry.sequence).padStart(3, '0')}`,
      workingDirectoryBeforeEntries: [],
      workingDirectoryAfterEntries: [],
      workingDirectoryRemoved: true,
    };
    entry.successfulResult = {
      resolvedModel: PINNED_MODEL,
      resolvedModelEvidence: {
        streamInit: PINNED_MODEL,
        otlpSdkApiRequests: [{ model: PINNED_MODEL, requestId: `model-${entry.sequence}` }],
      },
      resolvedEffort: PINNED_EFFORT,
      resolvedEffortEvidence: {
        channel: 'synthetic control',
        events: [{ effort: PINNED_EFFORT, requestId: `effort-${entry.sequence}` }],
      },
      parsed: Array.from({ length: 41 }, (_, index) => ({
        id: `C${String(index + 1).padStart(2, '0')}`,
        value: allowedValue,
      })),
      resultTelemetry: {},
      auxiliaryModelUsage: {},
    };
  }
  return observations;
}

function expectFailure(observations, expectedFragment) {
  try {
    assertComplete(observations);
  } catch (error) {
    if (!error.message.includes(expectedFragment)) {
      fail(`control threw ${JSON.stringify(error.message)}, expected ${JSON.stringify(expectedFragment)}`);
    }
    return error.message;
  }
  fail(`control did not fail for ${expectedFragment}`);
}

function selfTest() {
  const valid = syntheticSuccessfulObservations();
  const result = assertComplete(valid);
  console.log(`completion-gate-control valid_slots=${result.slots} passes=true`);

  const failed = structuredClone(valid);
  const failedIndex = 36;
  failed.entries[failedIndex].status = 'terminal-failure';
  failed.entries[failedIndex].successfulResult = null;
  failed.entries[failedIndex].terminalFailure = { code: 'synthetic', detail: 'one-slot control' };
  if (failed.entries[failedIndex].status !== 'terminal-failure') fail('failure mutation did not land');
  console.log(
    `completion-gate-control failure_mutation_landed=true message=${JSON.stringify(
      expectFailure(failed, failed.entries[failedIndex].slotId),
    )}`,
  );

  const modelMismatch = structuredClone(valid);
  modelMismatch.entries[0].successfulResult.resolvedModel = 'wrong-model-control';
  if (modelMismatch.entries[0].successfulResult.resolvedModel !== 'wrong-model-control') {
    fail('model mutation did not land');
  }
  console.log(
    `completion-gate-control model_mutation_landed=true message=${JSON.stringify(
      expectFailure(modelMismatch, 'resolved model'),
    )}`,
  );

  const effortMismatch = structuredClone(valid);
  effortMismatch.entries[0].successfulResult.resolvedEffort = 'wrong-effort-control';
  if (effortMismatch.entries[0].successfulResult.resolvedEffort !== 'wrong-effort-control') {
    fail('effort mutation did not land');
  }
  console.log(
    `completion-gate-control effort_mutation_landed=true message=${JSON.stringify(
      expectFailure(effortMismatch, 'resolved effort'),
    )}`,
  );

  const duplicateDirectory = structuredClone(valid);
  duplicateDirectory.entries[1].attempt.workingDirectory =
    duplicateDirectory.entries[0].attempt.workingDirectory;
  if (
    duplicateDirectory.entries[1].attempt.workingDirectory !==
    duplicateDirectory.entries[0].attempt.workingDirectory
  ) {
    fail('working-directory mutation did not land');
  }
  console.log(
    `completion-gate-control cwd_mutation_landed=true message=${JSON.stringify(
      expectFailure(duplicateDirectory, 'working directory path is duplicated'),
    )}`,
  );
  console.log('completion-gate-self-test PASS');
}

function main() {
  const command = process.argv[2];
  if (command === 'self-test') return selfTest();
  if (command === 'check') {
    const observations = JSON.parse(fs.readFileSync(OBSERVATIONS_PATH, 'utf8'));
    const result = assertComplete(observations);
    console.log(
      `completion-gate PASS slots=${result.slots} unique_sessions=${result.uniqueSessionIds} ` +
        `unique_cwds=${result.uniqueWorkingDirectories} usage_readings=${result.usageReadingsPresent}`,
    );
    return;
  }
  fail('usage: node completion-gate.js self-test|check');
}

if (require.main === module) {
  try {
    main();
  } catch (error) {
    console.error(`completion-gate FAIL: ${error.message}`);
    process.exitCode = 1;
  }
}

module.exports = { assertComplete, syntheticSuccessfulObservations };
