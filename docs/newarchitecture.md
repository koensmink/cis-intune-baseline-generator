Implement the next phase of the CIS → Intune mapper using a hybrid design.

Goal:
Keep the current deterministic codebase, add a value parser and modular Windows Server 2025 rule packs, and add an LLM-assisted fallback only for manual_review controls.

Tasks:
1. Add value_parser.py to normalize CIS recommendations into structured values.
2. Add normalizer.py between parser output and resolver.
3. Split the current rules.py into modular rule packs under:
   src/cis_pdf2csv/intune_mapper/rules/windows_server/
4. Implement first rule packs for:
   - account policies
   - audit policy
   - security options
   - defender
   - firewall
   - credential protection
   - event log
   - remote access
5. Expand models.py and resolver.py to use parsed recommendations and quality flags.
6. Add llm_fallback.py that only runs for manual_review controls and returns structured mapping suggestions.
7. Expand CLI and exporters to emit:
   - baseline.csv
   - manual_review.csv
   - intune_policies.json
   - suggested_mappings.jsonl
8. Add tests for value parsing, rule packs, and mocked LLM fallback.

Constraints:
- do not replace the deterministic mapper with LLM logic
- LLM fallback must only assist manual_review items
- keep Windows Server 2025 as the first supported target
- structure the code so Windows Server 2016/2019/2022 can be added later with shared rule packs and overrides

Before coding:
- list files to create/change
- show the migration plan from current rules.py
- explain the staged implementation order
