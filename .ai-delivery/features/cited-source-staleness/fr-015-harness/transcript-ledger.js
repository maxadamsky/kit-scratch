#!/usr/bin/env node
'use strict';

// Consumer: the Stage 4 owner and operator. Reads the retained Codex transcript only.

const fs = require('node:fs');
const path = require('node:path');

function fail(message) {
  throw new Error(message);
}

function messageText(record) {
  return (record.payload?.content || [])
    .map((part) => part.text || part.input_text || part.output_text || '')
    .join('\n');
}

function countProbeLedger(transcriptPath) {
  const rows = fs
    .readFileSync(transcriptPath, 'utf8')
    .trimEnd()
    .split('\n')
    .map((line) => JSON.parse(line));

  const cutoff = rows.find(
    (row) =>
      row.type === 'response_item' &&
      row.payload?.type === 'message' &&
      row.payload?.role === 'user' &&
      messageText(row).startsWith('Stage 4 review, three items before approval.'),
  );
  if (!cutoff) fail('Stage 4 review cutoff message is absent');

  const outputs = new Map(
    rows
      .filter((row) => row.payload?.type === 'custom_tool_call_output')
      .map((row) => [row.payload.call_id, JSON.stringify(row.payload.output)]),
  );
  const calls = rows.filter(
    (row) =>
      row.ordinal < cutoff.ordinal &&
      row.payload?.type === 'custom_tool_call' &&
      row.payload?.name === 'exec' &&
      (row.payload.input || '').includes('tools.exec_command'),
  );

  const ledger = [];
  for (const call of calls) {
    const input = call.payload.input || '';
    const commands = input.split('claude -p').length - 1;
    if (commands === 0) continue;

    const rawOutput = outputs.get(call.payload.call_id) || '';
    let state;
    if (rawOutput.includes('Rejected(')) {
      state = 'not-launched';
    } else if (input.includes('FR-015-BILLING-PROBE-OK')) {
      state = 'stage1-billing';
    } else if (
      rawOutput.includes("error: unknown option '---") ||
      rawOutput.includes('No conversation found with session ID:')
    ) {
      state = 'pre-model';
    } else if (rawOutput.includes('session_id') || rawOutput.includes('messageModel')) {
      state = 'model-backed';
    } else {
      fail(`unclassified transcript record at ordinal ${call.ordinal}`);
    }
    ledger.push({ ordinal: call.ordinal, commands, state });
  }

  const count = (state) =>
    ledger
      .filter((entry) => entry.state === state)
      .reduce((total, entry) => total + entry.commands, 0);
  const chooserInvocations = calls.filter(
    (call) =>
      (call.payload.input || '').includes('cmd: "claude --safe-mode') &&
      (call.payload.input || '').includes('tty: true') &&
      !(call.payload.input || '').includes('claude -p'),
  ).length;

  return {
    cutoffOrdinal: cutoff.ordinal,
    ledger,
    summary: {
      mechanismAttempts: count('model-backed') + count('pre-model'),
      modelBacked: count('model-backed'),
      preModel: count('pre-model'),
      chooserInvocations,
      separateStage1BillingAttempts: count('stage1-billing'),
      rejectedBeforeLaunch: count('not-launched'),
    },
  };
}

function main() {
  const argument = process.argv[2];
  if (!argument) fail('usage: node transcript-ledger.js <rollout.jsonl>');
  const transcriptPath = path.resolve(argument);
  const result = countProbeLedger(transcriptPath);
  console.log(`transcript=${transcriptPath}`);
  console.log(`stage4-cutoff-ordinal=${result.cutoffOrdinal}`);
  for (const entry of result.ledger) console.log(JSON.stringify(entry));
  console.log(JSON.stringify(result.summary));
}

if (require.main === module) {
  try {
    main();
  } catch (error) {
    console.error(`transcript-ledger FAIL: ${error.message}`);
    process.exitCode = 1;
  }
}

module.exports = { countProbeLedger };
