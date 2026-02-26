"""Pydantic models for compliance findings, risk scores, and agent signals."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceFramework(str, Enum):
    GDPR = "gdpr"
    SOC2 = "soc2"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"


class SignalSource(str, Enum):
    GITHUB_PR = "github_pr"
    SLACK_MESSAGE = "slack_message"
    DOCUMENT = "document"


class ComplianceFinding(BaseModel):
    """A single compliance finding from any agent."""

    id: str = Field(description="Unique finding ID")
    source: SignalSource
    source_url: Optional[str] = None
    title: str
    description: str
    severity: Severity
    frameworks: list[ComplianceFramework] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, description="Agent confidence 0-1")
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    raw_content: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class RiskScore(BaseModel):
    """Aggregated risk score from the orchestrator."""

    overall_score: float = Field(ge=0.0, le=100.0)
    framework_scores: dict[ComplianceFramework, float] = Field(default_factory=dict)
    findings_count: int = 0
    critical_count: int = 0
    high_count: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class HITLReview(BaseModel):
    """Human-in-the-loop review request."""

    id: str
    finding_id: str
    status: str = "pending"  # pending | approved | dismissed | escalated
    reviewer: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


class AgentStatus(BaseModel):
    """Status of an individual monitoring agent."""

    agent_name: str
    is_active: bool = True
    last_heartbeat: Optional[datetime] = None
    findings_today: int = 0
    error_count: int = 0
