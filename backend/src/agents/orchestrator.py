"""Orchestrator Agent — aggregates signals from all agents, scores risk, triggers HITL review."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Optional

from src.models.compliance import (
    AgentStatus,
    ComplianceFinding,
    ComplianceFramework,
    HITLReview,
    RiskScore,
    Severity,
)

logger = logging.getLogger(__name__)

# Severity weights for risk scoring
SEVERITY_WEIGHTS = {
    Severity.LOW: 1.0,
    Severity.MEDIUM: 3.0,
    Severity.HIGH: 7.0,
    Severity.CRITICAL: 15.0,
}

# Thresholds for HITL triggers
HITL_THRESHOLD_SCORE = 50.0  # Overall risk score that triggers HITL
HITL_THRESHOLD_CRITICAL = 1  # Number of critical findings that triggers HITL


class OrchestratorAgent:
    """Central orchestrator that aggregates findings and manages risk."""

    def __init__(self):
        self.findings: list[ComplianceFinding] = []
        self.reviews: list[HITLReview] = []
        self.agent_statuses: dict[str, AgentStatus] = {}
        self._current_risk: Optional[RiskScore] = None

    def ingest_findings(self, new_findings: list[ComplianceFinding]) -> RiskScore:
        """Ingest new findings from any agent and recalculate risk."""
        # Deduplicate by ID
        existing_ids = {f.id for f in self.findings}
        unique_new = [f for f in new_findings if f.id not in existing_ids]

        self.findings.extend(unique_new)
        logger.info(f"Ingested {len(unique_new)} new findings ({len(new_findings) - len(unique_new)} duplicates skipped)")

        # Recalculate risk
        self._current_risk = self._calculate_risk()

        # Check HITL triggers
        if self._should_trigger_hitl(unique_new):
            for finding in unique_new:
                if finding.severity in (Severity.CRITICAL, Severity.HIGH):
                    self._create_hitl_review(finding)

        return self._current_risk

    def _calculate_risk(self) -> RiskScore:
        """Calculate overall and per-framework risk scores."""
        if not self.findings:
            return RiskScore(overall_score=0.0)

        # Overall score: weighted sum of findings, capped at 100
        total_weight = sum(
            SEVERITY_WEIGHTS[f.severity] * f.confidence for f in self.findings
        )
        # Normalize: 100 = 20+ weighted findings
        overall = min(100.0, (total_weight / 20.0) * 100.0)

        # Per-framework scores
        framework_scores: dict[ComplianceFramework, float] = {}
        for framework in ComplianceFramework:
            framework_findings = [f for f in self.findings if framework in f.frameworks]
            if framework_findings:
                fw_weight = sum(
                    SEVERITY_WEIGHTS[f.severity] * f.confidence for f in framework_findings
                )
                framework_scores[framework] = min(100.0, (fw_weight / 10.0) * 100.0)

        critical_count = sum(1 for f in self.findings if f.severity == Severity.CRITICAL)
        high_count = sum(1 for f in self.findings if f.severity == Severity.HIGH)

        return RiskScore(
            overall_score=round(overall, 1),
            framework_scores=framework_scores,
            findings_count=len(self.findings),
            critical_count=critical_count,
            high_count=high_count,
        )

    def _should_trigger_hitl(self, new_findings: list[ComplianceFinding]) -> bool:
        """Determine if new findings should trigger HITL review."""
        if not self._current_risk:
            return False

        # Trigger on high overall risk
        if self._current_risk.overall_score >= HITL_THRESHOLD_SCORE:
            return True

        # Trigger on critical findings
        new_critical = sum(1 for f in new_findings if f.severity == Severity.CRITICAL)
        if new_critical >= HITL_THRESHOLD_CRITICAL:
            return True

        return False

    def _create_hitl_review(self, finding: ComplianceFinding) -> HITLReview:
        """Create a HITL review request for a finding."""
        review = HITLReview(
            id=str(uuid.uuid4()),
            finding_id=finding.id,
            status="pending",
        )
        self.reviews.append(review)
        logger.info(f"HITL review created for finding {finding.id}: {finding.title}")
        return review

    def resolve_review(self, review_id: str, status: str, reviewer: str, notes: Optional[str] = None) -> Optional[HITLReview]:
        """Resolve a HITL review."""
        for review in self.reviews:
            if review.id == review_id:
                review.status = status
                review.reviewer = reviewer
                review.notes = notes
                review.resolved_at = datetime.utcnow()
                logger.info(f"Review {review_id} resolved: {status} by {reviewer}")
                return review
        return None

    def get_risk_score(self) -> RiskScore:
        """Get current risk score."""
        if not self._current_risk:
            self._current_risk = self._calculate_risk()
        return self._current_risk

    def get_pending_reviews(self) -> list[HITLReview]:
        """Get all pending HITL reviews."""
        return [r for r in self.reviews if r.status == "pending"]

    def get_findings_by_severity(self, severity: Severity) -> list[ComplianceFinding]:
        """Get findings filtered by severity."""
        return [f for f in self.findings if f.severity == severity]

    def get_findings_by_framework(self, framework: ComplianceFramework) -> list[ComplianceFinding]:
        """Get findings filtered by framework."""
        return [f for f in self.findings if framework in f.frameworks]

    def update_agent_status(self, agent_name: str, is_active: bool, findings_today: int = 0):
        """Update the status of a monitoring agent."""
        self.agent_statuses[agent_name] = AgentStatus(
            agent_name=agent_name,
            is_active=is_active,
            last_heartbeat=datetime.utcnow(),
            findings_today=findings_today,
        )

    def get_dashboard_summary(self) -> dict:
        """Get a summary suitable for the dashboard."""
        risk = self.get_risk_score()
        return {
            "risk_score": risk.model_dump(),
            "pending_reviews": len(self.get_pending_reviews()),
            "total_findings": len(self.findings),
            "critical_findings": risk.critical_count,
            "high_findings": risk.high_count,
            "agent_statuses": {
                name: status.model_dump() for name, status in self.agent_statuses.items()
            },
            "recent_findings": [
                f.model_dump() for f in sorted(
                    self.findings, key=lambda x: x.detected_at, reverse=True
                )[:10]
            ],
        }
