---
id: sqlite-pro
name: sqlite-pro
category: tools
tags:
  - sqlite-pro
goals:
  - "Advanced SQLite skill for AI agents — vector search, hybrid retrieval, knowledge graphs, and SQLite 3.53.0+ features. Use when working with: (1) Building AI agent memory systems with SQLite backend, (2) Implementing vector similarity search using sqlite-vec or sqlite-vector, (3) Setting up FTS5 full-text search with hybrid retrieval (vector + keyword), (4) Creating knowledge graphs with recursive CTEs, (5) Implementing RRF (Reciprocal Rank Fusion) for result fusion, (6) Using QJL two-pass compression for scalable vector search, (7) Ed25519-signed hash chains for tamper-evident memory, (8) Leveraging SQLite 3.53.0 features: ALTER TABLE constraints, REINDEX EXPRESSIONS, JSON array functions, WAL optimizations, or (9) Any SQLite-backed persistent memory, RAG pipeline, or edge AI storage system."
authors:
  - Brahyan Belalcazar
---

# SQLite PRO

Advanced SQLite patterns for AI agent memory, vector search, and edge AI storage. Built for SQLite 3.53.0+.

## Core Architecture (Three Pillars)

```
Query Input
    │
    ├──▶ FTS5 (keyword/exact match) ──┐
    ├──▶ Vector Search (sqlite-vec/sqai-vector) ─┤──▶ RRF Fusion ──▶ Ranked Results
    └──▶ Knowledge Graph (entities/relations) ──┘
```

## Quick Start

### 1. Choose Vector Engine
```bash
# Option A: sqlite-vec (pre-v1, simpler, partitions)
.load ./vec0
CREATE VIRTUAL TABLE mem USING vec0(embedding float[768]);

# Option B: sqlite-vector (sqliteai, no virtual tables, SIMD, quantization)
SELECT load_extension('./vector');
CREATE TABLE entries (id TEXT PRIMARY KEY, embedding BLOB);
SELECT vector_init('entries', 'embedding', 'type=FLOAT32,dimension=768,distance=COSINE');
```

### 2. Set Up Schema
```sql
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    path TEXT,
    content TEXT NOT NULL,
    metadata TEXT,  -- JSON
    embedding BLOB,  -- Float32 vector (768-dim)
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    revision INTEGER DEFAULT 1,
    parent_id TEXT,
    revisions TEXT,  -- JSON array
    content_hash TEXT  -- For verification
);

CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
    id UNINDEXED, path UNINDEXED, content,
    content_rowid='id'
);

CREATE VIRTUAL TABLE IF NOT EXISTS memory_vec USING vec0(
    embedding float[768],
    PRIMARY KEY (id, workspace_id)
);
```

### 3. Insert with Vector Sync
```sql
-- In a transaction: memory + vector
BEGIN IMMEDIATE;
INSERT INTO memories (id, workspace_id, content, embedding) VALUES (?, ?, ?, ?);
INSERT INTO memory_vec (rowid, embedding) 
    VALUES ((SELECT rowid FROM memories WHERE id = ?), vector_from_json(?));
COMMIT;
```

### 4. Hybrid Search (RRF)
```sql
WITH ranked AS (
    SELECT id, 'vec' AS source, 1/(60 + ROW_NUMBER() OVER (ORDER BY distance)) AS score
    FROM memory_vec WHERE embedding knn_search(vector_from_json(?), 10)
), fts_ranked AS (
    SELECT id, 'fts' AS source, 1/(60 + ROW_NUMBER() OVER (ORDER BY rank)) AS score
    FROM memory_fts WHERE content MATCH ?
)
SELECT m.*, SUM(r.score) AS final_score
FROM memories m
JOIN (
    SELECT id, score FROM ranked UNION ALL SELECT id, score FROM fts_ranked
) r ON m.id = r.id
GROUP BY m.id
ORDER BY final_score DESC LIMIT 10;
```

---

## SQLite 3.53.0 — Key New Features

### ALTER TABLE Constraints (Game Changer)
```sql
-- Add NOT NULL without rewriting table
ALTER TABLE t ADD COLUMN col TEXT NOT NULL DEFAULT 'default';

-- Add CHECK constraint
ALTER TABLE t ADD COLUMN col TEXT CHECK(col IS NOT NULL);

-- Drop constraint
ALTER TABLE t DROP CONSTRAINT constraint_name;
```

### REINDEX EXPRESSIONS
Repairs stale expression indexes (run after schema changes):
```sql
REINDEX EXPRESSIONS;
```

### JSON Array Insert
```sql
SELECT json_array_insert('[1,2,3]', '#-1', 'new');  -- Insert at end
SELECT jsonb_array_insert('{"a":[1,2]}', '$.a.#0', 'x');  -- JSONB variant
```

### WAL Reset Fix
Critical fix for WAL-mode databases. Always use WAL mode for concurrent access:
```sql
PRAGMA journal_mode=WAL;
PRAGMA wal_autocheckpoint=1000;
```

---

## Vector Search (sqlite-vector preferred)

### sqlite-vector (sqliteai) — Best for Production
```sql
-- Initialize (no virtual tables needed!)
SELECT vector_init('entries', 'embedding', 'type=FLOAT32,dimension=768,distance=COSINE');

-- Quantize for 4-5x speedup on large datasets
SELECT vector_quantize('entries', 'embedding');
SELECT vector_quantize_preload('entries', 'embedding');

-- KNN search
SELECT e.id, e.content, v.distance 
FROM entries e
JOIN vector_quantize_scan('entries', 'embedding', ?, 20) v ON e.id = v.rowid
WHERE e.workspace_id = ?
ORDER BY v.distance LIMIT 10;

-- Streaming (no k limit = all results, use SQL to filter)
SELECT e.id, v.distance FROM entries e
JOIN vector_quantize_scan('entries', 'embedding', ?) v ON e.id = v.rowid
WHERE e.workspace_id = 'ws1' AND e.type = 'doc' LIMIT 10;
```

