---
id: swal-finetune
name: swal-finetune
category: ai
tags:
  - swal-finetune
goals:
  - 'Fine-tune an LLM to be the SWAL CEO assistant ("BelaMini") — expert in SWAL''s software products, projects, clients, and internal operations. Exposes NO sensitive data (API keys, passwords, internal strategy).'
authors:
  - Brahyan Belalcazar
---

# SWAL Fine-Tune Skill - CEO Assistant Model

## Overview
Fine-tune an LLM to be the SWAL CEO assistant ("BelaMini") — expert in SWAL's software products, projects, clients, and internal operations. Exposes NO sensitive data (API keys, passwords, internal strategy).

## Target Model
**Gemma 4 E2B** (google/gemma-4-E2B) — 10.3GB, optimized for local/phone deployment
- Alternatives: Qwen3-4B, Llama-3.2-3B for faster training

---

## PHASE 1: Data Collection (from Cortex)

### 1.1 Gather SWAL Context
Run scripts to extract from Cortex:
```bash
# Pull all memories about SWAL, projects, clients
Search-Cortex -Query "SWAL projects products ManteniApp Cortex Gestalt" -Limit 50

# Pull client info
Search-Cortex -Query "Leonardo Duque Rodacenter client requirements" -Limit 20

# Pull technical decisions
Search-Cortex -Query "architecture decisions pricing sales" -Limit 30
```

### 1.2 Generate Training Data
Use `scripts/export_training_data.py` to create `swal_training.jsonl`:
- Q&A pairs about SWAL products
- Client interaction patterns
- Project management knowledge
- Software development guidance

### 1.3 Data Curation — REMOVE SENSITIVE INFO ⚠️

**MUST REMOVE:**
- API keys, tokens, passwords
- Internal strategy discussions
- Personal conversations (only professional context)
- Financial details not public
- Employee personal info

**KEEP:**
- Product features, pricing, capabilities
- Public client information (Rodacenter, tripro.cl)
- Project architectures and decisions
- General company knowledge

---

## PHASE 2: Fine-Tuning (Colab + Unsloth)

### 2.1 Setup Colab
1. Open: `skills/swal-finetune/notebooks/swal-ceo-assistant-colab.ipynb`
2. Add Secrets in Colab:
   - `HF_TOKEN` - HuggingFace write token
   - `WANDB_API_KEY` - Weights & Biases (optional)

### 2.2 Upload Training Data
```python
from google.colab import files
uploaded = files.upload()
# Upload: swal_training.jsonl
```

Or mount Google Drive once:
```python
from google.colab import drive
drive.mount('/content/drive')
# Then copy: !cp /content/drive/MyDrive/swal_training.jsonl .
```

### 2.3 Run Training
```python
# Model: Gemma 4 E2B (or smaller if VRAM limited)
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "google/gemma-4-E2B",
    max_seq_length = 2048,
    load_in_4bit = True,
)

# Add LoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    r = 32,
    target_modules = ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 16,
)

# Train
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    max_seq_length = 2048,
    dataset_text_field = "text",
)
trainer.train()
```

### 2.4 Save & Export
```python
# Save to Drive
model.save_pretrained("/content/drive/MyDrive/swal-ceo-assistant")
tokenizer.save_pretrained("/content/drive/MyDrive/swal-ceo-assistant")

# Or merge and upload to HuggingFace
model.push_to_hub("iberi22/swal-ceo-assistant", token = HF_TOKEN)
tokenizer.push_to_hub("iberi22/swal-ceo-assistant", token = HF_TOKEN)
```

---

## PHASE 3: Upload to HuggingFace

### 3.1 Create HuggingFace Repo
```bash
# Via web interface
# 1. Go to https://huggingface.co/new
# 2. Name: iberi22/swal-ceo-assistant
# 3. Set Private or Public
```

### 3.2 Upload via CLI
```bash
pip install huggingface_hub
huggingface-cli login
# Paste HF_TOKEN

# Upload model files
huggingface-cli upload iberi22/swal-ceo-assistant ./swal-ceo-assistant/
```

### 3.3 Generate GGUF for Ollama
```python
# Use llama.cpp to convert to GGUF
!git clone https://github.com/ggerganov/llama.cpp.git
!python llama.cpp/convert-hf-to-gguf.py ./swal-ceo-assistant --outfile ./swal-ceo-assistant-q4.gguf
```

---

## PHASE 4: Continuous Updates

### 4.1 Weekly Data Refresh
```bash
# Pull new context from Cortex
python scripts/export_training_data.py --output swal_training_v2.jsonl

# Merge with existing data
python scripts/merge_training_data.py swal_training.jsonl swal_training_v2.jsonl
```

### 4.2 Incremental Fine-Tuning
```python
# Load previous model as base
model = FastLanguageModel.from_pretrained(
    model_name = "iberi22/swal-ceo-assistant",
    load_in_4bit = True,
)

# Fine-tune with new data
trainer.train()  # Use new_dataset with additional examples

# Push updated version
model.push_to_hub("iberi22/swal-ceo-assistant-v2", token = HF_TOKEN)
```

### 4.3 Quality Check
Before uploading:
- Test model responses
- Verify no sensitive info exposed
- Check response quality on SWAL topics

---

## Quick Start Commands

```bash
# 1. Collect data
python E:\scripts-python\xavier2\scripts\export_training_data.py

# 2. Check training data
head -5 E:\datasetsDrive\training\swal_training.jsonl

# 3. Open Colab notebook
start https://colab.research.google.com/github/iberi22/xavier2/blob/master/notebooks/swal-ceo-assistant-colab.ipynb

# 4. After training, merge LoRA adapters
python merge_lora.py iberi22/swal-ceo-assistant --output ./swal-ceo-assistant-merged

# 5. Upload to HuggingFace
huggingface-cli upload iberi22/swal-ceo-assistant ./swal-ceo-assistant-merged/
```

---

## Training Data Format (JSONL)

```json
{"instruction": "What is ManteniApp and what pricing plans does SWAL offer?", "input": "", "output": "ManteniApp is SWAL's AI-powered machinery monitoring platform...", "category": "product"}
{"instruction": "Who is Leonardo Duque and what is his role with SWAL?", "input": "", "output": "Leonardo Duque is a SWAL partner/vendor who works with Rodacenter in Chile...", "category": "client"}
{"instruction": "Describe the architecture of the Gestalt-Rust project", "input": "", "output": "Gestalt-Rust is a Rust-based system with...", "category": "technical"}
```

---

## Environment & Resources

| Resource | Value |
|----------|-------|
| Colab GPU | A100 (40GB VRAM) recommended |
| Training Time | ~1-2 hours for Gemma 4 E2B |
| Storage | ~15GB for model + checkpoints |
| RAM | 12GB+ recommended |

---

## Files in this Skill

```
skills/swal-finetune/
├── SKILL.md                           # This file
├── reference_notebooks/
│   ├── Jackrong-Qwopus3-5-27b-Colab.ipynb   # Reference guide
│   └── Qwopus3-5-27b-Colab_complete_guide.pdf
├── notebooks/
│   └── swal-ceo-assistant-colab.ipynb        # Main training notebook
└── scripts/
    ├── export_training_data.py         # Extract from Cortex
    ├── merge_training_data.py          # Merge training sets
    └── test_model.py                  # Quality check script
```