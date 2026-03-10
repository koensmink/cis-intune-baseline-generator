
# cis-pdf2csv
### CIS Benchmark Parser & Intune Baseline Generator

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)
![Platform](https://img.shields.io/badge/platform-Windows%20Server%202025-lightgrey)

Convert **CIS Benchmark PDFs** into structured data and generate **Microsoft Intune baseline configurations**.

The project provides a hybrid architecture combining:

- deterministic security mapping logic
- structured CIS parsing
- rule‑based Intune policy generation
- optional LLM‑assisted mapping suggestions

This enables automated transformation of **CIS hardening benchmarks → Intune baseline artifacts**.

---

# Key Features

### CIS Benchmark Parsing
Extract structured controls from CIS benchmark PDFs.

Fields extracted:

- control_id
- title
- description
- audit instructions
- remediation steps
- default values
- benchmark metadata
- page references

Output format:

```
JSONL (one control per line)
```

---

### Deterministic Intune Baseline Generation

A rule‑based mapping engine converts CIS controls into **Intune configuration recommendations**.

The mapping engine contains:

- value normalization
- CIS recommendation parsing
- rule packs per control family
- deterministic policy resolution

---

### LLM Assisted Mapping

Controls that cannot be mapped deterministically are optionally sent to an **LLM fallback engine**.

The model proposes structured mappings which can later be reviewed and promoted to permanent rules.

LLM output example:

```json
{
  "implementation_type": "settings_catalog",
  "intune_area": "Local Policies/Security Options",
  "setting_name": "Interactive logon: Do not display last signed-in",
  "value_kind": "boolean",
  "value": true,
  "confidence": 0.83
}
```

The LLM assists rule development but **never replaces deterministic mappings**.

---

# Architecture

```
CIS Benchmark PDF
        │
        ▼
   CIS Parser
        │
        ▼
  JSONL Controls
        │
        ▼
     Normalizer
        │
        ▼
   Value Parser
        │
        ▼
   Rule Engine
        │
        ├── mapped controls
        │
        └── manual review
                │
                ▼
         LLM Suggestion Engine
                │
                ▼
      suggested_mappings.jsonl
```

---

# Repository Structure

```
src/
 └─ cis_pdf2csv/
      ├─ parser.py
      ├─ cli.py
      └─ intune_mapper/
           ├─ cli.py
           ├─ resolver.py
           ├─ normalizer.py
           ├─ value_parser.py
           ├─ exporters.py
           ├─ llm_fallback.py
           └─ rules/
                └─ windows_server/
                     ├─ account_policies.py
                     ├─ audit_policy.py
                     ├─ security_options.py
                     ├─ defender.py
                     ├─ firewall.py
                     ├─ credential_protection.py
                     ├─ event_log.py
                     └─ remote_access.py
```

---

# Supported CIS Benchmarks

Currently implemented:

- Windows Server 2025

Architecture prepared for:

- Windows Server 2016
- Windows Server 2019
- Windows Server 2022
- Windows 10 / 11
- Apple macOS

---

# Installation

Clone repository

```
git clone https://github.com/koensmink/cis-pdf2csv.git
cd cis-pdf2csv
```

Install dependencies

```
pip install -e .
```

---

# Usage

## Parse CIS Benchmark

```
python -m cis_pdf2csv.cli benchmark.pdf -o controls.jsonl
```

Output:

```
controls.jsonl
```

---

## Generate Intune Baseline

```
python -m cis_pdf2csv.intune_mapper.cli controls.jsonl -o intune_out
```

Output directory:

```
intune_out/
```

Generated artifacts:

| File | Description |
|-----|-------------|
| baseline.csv | proposed Intune baseline |
| manual_review.csv | controls needing review |
| intune_policies.json | structured policy data |
| suggested_mappings.jsonl | LLM mapping suggestions |

---

## Enable LLM Suggestions

```
python -m cis_pdf2csv.intune_mapper.cli controls.jsonl -o intune_out --llm-fallback
```

Environment variable required:

```
OPENAI_API_KEY=your_api_key
```

---

# Example Workflow

```
1. Download CIS Benchmark PDF
2. Parse PDF → JSONL dataset
3. Run Intune mapper
4. Review manual_review.csv
5. Review suggested_mappings.jsonl
6. Promote accepted suggestions to rule packs
```

---

# Design Principles

### Deterministic First

Baseline generation must be reproducible.

Rule packs remain the primary mapping method.

### AI Assisted Engineering

LLM suggestions accelerate rule creation but do not replace deterministic logic.

### Reviewable Output

All mappings are exported as structured artifacts that can be reviewed and audited.

---

# Development Roadmap

Planned improvements:

- Windows Server shared rule packs (2016‑2025)
- macOS CIS mapping
- Windows 11 workstation baseline
- Intune Settings Catalog metadata integration
- Microsoft Graph API policy deployment
- Policy template generation
- Coverage metrics per benchmark

---

# Contributing

Contributions are welcome.

Recommended workflow:

1. Identify unmapped controls in `manual_review.csv`
2. Review `suggested_mappings.jsonl`
3. Promote mappings to rule packs
4. Add tests
5. Submit PR

---

# License

MIT License

---

# Author

Koen Smink  
Security Engineering / Automation
