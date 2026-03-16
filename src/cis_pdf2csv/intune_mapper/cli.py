from __future__ import annotations

import argparse
import inspect
import json
import os
from pathlib import Path
from typing import List

from rich.console import Console
from rich.table import Table

from .exporters import (
    write_baseline_csv,
    write_conflicts_csv,
    write_intune_policies_json,
    write_manual_review_csv,
    write_suggested_mappings_jsonl,
)
from .llm_fallback import OpenAILLMClient
from .models import MappingInputControl
from .resolver import resolve_controls

console = Console()


def _load_controls_jsonl(path: Path) -> List[MappingInputControl]:
    controls: List[MappingInputControl] = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            controls.append(MappingInputControl(**json.loads(line)))

    return controls


def _build_llm_client(enabled: bool):
    """
    Build a real OpenAI-backed LLM client if requested and possible.
    Falls back to None if disabled or OPENAI_API_KEY is missing.
    """
    if not enabled:
        return None

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print(
            "[yellow]LLM fallback requested, but OPENAI_API_KEY is not set. "
            "Heuristic fallback will be used instead.[/yellow]"
        )
        return None

    try:
        return OpenAILLMClient(api_key=api_key)
    except Exception as e:
        console.print(
            f"[yellow]Failed to initialize OpenAI LLM client: {e}. "
            "Heuristic fallback will be used instead.[/yellow]"
        )
        return None


def _resolve_with_optional_llm_fallback(
    controls: List[MappingInputControl],
    llm_fallback: bool,
):
    """
    Call resolve_controls() and pass llm_client if the resolver supports it.
    Falls back gracefully if the resolver uses an older signature.
    """
    llm_client = _build_llm_client(llm_fallback)
    sig = inspect.signature(resolve_controls)

    if "llm_client" in sig.parameters:
        return resolve_controls(controls, llm_client=llm_client)

    # Backward-compatible fallback for older resolver variants
    if "llm_fallback" in sig.parameters:
        return resolve_controls(controls, llm_fallback=llm_fallback)

    return resolve_controls(controls)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cis-intune-map",
        description="Map parsed CIS controls to Intune baseline artifacts",
    )
    parser.add_argument(
        "input",
        help="Input controls JSONL exported by cis-pdf2csv",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        required=True,
        help="Output directory",
    )
    parser.add_argument(
        "--llm-fallback",
        action="store_true",
        help="Use LLM fallback for controls that cannot be mapped deterministically",
    )

    args = parser.parse_args(argv)

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    controls = _load_controls_jsonl(input_path)
    result = _resolve_with_optional_llm_fallback(
        controls=controls,
        llm_fallback=args.llm_fallback,
    )

    mappings = result.mappings
    conflicts = result.conflicts
    suggestions = result.suggestions

    write_baseline_csv(mappings, output_dir / "baseline.csv")
    write_intune_policies_json(mappings, output_dir / "intune_policies.json")
    write_manual_review_csv(mappings, output_dir / "manual_review.csv")
    write_suggested_mappings_jsonl(suggestions, output_dir / "suggested_mappings.jsonl")
    write_conflicts_csv(conflicts, output_dir / "conflicts.csv")

    manual_count = len([m for m in mappings if m.implementation_type == "manual_review"])

    table = Table(title="cis-intune-map summary")
    table.add_column("Controls", justify="right")
    table.add_column("Mapped", justify="right")
    table.add_column("Manual review", justify="right")
    table.add_column("Conflicts", justify="right")
    table.add_column("Suggestions", justify="right")
    table.add_row(
        str(len(controls)),
        str(len(mappings) - manual_count),
        str(manual_count),
        str(len(conflicts)),
        str(len(suggestions)),
    )
    console.print(table)

    if args.llm_fallback:
        if os.getenv("OPENAI_API_KEY"):
            console.print("[green]LLM fallback requested and OPENAI_API_KEY detected[/green]")
        else:
            console.print("[yellow]LLM fallback requested, but no OPENAI_API_KEY detected[/yellow]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
def _resolve_with_optional_llm_fallback(
    controls: List[MappingInputControl],
    llm_fallback: bool,
):
    """
    Call resolve_controls() and only pass llm_fallback if the resolver
    actually supports that parameter. This keeps the CLI backward-compatible.
    """
    sig = inspect.signature(resolve_controls)

    if "llm_fallback" in sig.parameters:
        return resolve_controls(controls, llm_fallback=llm_fallback)

    return resolve_controls(controls)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cis-intune-map",
        description="Map parsed CIS controls to Intune baseline artifacts",
    )
    parser.add_argument(
        "input",
        help="Input controls JSONL exported by cis-pdf2csv",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        required=True,
        help="Output directory",
    )
    parser.add_argument(
        "--llm-fallback",
        action="store_true",
        help="Use LLM fallback for controls that cannot be mapped deterministically",
    )

    args = parser.parse_args(argv)

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    controls = _load_controls_jsonl(input_path)
    result = _resolve_with_optional_llm_fallback(
        controls=controls,
        llm_fallback=args.llm_fallback,
    )

    mappings = result.mappings
    conflicts = result.conflicts
    suggestions = result.suggestions

    write_baseline_csv(mappings, output_dir / "baseline.csv")
    write_intune_policies_json(mappings, output_dir / "intune_policies.json")
    write_manual_review_csv(mappings, output_dir / "manual_review.csv")
    write_suggested_mappings_jsonl(suggestions, output_dir / "suggested_mappings.jsonl")
    write_conflicts_csv(conflicts, output_dir / "conflicts.csv")

    manual_count = len([m for m in mappings if m.implementation_type == "manual_review"])

    table = Table(title="cis-intune-map summary")
    table.add_column("Controls", justify="right")
    table.add_column("Mapped", justify="right")
    table.add_column("Manual review", justify="right")
    table.add_column("Conflicts", justify="right")
    table.add_column("Suggestions", justify="right")
    table.add_row(
        str(len(controls)),
        str(len(mappings) - manual_count),
        str(manual_count),
        str(len(conflicts)),
        str(len(suggestions)),
    )
    console.print(table)

    if args.llm_fallback:
        console.print("[cyan]LLM fallback requested[/cyan]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
