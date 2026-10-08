# Equivalence sandbox recipe

A runnable pattern for proving a refactor changed nothing. Adapt paths; keep the shape:
two isolated directories, one seeded from the pre-change revision, both fed identical
input, compared byte-for-byte.

## 1. Seed from the PRE-change revision

```bash
git show <pre-change-sha>:<path/to/file> > /tmp/eq/old/<file>
```

Assert the seed is clean. This assertion is the whole point — it is what distinguishes a
real check from a vacuous one:

```python
assert "studies:" not in r.stdout, f"{f} already had it — wrong seed"
```

If that assertion fires, you seeded from HEAD instead of the pre-change commit. Fix the
sha, not the assertion.

## 2. Apply old code, snapshot

```bash
cd /tmp/eq && <run old script> --apply
mv <content-dir> /tmp/eq/old-out
```

## 3. Apply new code to identical input

```bash
git show <pre-change-sha>:<path/to/file> > /tmp/eq/new/<file>   # re-seed, same source
cd /tmp/eq && <run new script> --apply
```

Re-seeding matters: running new-code-onto-old-output tests a different thing (and would
trip the idempotency guard instead of the writer).

## 4. Compare

```bash
diff -r /tmp/eq/old-out /tmp/eq/new/content && echo "byte-identical"
```

In Python, for the count to report:

```python
same = diff = 0
for f in files:
    if open(a, encoding="utf-8").read() == open(b, encoding="utf-8").read():
        same += 1
    else:
        diff += 1
        if diff <= 2:
            for l in list(difflib.unified_diff(a_lines, b_lines, lineterm=""))[:10]:
                print(l)
print(f"byte-identical: {same} | distintos: {diff}")
```

Always print the first couple of diffs. The count tells you it failed; the diff tells you
why, and "why" is usually one blank line or one indent width.

## 5. Pure-function corpus check

Load both versions as modules and compare over the whole tree:

```python
import importlib.util
def load(src, name):
    p = f"/tmp/eq/{name}.py"; open(p, "w").write(src)
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

old = load(git_show_pre_change, "old")
new = load(open(current_path).read(), "new")

same = diff = 0
for f in glob_all_files():
    fm = split_frontmatter(open(f, encoding="utf-8").read())
    if old.parse(fm) == new.parse(fm):
        same += 1
    else:
        diff += 1
print(f"{same} identicas | {diff} diferentes")
```

`0 diferentes` across the full corpus is the reportable number. Sample-based spot checks
miss the malformed inputs that live at the edges of the collection.

## 6. Idempotency

```bash
<run script>            # second time, same content
# must report: 0 written, N already had it
```

If it writes again, the "already has it" guard is broken — it will double-append on every
future run. Fix before committing.

## Cleanup

```bash
rm -rf /tmp/eq
```
