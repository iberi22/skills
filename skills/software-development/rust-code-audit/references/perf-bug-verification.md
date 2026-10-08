# Verifying a performance fix in a live Rust service

Use when a fix targets a CPU/IO hot loop in a running service, and local tests already pass.

The failure mode this prevents: a green suite, a committed fix, and a service that is still
slow — because the fix covered one instance of a pattern the codebase repeats.

## 1. Fingerprint the cost before touching code

```bash
PID=$(systemctl --user show <svc>.service -p MainPID --value)
grep -E 'rchar|syscr' /proc/$PID/io          # bytes read / read syscalls
ps -o pcpu,rss,etime -p $PID                  # CPU and uptime
uptime                                       # system load
```

A `rchar / syscr` ratio pinned to a power of two (~4096) means page-sized reads from a
database, not compute. That points at a per-record query, not at an expensive algorithm.

A process that is already hot minutes after start was never degrading — it is steady-state
cost against a corpus that grows. Do not frame it as a leak.

## 2. Isolate by disabling one subsystem

Prefer an existing kill switch in the code over patching. Background loops usually document
one:

```bash
grep -n 'EMERGENCY\|DISABLED\|_INTERVAL_SECS' src/<service>.rs
```

Apply it as a systemd drop-in so it is reversible without touching the repo:

```bash
printf '[Service]\nEnvironment=<VAR>=0\n' > ~/.config/systemd/user/<svc>.service.d/diag.conf
systemctl --user daemon-reload && systemctl --user restart <svc>.service
tr '\0' '\n' < /proc/$PID/environ | grep <VAR>   # prove the process has it
```

Keep the mitigation in place while you develop the fix. Deploy without it only to measure,
and restore it immediately after the measurement.

## 3. Find every instance of the pattern, not the one you fixed

```bash
grep -rc 'store\.get(' src/<component>/ | grep -v ':0'
```

Count > 1 means the bug is N instances of one shape. Fixing one leaves the service at the
same cost and the suite at the same green.

## 4. Read the live log to attribute cost

```bash
journalctl --user -u <svc>.service --since '10 min ago' --no-pager | grep -i <stage>
```

Stages that log a completion timestamp are measurable. A loop that prints A at T+17s, B at
T+37s and never prints C tells you B consumed ~20s and C is where it stalls. Compare against
what your fix targeted — if the targeted stage now costs nothing and the symptom persists,
the remaining stages are the cause.

## 5. Separate the two intents before caching

An incremental skip breaks any caller that expects a full count. Split the entry points:

- **explicit path** — always reads everything, for callers that report `count` to a user
- **incremental path** — skips unchanged files, for background loops that discard the result
- **force path** — ignores the cache, as the reconciliation hatch

Deciding whether a file changed costs one `stat`; the previous code instead opened the file
and asked the store about every record inside it.

The reconciliation hatch is mandatory, not optional: `rsync -t`, `tar` and `mv` all preserve
an old mtime, so a file rewritten that way is skipped forever. Nothing detects this
automatically — say so in the doc comment rather than implying the cache is authoritative.

## 6. Gate the test on the cost, not the output

Count the expensive operation, not the result. A test asserting "the records still come back"
passes on a system that queries the store for every record.

```rust
let second = importer.sync(&store).await?;
assert_eq!(second.store_reads, 0, "unchanged corpus must not query the store");
```

The stats struct needs a `store_reads` counter for this. If the counter lives in a test-only
wrapper reimplementing a large trait, it will drift — count in production code and assert on
it instead.

## 7. Prove the test guards the fix

Revert the mitigation, expect red, restore. If it stays green, the invariant is not reachable
from any test — extract a named function or constant that production calls, then assert on
that. Never weaken the assertion to get green.

## 8. Deploy the verified feature set

A release build with a reduced feature set is a different binary. Before replacing a running
node's binary:

```bash
# symbol counts for the feature's types, old vs new
nm -C <installed> | grep -ci '<feature>::'
nm -C <new>      | grep -ci '<feature>::'
```

A large file-size delta with equal symbol counts is usually `lto`/`codegen-units` drift.
A missing feature's symbols mean the new binary silently dropped that subsystem.

## 9. Post-deploy gates

```bash
systemctl --user show <svc>.service -p NRestarts -p MainPID   # NRestarts=0 => no CrashLoopBackOff
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:<port>/health
```

Then re-measure the same counters from step 1 over the same interval. That comparison, not the
suite, is what closes the phase.