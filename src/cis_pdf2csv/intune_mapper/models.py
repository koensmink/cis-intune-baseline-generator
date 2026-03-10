from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from .value_parser import ParsedRecommendation


class MappingInputControl(BaseModel):
    control_id: str
    title: str
    profile: str = "Unknown"
    assessment: str = "Unknown"

    recommendation: Optional[str] = None
    description: Optional[str] = None
    rationale: Optional[str] = None
    impact: Optional[str] = None
    audit: Optional[str] = None
    remediation: Optional[str] = None
    default_value: Optional[str] = None
    references: Optional[str] = None


class NormalizedControl(MappingInputControl):
    target: str = "windows_server_2025"
    parsed_recommendation: ParsedRecommendation
    quality_flags: List[str] = Field(default_factory=list)


class IntuneMapping(BaseModel):
    cis_id: str
    title: str
    implementation_type: str
    intune_area: str
    setting_name: str
    value: str
    confidence: float

    rule_id: str
    notes: Optional[str] = None
    parsed_value_type: Optional[str] = None
    quality_flags: List[str] = Field(default_factory=list)


class MappingConflict(BaseModel):
    cis_id: str
    title: str
    selected_rule_id: str
    selected_implementation_type: str
    matched_rule_ids: List[str]
    matched_implementation_types: List[str]


class SuggestedMapping(BaseModel):
    cis_id: str
    title: str
    suggested_implementation_type: str
    suggested_intune_area: str
    suggested_setting_name: str
    suggested_value: str
    confidence: float
    reasoning: str


class ResolverResult(BaseModel):
    mappings: List[IntuneMapping]
    conflicts: List[MappingConflict]
    suggestions: List[SuggestedMapping] = Field(default_factory=list)
