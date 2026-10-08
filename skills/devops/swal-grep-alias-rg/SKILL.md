---
name: swal-grep-alias-rg
description: Use when a bash/zsh verification pipeline silently fails to filter output in SWAL desktop.
version: 1.0.0
---

# `grep` is an alias for `rg` on this machine

## The trap

`zsh` on this desktop has `alias grep=rg`. Ripgrep does **not** implement
GNU's `-E` / `--extended-regexp`; it reads `-E` as `--encoding`, so:

```bash
grep -E '^  FAIL' out.txt
# rg: error parsing flag -E: grep config error: unknown encoding: FAIL
```

This fails **silently in the worst way**: inside a pipeline the error goes to
stderr and the command produces nothing, so a check that was filtering output
appears to pass with zero matches. It cost a whole verification round before it
was spotted — a negative control reported "0 FAILs" because its own filter was
broken, not because the code was clean.

## Rules

- **In scripts**: shebang `#!/usr/bin/env bash` and the alias does not apply —
  the script body runs in bash, not zsh. Plain `grep '^  FAIL'` is safe there.
- **In ad-hoc `terminal` commands**: never `grep -E` / `grep --extended-regexp`.
  Prefer `rg` directly (`rg '^  FAIL'`), which is what the alias resolves to.
- **Verify the filter before trusting it**: `echo 'a FAIL b' | grep 'FAIL'`
  must print a line. A filter that returns nothing on a known match is broken,
  not proof of a clean result.
- **Prefer `rg -c`** for counts; it is unambiguous about what it matched.

## Related

- Same class of bug: piping to `head`/`tail` hides a script's real exit code
  (`$?` is the pipe's last command). Capture to a file, then read the file.
