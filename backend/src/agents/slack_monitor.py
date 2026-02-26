"""Slack Monitor Agent — flags policy-relevant conversations."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from src.models.compliance import (
    ComplianceFinding,
    ComplianceFramework,
    Severity,
    SignalSource,
)

logger = logging.getLogger(__name__)

# Policy-relevant conversation patterns
POLICY_PATTERNS = {
    "data_sharing": {
        "keywords": ["share data with", "send to third party", "export user data", "data transfer"],
        "frameworks": [ComplianceFramework.GDPR, ComplianceFramework.SOC2],
        "severity": Severity.HIGH,
    },
    "access_bypass": {
        "keywords": ["skip auth", "bypass security", "shared password", "use my credentials"],
        "frameworks": [ComplianceFramework.SOC2],
        "severity": Severity.CRITICAL,
    },
    "patient_info": {
        "keywords": ["patient name", "diagnosis", "medical record", "health info"],
        "frameworks": [ComplianceFramework.HIPAA],
        "severity": Severity.CRITICAL,
    },
    "payment_data": {
        "keywords": ["credit card", "card number", "payment details", "billing info"],
        "frameworks": [ComplianceFramework.PCI_DSS],
        "severity": Severity.CRITICAL,
    },
    "retention_policy": {
        "keywords": ["delete old data", "keep forever", "retention period", "data cleanup"],
        "frameworks": [ComplianceFramework.GDPR],
        "severity": Severity.MEDIUM,
    },
    "consent_discussion": {
        "keywords": ["user consent", "opt-in", "opt-out", "privacy notice", "cookie banner"],
        "frameworks": [ComplianceFramework.GDPR],
        "severity": Severity.MEDIUM,
    },
}


class SlackMonitorAgent:
    """Monitors Slack messages for compliance-relevant conversations."""

    def __init__(self, slack_token: Optional[str] = None):
        self.slack_token = slack_token

    async def analyze_message(
        self, channel: str, user: str, text: str, timestamp: str
    ) -> list[ComplianceFinding]:
        """Analyze a single Slack message for compliance signals."""
        findings: list[ComplianceFinding] = []
        text_lower = text.lower()

        for pattern_name, config in POLICY_PATTERNS.items():
            for keyword in config["keywords"]:
                if keyword.lower() in text_lower:
                    finding = ComplianceFinding(
                        id=f"slack-{channel}-{timestamp}-{pattern_name}",
                        source=SignalSource.SLACK_MESSAGE,
                        source_url=None,
                        title=f"Policy-relevant conversation: {pattern_name.replace('_', ' ').title()}",
                        description=(
                            f"Keyword '{keyword}' detected in #{channel} by {user}. "
                            f"This may relate to {', '.join(f.value.upper() for f in config['frameworks'])} compliance."
                        ),
                        severity=config["severity"],
                        frameworks=config["frameworks"],
                        confidence=0.6,
                        raw_content=text[:500],
                        metadata={
                            "channel": channel,
                            "user": user,
                            "pattern": pattern_name,
                            "keyword": keyword,
                        },
                    )
                    findings.append(finding)
                    break  # One finding per pattern per message

        logger.info(f"Slack message in #{channel}: {len(findings)} compliance findings")
        return findings

    async def analyze_batch(
        self, messages: list[dict]
    ) -> list[ComplianceFinding]:
        """Analyze a batch of Slack messages."""
        all_findings: list[ComplianceFinding] = []
        for msg in messages:
            findings = await self.analyze_message(
                channel=msg.get("channel", "unknown"),
                user=msg.get("user", "unknown"),
                text=msg.get("text", ""),
                timestamp=msg.get("ts", str(datetime.utcnow().timestamp())),
            )
            all_findings.extend(findings)
        return all_findings