### sqlite-vec — Simpler, Partitions Built-in
```sql
CREATE VIRTUAL TABLE mem USING vec0(
    embedding float[768],
    PRIMARY KEY (id, workspace_id)
);

INSERT INTO mem(rowid, embedding) VALUES (rowid, vector_from_json(?));
SELECT rowid, distance FROM mem WHERE embedding knn_search(?, 10);
```

### Distance Metrics
| Metric | Use Case |
|--------|----------|
| `L2` (default) | General purpose |
| `COSINE` | Semantic similarity (normalized vectors) |
| `DOT` | Recommendations, scoring |
| `HAMMING` | Binary vectors (e.g., hash embeddings) |

---

## Knowledge Graph (Multi-Hop Entity Traversal)

### Schema
```sql
CREATE TABLE entities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    entity_type TEXT,  -- 'person', 'project', 'decision'
    properties TEXT,   -- JSON
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE relations (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,  -- 'owns', 'depends_on', 'decided'
    properties TEXT,
    FOREIGN KEY (source_id) REFERENCES entities(id),
    FOREIGN KEY (target_id) REFERENCES entities(id)
);
```

### Multi-Hop Traversal
```sql
-- Find all entities 2 hops from 'project-alpha'
WITH RECURSIVE kg_traverse(id, depth, path) AS (
    SELECT target_id, 1, source_id || ',' || target_id
    FROM relations WHERE source_id = 'project-alpha'
    UNION ALL
    SELECT r.target_id, t.depth + 1, t.path || ',' || r.target_id
    FROM relations r JOIN kg_traverse t ON r.source_id = t.id
    WHERE t.depth < 5
)
SELECT DISTINCT e.id, e.name, e.entity_type, t.depth
FROM entities e JOIN kg_traverse t ON e.id = t.id
ORDER BY t.depth, e.name;
```

### Entity Search
```sql
-- "What did Alice decide about auth?"
WITH alice_decisions AS (
    SELECT DISTINCT target_id FROM relations
    WHERE source_id = (SELECT id FROM entities WHERE name = 'Alice')
    AND relation_type = 'decided'
)
SELECT e.* FROM entities e WHERE e.id IN (SELECT target_id FROM alice_decisions);
```

---

## RRF (Reciprocal Rank Fusion)

Combine multiple retrieval signals by rank, not score. Robust to scale differences.

```sql
WITH vec_signal AS (
    SELECT id, 1.0 / (60 + row_num) AS score
    FROM (
        SELECT id, ROW_NUMBER() OVER (ORDER BY distance) AS row_num
        FROM memory_vec WHERE embedding knn_search(?, 20)
    )
),
fts_signal AS (
    SELECT id, 1.0 / (60 + row_num) AS score
    FROM (
        SELECT id, ROW_NUMBER() OVER (ORDER BY rank) AS row_num
        FROM memory_fts WHERE content MATCH ?
    )
),
kg_signal AS (
    SELECT id, 1.0 / (60 + row_num) AS score
    FROM (
        SELECT id, ROW_NUMBER() OVER (ORDER BY depth) AS row_num
        FROM kg_traverse WHERE entity_type = 'decision'
    )
)
SELECT 
    COALESCE(v.id, f.id, k.id) AS id,
    COALESCE(v.score, 0) + COALESCE(f.score, 0) + COALESCE(k.score, 0) AS final_score,
    CASE WHEN v.id IS NOT NULL THEN 'vec' ELSE '' END ||
    CASE WHEN f.id IS NOT NULL THEN ',fts' ELSE '' END AS sources
FROM vec_signal v
FULL OUTER JOIN fts_signal f ON v.id = f.id
FULL OUTER JOIN kg_signal k ON COALESCE(v.id, f.id) = k.id
ORDER BY final_score DESC LIMIT 10;
```

**Why k=60?** RRF with k=60 is empirically optimal for fusing ranked lists of different sizes. Lower k = more weight to top results.

---

## Performance Checklist

- [ ] **WAL mode** — Always for concurrent access
- [ ] **Indexes before data** — CREATE INDEX first, then INSERT
- [ ] **Batch in transactions** — `BEGIN IMMEDIATE` for writes
- [ ] **mmap for reads** — `PRAGMA mmap_size = 268435456`
- [ ] **FTS5 content=** — Avoid double storage with `content_rowid`
- [ ] **WAL checkpoint** — `PRAGMA wal_checkpoint(TRUNCATE)` after batch writes
- [ ] **Prepare statements** — Reuse for repeated queries
- [ ] **Quantize vectors** — `vector_quantize()` for 4-5x speedup

---

## Hash Chain (Tamper-Evident Memory)

```sql
CREATE TABLE memory_chain (
    id TEXT PRIMARY KEY,
    prev_hash TEXT,
    content_hash TEXT NOT NULL,  -- SHA-256(content || prev_hash)
    signature TEXT NOT NULL,      -- Ed25519 sig(content_hash)
    created_at TEXT DEFAULT (datetime('now'))
);

-- Verification: recompute hashes and check chain continuity
-- Any break = tampering detected
```

---

## References

- [SQLite 3.53.0 Features](references/sqlite-353-features.md)
- [SQLite Patterns & Schema](references/sqlite-patterns.md)