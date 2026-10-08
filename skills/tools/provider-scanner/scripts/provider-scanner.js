#!/usr/bin/env node
/**
 * provider-scanner.js — RF-006 SWAL Provider Scanner (OpenClaw skill)
 *
 * Escanea CLIs reales (aws, gh, docker, kubectl): versión, credenciales,
 * quotas/rate-limits. Sin mocks. Output: /tmp/providers-report.json
 *
 *   node provider-scanner.js [--output /tmp/providers-report.json]
 */
"use strict";

const { execFile } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { promisify } = require("util");

const execFileAsync = promisify(execFile);
const SCHEMA_VERSION = "1.0";
const DEFAULT_OUTPUT = "/tmp/providers-report.json";
const TIMEOUT = 8_000;

async function run(cmd, args) {
  try {
    const { stdout, stderr } = await execFileAsync(cmd, args, {
      timeout: TIMEOUT,
      maxBuffer: 2 * 1024 * 1024,
      env: process.env,
    });
    return { ok: true, stdout: String(stdout || "").trim(), stderr: String(stderr || "").trim() };
  } catch (err) {
    return {
      ok: false,
      stdout: String((err && err.stdout) || "").trim(),
      stderr: String((err && err.stderr) || err.message || "").trim(),
      code: err && (err.code ?? err.status),
    };
  }
}

function line(text) {
  return String(text || "").split(/\r?\n/).map((l) => l.trim()).find(Boolean) || "";
}

