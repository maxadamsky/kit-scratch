#!/usr/bin/env node
'use strict';

// Consumer: the operator. Reads answer-key.json only after completion-gate.js passes.

const fs = require('node:fs');
const path = require('node:path');

const { assertComplete, syntheticSuccessfulObservations } = require('./completion-gate.js');
const { OBSERVATIONS_PATH } = require('./runner.js');

const HARNESS_DIR = __dirname;
const ANSWER_KEY_PATH = path.join(HARNESS_DIR, 'answer-key.json');
const ARM_IDS = ['A', 'B', 'C', 'D'];
const CANDIDATE_IDS = ['B', 'C', 'D'];
const PILE_TRIALS_PER_ARM = 20;
const ACTION_TRIALS_PER_ARM = 10;
const GROUNDED_ROWS_PER_TRIAL = 14;
const OBJECTIVE_CONTROLS_PER_TRIAL = 9;
const ACTION_ROWS_PER_TRIAL = 41;
const GROUNDED_DENOMINATOR = PILE_TRIALS_PER_ARM * GROUNDED_ROWS_PER_TRIAL;
const CONTROL_DENOMINATOR = PILE_TRIALS_PER_ARM * OBJECTIVE_CONTROLS_PER_TRIAL;
const ACTION_DENOMINATOR = ACTION_TRIALS_PER_ARM * ACTION_ROWS_PER_TRIAL;
const INVARIANCE_MAX_COUNT_DIFFERENCE = 18; // 0.10 * 180
const RECENT_FLOOR_MAX_COUNT = 56; // 0.20 * 280
const WINNER_BAND_MAX_COUNT_DIFFERENCE = 14; // 0.05 * 280

function fail(message) {
  throw new Error(message);
}

