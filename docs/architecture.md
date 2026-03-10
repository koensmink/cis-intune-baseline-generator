# CIS → Intune Baseline Generator Architecture

## Objective

Convert CIS benchmark controls into Microsoft Intune configuration
policies.

The generator processes CIS benchmark documents and produces structured
outputs that can be used to create Intune baseline policies.

Primary outputs: - Intune baseline mapping - Implementation-ready
configuration artifacts - Manual review list for unmapped controls

------------------------------------------------------------------------

## High-level pipeline

CIS PDF → CIS parser → Normalized control dataset → Mapping engine →
Policy classification → Export layer → Intune-ready artifacts

Pipeline:

CIS PDF\
↓\
parser\
↓\
normalized_controls.csv\
↓\
resolver / mapping engine\
↓\
policy classification\
↓\
exports

------------------------------------------------------------------------

## Core components

### 1. CIS Parser

Responsible for extracting benchmark controls from CIS documents.

Output fields:

  field                 description
  --------------------- -------------------------------
  cis_id                CIS control identifier
  title                 control title
  level                 L1 / L2
  profile               benchmark profile
  gpo_path              Windows GPO reference
  registry_path         registry key
  registry_value_name   registry value
  recommended_value     CIS recommended configuration
  description           CIS description
  rationale             CIS rationale

Output format:

normalized_controls.csv

------------------------------------------------------------------------

### 2. Mapping Engine

Translates CIS controls to Intune implementation models.

Possible implementation types:

  type                      description
  ------------------------- -------------------------------
  settings_catalog          Windows Settings Catalog
  endpoint_security         Defender, Firewall, BitLocker
  administrative_template   ADMX-backed policy
  custom_oma_uri            CSP configuration
  manual_review             requires human validation

------------------------------------------------------------------------

### 3. Rule Engine

Rules inspect CIS controls using: - title patterns - GPO path - registry
path - known mappings

Rules output an `IntuneMapping` object.

Conflict resolution: 1. prefer endpoint_security 2. prefer
settings_catalog 3. fallback to OMA-URI 4. manual_review

------------------------------------------------------------------------

### 4. Policy Classification

Mapped controls grouped into baseline profiles:

-   Windows OS Hardening
-   Defender Security
-   Firewall
-   BitLocker
-   Credential Protection
-   Logging & Auditing
-   Browser Hardening

Reference:
https://learn.microsoft.com/en-us/mem/intune/protect/endpoint-security

------------------------------------------------------------------------

### 5. Export Layer

Supported exports:

  output                 purpose
  ---------------------- -----------------------
  baseline.csv           full mapping overview
  intune_policies.json   policy definitions
  manual_review.csv      unresolved controls
  conflicts.csv          multiple rule matches
