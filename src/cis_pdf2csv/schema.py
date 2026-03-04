from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional

class ControlRecord(BaseModel):
    benchmark_name: str
    benchmark_version: str
    benchmark_date: str

    control_id: str
    profile: str
    title: str
    assessment: str
    applicability: Optional[str] = None

    description: Optional[str] = None
    rationale: Optional[str] = None
    impact: Optional[str] = None
    audit: Optional[str] = None
    remediation: Optional[str] = None
    default_value: Optional[str] = None
    references: Optional[str] = None

    page_start: int
    page_end: int

    source_pdf_sha256: str
    block_text_sha256: str
    extracted_at_utc: str
    parser_version: str = Field(default="0.1.0")