function mean(values) {
  if (values.length === 0) fail('cannot take mean of an empty array');
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function pearson(xs, ys) {
  if (xs.length !== ys.length || xs.length < 2) fail('Pearson inputs have invalid lengths');
  const xMean = mean(xs);
  const yMean = mean(ys);
  let numerator = 0;
  let xSquares = 0;
  let ySquares = 0;
  for (let index = 0; index < xs.length; index += 1) {
    const xDelta = xs[index] - xMean;
    const yDelta = ys[index] - yMean;
    numerator += xDelta * yDelta;
    xSquares += xDelta * xDelta;
    ySquares += yDelta * yDelta;
  }
  if (xSquares === 0 || ySquares === 0) return null;
  return numerator / Math.sqrt(xSquares * ySquares);
}

function evaluateDecision(arms) {
  const controlTotals = ARM_IDS.map((arm) => arms[arm].controlMisclassificationTotal);
  const invarianceCountDifference = Math.max(...controlTotals) - Math.min(...controlTotals);
  const invarianceRange = invarianceCountDifference / CONTROL_DENOMINATOR;
  if (invarianceCountDifference > INVARIANCE_MAX_COUNT_DIFFERENCE) {
    return {
      status: 'invalid',
      reason: 'invariance-control',
      invarianceRange,
      invarianceCountDifference,
      floorFailures: null,
      passingCandidates: [],
      reportedWinners: [],
    };
  }

  const floorFailures = ARM_IDS.filter(
    (arm) =>
      arms[arm].recentExpiredTotal > RECENT_FLOOR_MAX_COUNT ||
      arms[arm].recentExpiredTotal >= arms[arm].oldExpiredTotal,
  );
  if (floorFailures.length === ARM_IDS.length) {
    return {
      status: 'decisive-against-feature',
      reason: 'floor-control-failed-in-all-arms',
      invarianceRange,
      invarianceCountDifference,
      floorFailures,
      passingCandidates: [],
      reportedWinners: [],
    };
  }
  if (floorFailures.length > 0) {
    return {
      status: 'invalid',
      reason: 'floor-control-failed-in-some-arms',
      invarianceRange,
      invarianceCountDifference,
      floorFailures,
      passingCandidates: [],
      reportedWinners: [],
    };
  }

  const baselineMaximumCount = arms.A.oldExpiredMaximumCount;
  const baselineMaximum = baselineMaximumCount / GROUNDED_ROWS_PER_TRIAL;
  const passingCandidates = CANDIDATE_IDS.filter(
    (arm) => arms[arm].oldExpiredMinimumCount > baselineMaximumCount,
  );
  if (passingCandidates.length === 0) {
    return {
      status: 'fr-015-fails',
      reason: 'no-candidate-has-strict-non-overlap',
      invarianceRange,
      invarianceCountDifference,
      floorFailures,
      baselineMaximum,
      baselineMaximumCount,
      passingCandidates,
      reportedWinners: [],
      requiredNextStep: 'Reconsider the verb before FR-001 merges.',
    };
  }

  const highestPassingTotal = Math.max(
    ...passingCandidates.map((arm) => arms[arm].oldExpiredTotal),
  );
  const highestPassingMean = highestPassingTotal / GROUNDED_DENOMINATOR;
  const reportedWinners = passingCandidates.filter(
    (arm) =>
      highestPassingTotal - arms[arm].oldExpiredTotal <= WINNER_BAND_MAX_COUNT_DIFFERENCE,
  );
  return {
    status: reportedWinners.length > 1 ? 'escalate' : 'single-reported-winner',
    reason:
      reportedWinners.length > 1
        ? 'multiple-passing-arms-within-inclusive-winner-band'
        : 'one-passing-arm-in-inclusive-winner-band',
    invarianceRange,
    invarianceCountDifference,
    floorFailures,
    baselineMaximum,
    baselineMaximumCount,
    passingCandidates,
    highestPassingMean,
    highestPassingTotal,
    reportedWinners,
    selectedArm: reportedWinners.length === 1 ? reportedWinners[0] : null,
  };
}

function responseMap(entry) {
  return new Map(entry.successfulResult.parsed.map((item) => [item.id, item.value]));
}

function measureObservations(observations, answerKey) {
  assertComplete(observations, { requireUsageReadings: true });
  const keyedLines = answerKey.lines;
  const oldIds = keyedLines.filter((line) => line.state === 'old-grounded').map((line) => line.id);
  const recentIds = keyedLines
    .filter((line) => line.state === 'recent-grounded')
    .map((line) => line.id);
  const objectiveControls = keyedLines.filter((line) => line.objectivePile !== null);
  if (oldIds.length !== 14 || recentIds.length !== 14 || objectiveControls.length !== 9) {
    fail(
      `answer-key scoring census differs: old=${oldIds.length} recent=${recentIds.length} ` +
        `objective_controls=${objectiveControls.length}`,
    );
  }

  const arms = {};
  for (const arm of ARM_IDS) {
    const pileEntries = observations.entries.filter(
      (entry) => entry.arm === arm && entry.trialType === 'pile-sort',
    );
    const actionEntries = observations.entries.filter(
      (entry) => entry.arm === arm && entry.trialType === 'action',
    );
    if (pileEntries.length !== 20 || actionEntries.length !== 10) {
      fail(`${arm}: expected 20 pile and 10 action entries`);
    }
    const pileTrials = pileEntries.map((entry) => {
      const responses = responseMap(entry);
      const oldExpiredCount = oldIds.filter((id) => responses.get(id) === 'Expired').length;
      const recentExpiredCount = recentIds.filter(
        (id) => responses.get(id) === 'Expired',
      ).length;
      const controlMisclassificationCount = objectiveControls.filter(
        (line) => responses.get(line.id) !== line.objectivePile,
      ).length;
      return {
        slotId: entry.slotId,
        oldExpiredCount,
        oldExpiredDenominator: GROUNDED_ROWS_PER_TRIAL,
        oldExpiredRate: oldExpiredCount / oldIds.length,
        recentExpiredCount,
        recentExpiredDenominator: GROUNDED_ROWS_PER_TRIAL,
        recentExpiredRate: recentExpiredCount / recentIds.length,
        controlMisclassificationCount,
        controlMisclassificationDenominator: OBJECTIVE_CONTROLS_PER_TRIAL,
        controlMisclassificationRate:
          controlMisclassificationCount / objectiveControls.length,
      };
    });
    const actionTrials = actionEntries.map((entry) => {
      const responses = responseMap(entry);
      const useCount = keyedLines.filter((line) => responses.get(line.id) === 'USE').length;
      return {
        slotId: entry.slotId,
        useCount,
        useDenominator: ACTION_ROWS_PER_TRIAL,
        useRate: useCount / ACTION_ROWS_PER_TRIAL,
      };
    });
    const oldCounts = pileTrials.map((trial) => trial.oldExpiredCount);
    const oldExpiredTotal = oldCounts.reduce((sum, count) => sum + count, 0);
    const recentExpiredTotal = pileTrials.reduce(
      (sum, trial) => sum + trial.recentExpiredCount,
      0,
    );
    const controlMisclassificationTotal = pileTrials.reduce(
      (sum, trial) => sum + trial.controlMisclassificationCount,
      0,
    );
    const actionUseTotal = actionTrials.reduce((sum, trial) => sum + trial.useCount, 0);
    arms[arm] = {
      pileTrials,
      actionTrials,
      oldExpiredTotal,
      oldExpiredDenominator: GROUNDED_DENOMINATOR,
      oldExpiredMean: oldExpiredTotal / GROUNDED_DENOMINATOR,
      oldExpiredMinimumCount: Math.min(...oldCounts),
      oldExpiredMinimum: Math.min(...oldCounts) / GROUNDED_ROWS_PER_TRIAL,
      oldExpiredMaximumCount: Math.max(...oldCounts),
      oldExpiredMaximum: Math.max(...oldCounts) / GROUNDED_ROWS_PER_TRIAL,
      recentExpiredTotal,
      recentExpiredDenominator: GROUNDED_DENOMINATOR,
      recentExpiredMean: recentExpiredTotal / GROUNDED_DENOMINATOR,
      controlMisclassificationTotal,
      controlMisclassificationDenominator: CONTROL_DENOMINATOR,
      controlMisclassificationMean: controlMisclassificationTotal / CONTROL_DENOMINATOR,
      actionUseTotal,
      actionUseDenominator: ACTION_DENOMINATOR,
      actionUseMean: actionUseTotal / ACTION_DENOMINATOR,
    };
  }

  const association = pearson(
    ARM_IDS.map((arm) => arms[arm].oldExpiredMean),
    ARM_IDS.map((arm) => arms[arm].actionUseMean),
  );
  return {
    schemaVersion: 1,
    consumer: 'operator',
    measurement: {
      oldAndRecent: 'Expired rates; piles 1 and 2 have no objective accuracy key',
      invariance:
        'pooled per-trial misclassification rate over five Never-grounded and four Human-authored keyed controls',
      action:
        'arm-level USE-rate aggregate only; gates nothing and supports no line-level claim',
    },
    arms,
    actionAssociation: {
      unit: 'four arm-level aggregate pairs',
      pearsonCorrelation: association,
    },
  };
}

function scoreObservations(observations, answerKey) {
  const measurement = measureObservations(observations, answerKey);
  return {
    ...measurement,
    decision: evaluateDecision(measurement.arms),
  };
}

function selfTest() {
  function arm(oldTotal, oldMinimumCount, oldMaximumCount, recentTotal, controlTotal) {
    return {
      oldExpiredTotal: oldTotal,
      oldExpiredMean: oldTotal / GROUNDED_DENOMINATOR,
      oldExpiredMinimumCount: oldMinimumCount,
      oldExpiredMinimum: oldMinimumCount / GROUNDED_ROWS_PER_TRIAL,
      oldExpiredMaximumCount: oldMaximumCount,
      oldExpiredMaximum: oldMaximumCount / GROUNDED_ROWS_PER_TRIAL,
      recentExpiredTotal: recentTotal,
      recentExpiredMean: recentTotal / GROUNDED_DENOMINATOR,
      controlMisclassificationTotal: controlTotal,
      controlMisclassificationMean: controlTotal / CONTROL_DENOMINATOR,
    };
  }
  const passingBase = {
    A: arm(112, 4, 7, 28, 4),
    B: arm(196, 9, 12, 28, 5),
    C: arm(182, 8, 11, 28, 7),
    D: arm(126, 6, 8, 28, 9),
  };
  const result = evaluateDecision(passingBase);
  if (result.status !== 'escalate' || result.reportedWinners.join(',') !== 'B,C') {
    fail('winner-band self-test failed');
  }
  const invarianceBoundary = JSON.parse(JSON.stringify(passingBase));
  invarianceBoundary.A.controlMisclassificationTotal = 0;
  invarianceBoundary.D.controlMisclassificationTotal = 18;
  if (evaluateDecision(invarianceBoundary).reason === 'invariance-control') {
    fail('inclusive invariance boundary self-test failed');
  }
  const invarianceFailure = JSON.parse(JSON.stringify(passingBase));
  invarianceFailure.A.controlMisclassificationTotal = 0;
  invarianceFailure.D.controlMisclassificationTotal = 19;
  if (evaluateDecision(invarianceFailure).reason !== 'invariance-control') {
    fail('invariance failure control did not fail');
  }
  const strictOverlap = JSON.parse(JSON.stringify(passingBase));
  strictOverlap.B.oldExpiredMinimumCount = strictOverlap.A.oldExpiredMaximumCount;
  strictOverlap.C.oldExpiredMinimumCount = strictOverlap.A.oldExpiredMaximumCount;
  if (evaluateDecision(strictOverlap).status !== 'fr-015-fails') {
    fail('strict non-overlap equality control did not fail');
  }
  const allFloorFailure = JSON.parse(JSON.stringify(passingBase));
  for (const armId of ARM_IDS) allFloorFailure[armId].recentExpiredTotal = 57;
  if (evaluateDecision(allFloorFailure).status !== 'decisive-against-feature') {
    fail('all-arm floor failure precedence self-test failed');
  }
  const partialFloorFailure = JSON.parse(JSON.stringify(passingBase));
  partialFloorFailure.B.recentExpiredTotal = 57;
  if (evaluateDecision(partialFloorFailure).reason !== 'floor-control-failed-in-some-arms') {
    fail('partial floor failure self-test failed');
  }
  const floorBoundary = JSON.parse(JSON.stringify(passingBase));
  for (const armId of ARM_IDS) floorBoundary[armId].recentExpiredTotal = 56;
  if (evaluateDecision(floorBoundary).reason?.startsWith('floor-control')) {
    fail('exact 0.20 floor boundary self-test failed');
  }
  const floorEquality = JSON.parse(JSON.stringify(passingBase));
  floorEquality.B.oldExpiredTotal = 50;
  floorEquality.B.recentExpiredTotal = 50;
  if (evaluateDecision(floorEquality).reason !== 'floor-control-failed-in-some-arms') {
    fail('recent-equals-old strict floor self-test failed');
  }
  const singleWinner = JSON.parse(JSON.stringify(passingBase));
  singleWinner.C.oldExpiredTotal = 181;
  if (
    evaluateDecision(singleWinner).status !== 'single-reported-winner' ||
    evaluateDecision(singleWinner).reportedWinners.join(',') !== 'B'
  ) {
    fail('single winner outside inclusive band self-test failed');
  }
  const precedence = JSON.parse(JSON.stringify(allFloorFailure));
  precedence.A.controlMisclassificationTotal = 0;
  precedence.D.controlMisclassificationTotal = 19;
  if (evaluateDecision(precedence).reason !== 'invariance-control') {
    fail('invariance precedence self-test failed');
  }

  const answerKey = JSON.parse(fs.readFileSync(ANSWER_KEY_PATH, 'utf8'));
  const endToEndBoundary = syntheticSuccessfulObservations();
  const oldIds = answerKey.lines
    .filter((line) => line.state === 'old-grounded')
    .map((line) => line.id);
  const recentIds = answerKey.lines
    .filter((line) => line.state === 'recent-grounded')
    .map((line) => line.id);
  const objectiveControls = answerKey.lines.filter((line) => line.objectivePile !== null);

  function setResponse(entry, id, value) {
    const response = entry.successfulResult.parsed.find((item) => item.id === id);
    if (!response) fail(`end-to-end control cannot find ${id}`);
    response.value = value;
  }

  for (const entry of endToEndBoundary.entries.filter(
    (candidate) => candidate.trialType === 'pile-sort',
  )) {
    for (const id of oldIds) setResponse(entry, id, 'Still-grounded');
    for (const id of oldIds.slice(0, 4)) setResponse(entry, id, 'Expired');
    for (const id of recentIds) setResponse(entry, id, 'Still-grounded');
    const recentCount = entry.trial <= 16 ? 3 : 2;
    for (const id of recentIds.slice(0, recentCount)) setResponse(entry, id, 'Expired');
    for (const line of objectiveControls) setResponse(entry, line.id, line.objectivePile);
    if (entry.arm === 'D' && entry.trial <= 18) {
      setResponse(entry, objectiveControls[0].id, 'Still-grounded');
    }
  }
  const endToEndResult = scoreObservations(endToEndBoundary, answerKey);
  const endToEndMeasurement = measureObservations(endToEndBoundary, answerKey);
  if (
    Object.hasOwn(endToEndMeasurement, 'decision') ||
    endToEndMeasurement.arms.D.controlMisclassificationTotal !== 18 ||
    ARM_IDS.some(
      (armId) =>
        endToEndMeasurement.arms[armId].recentExpiredTotal !== 56 ||
        endToEndMeasurement.arms[armId].oldExpiredDenominator !== 280 ||
        endToEndMeasurement.arms[armId].recentExpiredDenominator !== 280 ||
        endToEndMeasurement.arms[armId].controlMisclassificationDenominator !== 180 ||
        endToEndMeasurement.arms[armId].actionUseDenominator !== 410 ||
        endToEndMeasurement.arms[armId].actionTrials.some(
          (trial) => trial.useDenominator !== ACTION_ROWS_PER_TRIAL,
        ),
    )
  ) {
    fail('measureObservations raw-only self-test failed');
  }
  if (
    endToEndResult.decision.reason === 'invariance-control' ||
    endToEndResult.decision.reason?.startsWith('floor-control') ||
    endToEndResult.arms.D.controlMisclassificationTotal !== 18 ||
    endToEndResult.arms.A.controlMisclassificationTotal !== 0 ||
    ARM_IDS.some((armId) => endToEndResult.arms[armId].recentExpiredTotal !== 56)
  ) {
    fail('scoreObservations exact-boundary self-test failed');
  }

  const endToEndInvarianceFailure = structuredClone(endToEndBoundary);
  const dTrial19 = endToEndInvarianceFailure.entries.find(
    (entry) => entry.trialType === 'pile-sort' && entry.arm === 'D' && entry.trial === 19,
  );
  setResponse(dTrial19, objectiveControls[0].id, 'Still-grounded');
  if (
    scoreObservations(endToEndInvarianceFailure, answerKey).decision.reason !==
    'invariance-control'
  ) {
    fail('scoreObservations 19/180 invariance control did not fail');
  }

  const endToEndFloorFailure = structuredClone(endToEndBoundary);
  const bTrial20 = endToEndFloorFailure.entries.find(
    (entry) => entry.trialType === 'pile-sort' && entry.arm === 'B' && entry.trial === 20,
  );
  setResponse(bTrial20, recentIds[2], 'Expired');
  if (
    scoreObservations(endToEndFloorFailure, answerKey).decision.reason !==
    'floor-control-failed-in-some-arms'
  ) {
    fail('scoreObservations 57/280 recent-floor control did not fail');
  }
  console.log('scorer-self-test winner-band=B,C');
  console.log('scorer-self-test invariance-count-difference=18 denominator=180 accepted=true');
  console.log('scorer-self-test invariance-count-difference=19 denominator=180 invalid=true');
  console.log('scorer-self-test strict-equality passes=false');
  console.log('scorer-self-test all-floor-failure=decisive-against-feature');
  console.log('scorer-self-test partial-floor-failure=invalid');
  console.log('scorer-self-test recent-floor-count=56 denominator=280 accepted=true');
  console.log('scorer-self-test recent-equals-old fails=true');
  console.log('scorer-self-test winner-count-difference=14 denominator=280 included=true');
  console.log('scorer-self-test winner-count-difference=15 denominator=280 winner=B');
  console.log('scorer-self-test invariance-precedence=true');
  console.log(
    'scorer-self-test scoreObservations exact=18/180,56/280 accepted=true controls=19/180,57/280 failed=true',
  );
  console.log(
    'scorer-self-test measureObservations decision_present=false denominators=280,280,180,410',
  );
  console.log('scorer-self-test PASS');
}

function main() {
  const command = process.argv[2];
  if (command === 'self-test') return selfTest();
  if (command === 'measure') {
    const observations = JSON.parse(fs.readFileSync(OBSERVATIONS_PATH, 'utf8'));
    const answerKey = JSON.parse(fs.readFileSync(ANSWER_KEY_PATH, 'utf8'));
    const result = measureObservations(observations, answerKey);
    if (Object.hasOwn(result, 'decision')) {
      fail('measurement result unexpectedly contains a decision');
    }
    console.log(JSON.stringify(result, null, 2));
    return;
  }
  if (command === 'score') {
    const observations = JSON.parse(fs.readFileSync(OBSERVATIONS_PATH, 'utf8'));
    const answerKey = JSON.parse(fs.readFileSync(ANSWER_KEY_PATH, 'utf8'));
    console.log(JSON.stringify(scoreObservations(observations, answerKey), null, 2));
    return;
  }
  fail('usage: node scorer.js self-test|measure|score');
}

if (require.main === module) {
  try {
    main();
  } catch (error) {
    console.error(`scorer FAIL: ${error.message}`);
    process.exitCode = 1;
  }
}

module.exports = { evaluateDecision, measureObservations, scoreObservations };