function json(text) {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

async function which(bin) {
  const r = await run("sh", ["-c", `command -v ${bin}`]);
  return r.ok && r.stdout ? r.stdout : null;
}

async function scanAws() {
  const bin = await which("aws");
  if (!bin) return { name: "aws", available: false, version: null, credentialsPresent: false };
  const ver = await run("aws", ["--version"]);
  const version = line(ver.stdout || ver.stderr) || null;
  const ident = await run("aws", ["sts", "get-caller-identity", "--output", "json"]);
  const identity = ident.ok ? json(ident.stdout) : null;
  const credentialsPresent = Boolean(identity && identity.Account);
  let quota = null;
  if (credentialsPresent) {
    const q = await run("aws", [
      "service-quotas", "list-service-quotas",
      "--service-code", "ec2", "--max-items", "5", "--output", "json",
    ]);
    const qj = q.ok ? json(q.stdout) : null;
    if (qj && Array.isArray(qj.Quotas) && qj.Quotas.length) {
      quota = {};
      for (const item of qj.Quotas) {
        if (item.QuotaName != null && item.Value != null) {
          quota[String(item.QuotaName).replace(/\s+/g, "")] = item.Value;
        }
      }
    }
  }
  return {
    name: "aws", available: credentialsPresent, version, credentialsPresent, path: bin, cliPresent: true,
    identity: identity ? { account: identity.Account, arn: identity.Arn, userId: identity.UserId } : null,
    quota,
    error: credentialsPresent ? null : ident.stderr || "no credentials / sts failed",
  };
}

async function scanGh() {
  const bin = await which("gh");
  if (!bin) return { name: "github", available: false, version: null, credentialsPresent: false };
  const ver = await run("gh", ["--version"]);
  const version = line(ver.stdout) || null;
  const auth = await run("gh", ["auth", "status"]);
  const credentialsPresent = auth.ok || /Logged in to/i.test(auth.stderr + auth.stdout);
  let rateLimit = null;
  if (credentialsPresent) {
    const rl = await run("gh", ["api", "rate_limit", "--jq", "."]);
    const core = (json(rl.stdout) || {}).resources?.core;
    if (core) {
      rateLimit = {
        remaining: core.remaining,
        limit: core.limit,
        reset: core.reset ? new Date(core.reset * 1000).toISOString() : null,
      };
    }
  }
  return {
    name: "github", available: credentialsPresent, version, credentialsPresent, path: bin, cliPresent: true, rateLimit,
    error: credentialsPresent ? null : line(auth.stderr || auth.stdout) || "not authenticated",
  };
}

async function scanDocker() {
  const bin = await which("docker");
  if (!bin) return { name: "docker", available: false, version: null, credentialsPresent: false };
  const verFmt = await run("docker", ["version", "--format", "{{.Client.Version}}"]);
  const version = verFmt.ok ? line(verFmt.stdout) : line((await run("docker", ["--version"])).stdout);
  const info = await run("docker", ["info", "--format", "{{json .}}"]);
  const ij = info.ok ? json(info.stdout) : null;
  const daemonUp = Boolean(
    ij &&
      ij.ServerVersion &&
      !(Array.isArray(ij.ServerErrors) && ij.ServerErrors.length) &&
      !/Cannot connect to the Docker daemon/i.test(info.stderr || ""),
  );
  return {
    name: "docker",
    available: daemonUp,
    version: version || null,
    credentialsPresent: daemonUp,
    cliPresent: true,
    path: bin,
    info: ij ? {
      containers: ij.Containers, images: ij.Images,
      serverVersion: ij.ServerVersion || null, operatingSystem: ij.OperatingSystem || null,
    } : null,
    error: daemonUp ? null : line(info.stderr) || "docker daemon unreachable",
  };
}

async function scanKubectl() {
  const bin = await which("kubectl");
  if (!bin) return { name: "kubectl", available: false, version: null, credentialsPresent: false };
  const ver = await run("kubectl", ["version", "--client", "-o", "json"]);
  const vj = ver.ok ? json(ver.stdout) : null;
  const version = vj?.clientVersion?.gitVersion
    || line((await run("kubectl", ["version", "--client"])).stdout) || null;
  const cfg = await run("kubectl", ["config", "current-context"]);
  const credentialsPresent = cfg.ok && Boolean(cfg.stdout);
  return {
    name: "kubectl", available: true, version, credentialsPresent, path: bin,
    currentContext: credentialsPresent ? cfg.stdout : null,
    error: credentialsPresent ? null : line(cfg.stderr) || "no kube context",
  };
}

async function scanEnvironment() {
  let availableDisk = null;
  const df = await run("df", ["-B1", "--output=avail", "/"]);
  if (df.ok) {
    const lines = df.stdout.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
    const avail = Number(lines[lines.length - 1]);
    if (Number.isFinite(avail)) availableDisk = `${(avail / 1024 ** 3).toFixed(1)}GB`;
  }
  return {
    os: `${os.platform()} ${os.release()}`,
    arch: os.arch(),
    hostname: os.hostname(),
    totalRam: `${(os.totalmem() / 1024 ** 3).toFixed(1)}GB`,
    freeRam: `${(os.freemem() / 1024 ** 3).toFixed(1)}GB`,
    availableDisk,
    hasDocker: Boolean(await which("docker")),
    node: process.version,
  };
}

function parseArgs(argv) {
  let output = DEFAULT_OUTPUT;
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--output" && argv[i + 1]) output = path.resolve(argv[++i]);
  }
  return { output };
}

async function main() {
  const started = Date.now();
  const { output } = parseArgs(process.argv.slice(2));
  const [aws, github, docker, kubectl, environment] = await Promise.all([
    scanAws(), scanGh(), scanDocker(), scanKubectl(), scanEnvironment(),
  ]);
  const report = {
    schemaVersion: SCHEMA_VERSION,
    scannedAt: new Date().toISOString(),
    durationMs: Date.now() - started,
    providers: [aws, github, docker, kubectl],
    environment,
  };
  fs.writeFileSync(output, JSON.stringify(report, null, 2) + "\n", "utf8");
  process.stdout.write(`Wrote ${output} (${report.providers.length} providers, ${report.durationMs}ms)\n`);
  return report;
}

if (require.main === module) {
  main().catch((err) => {
    console.error("provider-scanner failed:", err);
    process.exit(1);
  });
}

module.exports = { main, scanAws, scanGh, scanDocker, scanKubectl, SCHEMA_VERSION };
