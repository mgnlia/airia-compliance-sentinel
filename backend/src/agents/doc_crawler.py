"""Document Crawler Agent — detects outdated compliance language in docs."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Optional

from src.models.compliance import (
    ComplianceFinding,
    ComplianceFramework,
    Severity,
    SignalSource,
)

logger = logging.getLogger(__name__)

# Outdated / risky compliance language patterns
OUTDATED_PATTERNS = {
    "safe_harbor": {
        "pattern": "safe harbor",
        "replacement": "EU-US Data Privacy Framework",
        "frameworks": [ComplianceFramework.GDPR],
        "severity": Severity.HIGH,
        "reason": "Safe Harbor was invalidated by Schrems I (2015). Use Data Privacy Framework.",
    },
    "privacy_shield": {
        "pattern": "privacy shield",
        "replacement": "EU-US Data Privacy Framework",
        "frameworks": [ComplianceFramework.GDPR],
        "severity": Severity.HIGH,
        "reason": "Privacy Shield was invalidated by Schrems II (2020). Use Data Privacy Framework.",
    },
    "implied_consent": {
        "pattern": "implied consent",
        "replacement": "explicit consent",
        "frameworks": [ComplianceFramework.GDPR],
        "severity": Severity.MEDIUM,
        "reason": "GDPR requires explicit, informed consent. Implied consent is insufficient.",
    },
    "reasonable_security": {
        "pattern": "reasonable security measures",
        "replacement": "specific security controls (encryption, access controls, audit logging)",
        "frameworks": [ComplianceFramework.SOC2, ComplianceFramework.HIPAA],
        "severity": Severity.MEDIUM,
        "reason": "Vague security language doesn't meet SOC2/HIPAA specificity requirements.",
    },
    "hipaa_old_breach": {
        "pattern": "notify within 60 days",
        "replacement": "notify without unreasonable delay, no later than 60 days",
        "frameworks": [ComplianceFramework.HIPAA],
        "severity": Severity.LOW,
        "reason": "HIPAA breach notification must emphasize 'without unreasonable delay'.",
    },
}

# Staleness thresholds — docs not updated in this long are flagged
STALENESS_THRESHOLDS = {
    "privacy_policy": timedelta(days=365),
    "security_policy": timedelta(days=180),
    "compliance_report": timedelta(days=90),
    "incident_response_plan": timedelta(days=365),
}


class DocCrawlerAgent:
    """Crawls documents to detect outdated compliance language and stale policies."""

    def __init__(self):
        pass

    async def analyze_document(
        self,
        doc_id: str,
        title: str,
        content: str,
        doc_url: Optional[str] = None,
        last_modified: Optional[datetime] = None,
    ) -> list[ComplianceFinding]:
        """Analyze a single document for compliance issues."""
        findings: list[ComplianceFinding] = []

        # Check for outdated language patterns
        content_lower = content.lower()
        for pattern_name, config in OUTDATED_PATTERNS.items():
            if config["pattern"].lower() in content_lower:
                finding = ComplianceFinding(
                    id=f"doc-{doc_id}-{pattern_name}",
                    source=SignalSource.DOCUMENT,
                    source_url=doc_url,
                    title=f"Outdated compliance language: '{config['pattern']}'",
                    description=(
                        f"Document '{title}' contains outdated language: '{config['pattern']}'. "
                        f"{config['reason']} "
                        f"Suggested replacement: '{config['replacement']}'."
                    ),
                    severity=config["severity"],
                    frameworks=config["frameworks"],
                    confidence=0.85,
                    raw_content=self._extract_context(content, config["pattern"]),
                    metadata={
                        "doc_id": doc_id,
                        "doc_title": title,
                        "pattern": pattern_name,
                        "suggested_replacement": config["replacement"],
                    },
                )
                findings.append(finding)

        # Check staleness
        if last_modified:
            staleness_findings = self._check_staleness(doc_id, title, doc_url, last_modified)
            findings.extend(staleness_findings)

        logger.info(f"Document '{title}': {len(findings)} compliance findings")
        return findings

    def _check_staleness(
        self,
        doc_id: str,
        title: str,
        doc_url: Optional[str],
        last_modified: datetime,
    ) -> list[ComplianceFinding]:
        """Check if a document is stale based on its type."""
        findings: list[ComplianceFinding] = []
        title_lower = title.lower()
        now = datetime.utcnow()

        for doc_type, threshold in STALENESS_THRESHOLDS.items():
            doc_type_readable = doc_type.replace("_", " ")
            if doc_type_readable in title_lower or doc_type.replace("_", "-") in title_lower:
                age = now - last_modified
                if age > threshold:
                    findings.append(
                        ComplianceFinding(
                            id=f"doc-{doc_id}-stale-{doc_type}",
                            source=SignalSource.DOCUMENT,
                            source_url=doc_url,
                            title=f"Stale document: '{title}' not updated in {age.days} days",
                            description=(
                                f"Document '{title}' was last modified {age.days} days ago. "
                                f"{doc_type_readable.title()} documents should be reviewed at least "
                                f"every {threshold.days} days."
                            ),
                            severity=Severity.MEDIUM if age < threshold * 2 else Severity.HIGH,
                            frameworks=[ComplianceFramework.SOC2, ComplianceFramework.GDPR],
                            confidence=0.95,
                            metadata={
                                "doc_id": doc_id,
                                "last_modified": last_modified.isoformat(),
                                "days_since_update": age.days,
                                "threshold_days": threshold.days,
                            },
                        )
                    )

        return findings

    def _extract_context(self, content: str, pattern: str, context_chars: int = 200) -> str:
        """Extract surrounding context for a pattern match."""
        idx = content.lower().find(pattern.lower())
        if idx == -1:
            return ""
        start = max(0, idx - context_chars)
        end = min(len(content), idx + len(pattern) + context_chars)
        return f"...{content[start:end]}..."
