"""PR Monitor Agent — scans GitHub PRs for compliance-relevant changes."""

from __future__ import annotations

import logging
from typing import Optional

import httpx

from src.models.compliance import (
    ComplianceFinding,
    ComplianceFramework,
    Severity,
    SignalSource,
)

logger = logging.getLogger(__name__)

# Compliance patterns to detect in code diffs
COMPLIANCE_PATTERNS = {
    ComplianceFramework.GDPR: [
        "personal_data", "user_email", "ip_address", "cookie",
        "consent", "data_retention", "right_to_delete", "gdpr",
        "data_processing", "privacy_policy",
    ],
    ComplianceFramework.HIPAA: [
        "patient", "medical_record", "health_data", "phi",
        "hipaa", "diagnosis", "treatment", "prescription",
        "ssn", "social_security",
    ],
    ComplianceFramework.SOC2: [
        "access_control", "audit_log", "encryption",
        "password", "api_key", "secret", "credential",
        "authentication", "authorization", "mfa",
    ],
    ComplianceFramework.PCI_DSS: [
        "credit_card", "card_number", "cvv", "payment",
        "cardholder", "pci", "stripe_key", "payment_token",
    ],
}

# High-risk file patterns
HIGH_RISK_PATHS = [
    "auth/", "security/", "encryption/", "privacy/",
    ".env", "config/secrets", "middleware/auth",
]


class PRMonitorAgent:
    """Monitors GitHub PRs for compliance-relevant code changes."""

    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"token {github_token}"} if github_token else {},
            timeout=30.0,
        )

    async def analyze_pr(self, owner: str, repo: str, pr_number: int) -> list[ComplianceFinding]:
        """Analyze a single PR for compliance issues."""
        findings: list[ComplianceFinding] = []

        # Fetch PR diff
        diff = await self._fetch_pr_diff(owner, repo, pr_number)
        if not diff:
            return findings

        # Scan for compliance patterns
        for framework, patterns in COMPLIANCE_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in diff.lower():
                    finding = ComplianceFinding(
                        id=f"pr-{owner}-{repo}-{pr_number}-{framework.value}-{pattern}",
                        source=SignalSource.GITHUB_PR,
                        source_url=f"https://github.com/{owner}/{repo}/pull/{pr_number}",
                        title=f"Potential {framework.value.upper()} relevance: '{pattern}' found in PR #{pr_number}",
                        description=f"The pattern '{pattern}' was detected in PR #{pr_number} of {owner}/{repo}. "
                        f"This may indicate changes relevant to {framework.value.upper()} compliance.",
                        severity=self._assess_severity(pattern, framework),
                        frameworks=[framework],
                        confidence=0.7,
                        raw_content=self._extract_context(diff, pattern),
                    )
                    findings.append(finding)

        # Check high-risk file paths
        files = await self._fetch_pr_files(owner, repo, pr_number)
        for file_path in files:
            for risk_path in HIGH_RISK_PATHS:
                if risk_path in file_path:
                    finding = ComplianceFinding(
                        id=f"pr-{owner}-{repo}-{pr_number}-highrisk-{file_path}",
                        source=SignalSource.GITHUB_PR,
                        source_url=f"https://github.com/{owner}/{repo}/pull/{pr_number}",
                        title=f"High-risk file modified: {file_path}",
                        description=f"File '{file_path}' in a security/compliance-sensitive path was modified.",
                        severity=Severity.HIGH,
                        frameworks=[],
                        confidence=0.8,
                    )
                    findings.append(finding)

        logger.info(f"PR #{pr_number}: {len(findings)} compliance findings")
        return findings

    async def _fetch_pr_diff(self, owner: str, repo: str, pr_number: int) -> Optional[str]:
        """Fetch the diff content of a PR."""
        try:
            resp = await self.client.get(
                f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}",
                headers={"Accept": "application/vnd.github.v3.diff"},
            )
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            logger.error(f"Failed to fetch PR diff: {e}")
            return None

    async def _fetch_pr_files(self, owner: str, repo: str, pr_number: int) -> list[str]:
        """Fetch list of files changed in a PR."""
        try:
            resp = await self.client.get(
                f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
            )
            resp.raise_for_status()
            return [f["filename"] for f in resp.json()]
        except Exception as e:
            logger.error(f"Failed to fetch PR files: {e}")
            return []

    def _assess_severity(self, pattern: str, framework: ComplianceFramework) -> Severity:
        """Assess severity based on pattern and framework."""
        critical_patterns = {"ssn", "social_security", "credit_card", "card_number", "api_key", "secret"}
        high_patterns = {"password", "credential", "patient", "phi", "personal_data"}

        if pattern in critical_patterns:
            return Severity.CRITICAL
        if pattern in high_patterns:
            return Severity.HIGH
        return Severity.MEDIUM

    def _extract_context(self, diff: str, pattern: str, context_lines: int = 3) -> str:
        """Extract surrounding context for a pattern match in a diff."""
        lines = diff.split("\n")
        for i, line in enumerate(lines):
            if pattern.lower() in line.lower():
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                return "\n".join(lines[start:end])
        return ""

    async def close(self):
        await self.client.aclose()
