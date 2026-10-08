#!/usr/bin/env node

/**
 * PR Security Scanner
 * Scan PR for security vulnerabilities
 */

const { execSync } = require('child_process');

const SEVERITY_LEVELS = {
  critical: { score: 4, emoji: '🔴' },
  high: { score: 3, emoji: '🟠' },
  medium: { score: 2, emoji: '🟡' },
  low: { score: 1, emoji: '🟢' }
};

/**
 * Run npm audit on a project
 */
function npmAudit(cwd) {
  try {
    const output = execSync('npm audit --json', { 
      cwd, 
      encoding: 'utf8',
      stdio: ['pipe', 'pipe', 'pipe']
    });
    return JSON.parse(output);
  } catch (e) {
    try {
      return JSON.parse(e.stdout || '{}');
    } catch {
      return { vulnerabilities: {} };
    }
  }
}

/**
 * Run pip audit if Python
 */
function pipAudit(cwd) {
  try {
    const output = execSync('pip-audit --format=json', { 
      cwd, 
      encoding: 'utf8',
      stdio: ['pipe', 'pipe', 'pipe']
    });
    return JSON.parse(output);
  } catch {
    return { dependencies: [] };
  }
}

/**
 * Scan for secrets in git
 */
function scanSecrets(cwd) {
  const findings = [];
  
  try {
    // Check for exposed secrets in git history
    const output = execSync('git log --all -p --full-history --source --remotes --full -S "api_key" -- "*.js" "*.ts" "*.py" "*.env" 2>/dev/null | head -100', {
      cwd,
      encoding: 'utf8'
    });
    
    if (output && output.length > 100) {
      findings.push({
        type: 'potential_secret',
        severity: 'HIGH',
        description: 'Potential API key found in git history'
      });
    }
  } catch {}
  
  return findings;
}

/**
 * Analyze package.json for outdated deps
 */
function checkDependencies(cwd) {
  const findings = [];
  
  try {
    const output = execSync('npm outdated --json', { 
      cwd, 
      encoding: 'utf8',
      stdio: ['pipe', 'pipe', 'pipe']
    });
    const outdated = JSON.parse(output || '{}');
    
    Object.entries(outdated).forEach(([pkg, info]) => {
      if (info.type === 'major') {
        findings.push({
          type: 'outdated_major',
          package: pkg,
          current: info.current,
          latest: info.latest,
          severity: 'MEDIUM',
          description: `Major version outdated: ${pkg}`
        });
      }
    });
  } catch {}
  
  return findings;
}

/**
 * Main security scan
 */
async function runSecurityScan(repoPath, options = {}) {
  console.log('🔒 Running security scan...\n');
  
  const results = {
    timestamp: new Date().toISOString(),
    vulnerabilities: [],
    secrets: [],
    dependencies: [],
    summary: { critical: 0, high: 0, medium: 0, low: 0 }
  };
  
  // Run scans
  try {
    const npmResult = npmAudit(repoPath);
    if (npmResult.vulnerabilities) {
      Object.entries(npmResult.vulnerabilities).forEach(([severity, vulns]) => {
        if (Array.isArray(vulns)) {
          vulns.forEach(v => {
            results.vulnerabilities.push({
              type: 'npm',
              package: v.name,
              severity,
              title: v.title || v.name,
              url: v.url
            });
            results.summary[severity] = (results.summary[severity] || 0) + 1;
          });
        }
      });
    }
  } catch (e) {
    console.log('⚠️ npm audit not available\n');
  }
  
  // Check dependencies
  results.dependencies = checkDependencies(repoPath);
  
  // Scan for secrets
  results.secrets = scanSecrets(repoPath);
  
  // Print summary
  console.log('══════════════════════════════════════════');
  console.log('🔒 SECURITY SCAN RESULTS');
  console.log('══════════════════════════════════════════\n');
  
  if (results.vulnerabilities.length === 0 && results.secrets.length === 0) {
    console.log('✅ No security issues found\n');
  } else {
    if (results.summary.critical > 0) {
      console.log(`🔴 CRITICAL: ${results.summary.critical}`);
    }
    if (results.summary.high > 0) {
      console.log(`🟠 HIGH: ${results.summary.high}`);
    }
    if (results.summary.medium > 0) {
      console.log(`🟡 MEDIUM: ${results.summary.medium}`);
    }
    if (results.summary.low > 0) {
      console.log(`🟢 LOW: ${results.summary.low}`);
    }
    console.log('');
  }
  
  // Decision points
  const decisions = [];
  
  if (results.summary.critical > 0) {
    decisions.push({
      type: 'block',
      message: `🚨 ${results.summary.critical} CRITICAL vulnerabilities found`,
      options: ['🛡️ Override', '❌ Block Merge']
    });
  }
  
  if (results.summary.high > 0) {
    decisions.push({
      type: 'warning',
      message: `⚠️ ${results.summary.high} HIGH severity vulnerabilities`,
      options: ['✅ Proceed', '❌ Block']
    });
  }
  
  if (results.secrets.length > 0) {
    decisions.push({
      type: 'critical',
      message: '🔐 Potential secrets exposed in code',
      options: ['👀 Review', '✅ Acknowledge']
    });
  }
  
  if (decisions.length > 0) {
    console.log('⚡ DECISION REQUIRED:\n');
    decisions.forEach((d, i) => {
      console.log(`${i + 1}. ${d.message}`);
      console.log(`   ${d.options.join(' | ')}\n`);
    });
  }
  
  return { results, decisions };
}

// Run if called directly
const repoPath = process.argv[2] || process.cwd();
runSecurityScan(repoPath).catch(console.error);

module.exports = { runSecurityScan };
