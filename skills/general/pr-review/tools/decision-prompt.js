#!/usr/bin/env node

/**
 * Decision Prompt Generator
 * Generate interactive prompts with buttons for user decisions
 */

const DECISION_TYPES = {
  binary: {
    name: 'Binary Decision',
    format: (title, options) => `${title}\n\n[${options[0]}] [${options[1]}]`
  },
  multi: {
    name: 'Multi-option',
    format: (title, options) => {
      const opts = options.map((o, i) => `[${String.fromCharCode(65 + i)}] ${o}`).join('  ');
      return `${title}\n\n${opts}`;
    }
  },
  override: {
    name: 'Override with Justification',
    format: (title, options) => {
      return `${title}\n\n${options.join(' | ')}`;
    }
  },
  severity: {
    name: 'Security Severity',
    format: (title, options) => {
      return `🚨 ${title}\n\n${options.join('\n')}`;
    }
  }
};

/**
 * Generate a decision prompt
 */
function generateDecision(decision) {
  const { type, title, options, severity } = decision;
  
  let emoji = '';
  if (severity === 'critical') emoji = '🚨';
  else if (severity === 'high') emoji = '⚠️';
  else if (severity === 'medium') emoji = '⚡';
  else emoji = '📋';
  
  const formatted = DECISION_TYPES[type]?.format(title, options) || title;
  
  return {
    id: decision.id || `dec_${Date.now()}`,
    type: decision.type,
    title: `${emoji} ${title}`,
    formatted,
    options: options.map((label, i) => ({
      label,
      action: decision.actions?.[i] || `action_${i}`,
      style: getButtonStyle(label, severity)
    })),
    requiresJustification: type === 'override',
    severity
  };
}

/**
 * Get button style based on label
 */
function getButtonStyle(label, severity) {
  const lower = label.toLowerCase();
  
  if (lower.includes('approve') || lower.includes('proceed') || lower.includes('yes') || lower.includes('ok')) {
    return 'success';
  }
  if (lower.includes('reject') || lower.includes('abort') || lower.includes('no') || lower.includes('block')) {
    return 'danger';
  }
  if (lower.includes('override') || lower.includes('acknowledge')) {
    return 'warning';
  }
  return 'default';
}

/**
 * Generate PR review decision points
 */
function generatePRDecisions(prData) {
  const decisions = [];
  
  // Security findings
  if (prData.security?.critical > 0) {
    decisions.push({
      type: 'severity',
      severity: 'critical',
      title: `${prData.security.critical} CRITICAL security vulnerabilities found`,
      options: ['🛡️ Override', '❌ Block Merge'],
      actions: ['override', 'block']
    });
  }
  
  // Breaking changes
  if (prData.breaking) {
    decisions.push({
      type: 'binary',
      severity: 'high',
      title: `Breaking change detected in ${prData.breaking.files?.join(', ')}`,
      options: ['✅ Proceed', '❌ Abort'],
      actions: ['proceed', 'abort']
    });
  }
  
  // New dependencies
  if (prData.newDependencies?.length > 0) {
    decisions.push({
      type: 'multi',
      severity: 'medium',
      title: `New dependencies: ${prData.newDependencies.join(', ')}`,
      options: prData.newDependencies.map(d => `✅ ${d}`),
      actions: prData.newDependencies.map(d => `approve_${d}`)
    });
  }
  
  // Coverage drop
  if (prData.coverageDrop > 5) {
    decisions.push({
      type: 'binary',
      severity: 'medium',
      title: `Test coverage dropped ${prData.coverageDrop}% (was ${prData.coverageBefore}%, now ${prData.coverageAfter}%)`,
      options: ['✅ Proceed', '❌ Abort'],
      actions: ['proceed', 'abort']
    });
  }
  
  // Complex refactor
  if (prData.complexity > 10) {
    decisions.push({
      type: 'override',
      severity: 'low',
      title: `Complex refactor: ${prData.changes} files changed, ${prData.additions} additions, ${prData.deletions} deletions`,
      options: ['🔍 Review Code', '✅ Acknowledge'],
      actions: ['review', 'acknowledge']
    });
  }
  
  return decisions;
}

/**
 * Format decision for display
 */
function formatDecision(decision, index) {
  const formatted = generateDecision(decision);
  
  return `
${index + 1}. ${formatted.title}
${formatted.options.map(o => `   ${o.label}`).join('\n')}
`;
}

/**
 * Main - generate full PR decision report
 */
function generatePRReport(prData) {
  console.log('══════════════════════════════════════════');
  console.log(`🔍 PR #${prData.number}: ${prData.title}`);
  console.log('══════════════════════════════════════════\n');
  
  console.log(`📁 Files: ${prData.files} changed (+${prData.additions}, -${prData.deletions})\n`);
  
  console.log('──────────────────────────────────────────');
  console.log('🔒 SECURITY');
  console.log('──────────────────────────────────────────');
  if (prData.security) {
    if (prData.security.critical > 0) console.log(`🔴 Critical: ${prData.security.critical}`);
    if (prData.security.high > 0) console.log(`🟠 High: ${prData.security.high}`);
    if (prData.security.medium > 0) console.log(`🟡 Medium: ${prData.security.medium}`);
    if (prData.security.low > 0) console.log(`🟢 Low: ${prData.security.low}`);
  } else {
    console.log('✅ No issues');
  }
  console.log('');
  
  console.log('──────────────────────────────────────────');
  console.log('📊 CODE QUALITY');
  console.log('──────────────────────────────────────────');
  console.log(`Linting: ${prData.lint === 'pass' ? '✅ Pass' : '❌ Fail'}`);
  console.log(`Tests: ${prData.tests.passed}/${prData.tests.total} (${prData.tests.coverage}%)`);
  console.log('');
  
  const decisions = generatePRDecisions(prData);
  
  if (decisions.length > 0) {
    console.log('──────────────────────────────────────────');
    console.log('⚡ DECISION REQUIRED');
    console.log('──────────────────────────────────────────\n');
    
    decisions.forEach((d, i) => {
      console.log(formatDecision(d, i));
    });
  }
  
  console.log('──────────────────────────────────────────');
  console.log('📋 SUMMARY');
  console.log('──────────────────────────────────────────');
  console.log(`Merge: ${decisions.length > 0 ? '⚠️ REQUIRES APPROVAL' : '✅ READY'}`);
  console.log('');
  
  return decisions;
}

// Example usage
const samplePR = {
  number: 42,
  title: 'Add payment integration',
  files: 12,
  additions: 234,
  deletions: 89,
  security: { critical: 0, high: 1, medium: 2, low: 3 },
  lint: 'pass',
  tests: { passed: 45, total: 48, coverage: 93 },
  coverageDrop: 2,
  newDependencies: ['stripe@14.0.0'],
  breaking: { files: ['src/payment.ts'] },
  complexity: 8
};

if (require.main === module) {
  generatePRReport(samplePR);
}

module.exports = { generateDecision, generatePRDecisions, formatDecision, generatePRReport };
