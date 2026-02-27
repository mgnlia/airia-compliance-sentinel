export type Severity = "critical" | "high" | "medium" | "low";
export type Framework = "GDPR" | "SOC2" | "HIPAA" | "PCI-DSS";

export interface Finding {
  id: string; title: string; description: string; severity: Severity;
  framework: Framework; source: string; confidence: number; timestamp: string;
}
export interface AgentStatus {
  name: string; active: boolean; lastHeartbeat: string; findingsCount: number;
}
export interface Review {
  id: string; findingId: string; title: string; severity: Severity;
  status: "pending" | "approved" | "dismissed" | "escalated"; assignee: string; createdAt: string;
}

export const riskScore = 67;
export const frameworkScores: Record<string, number> = { GDPR: 72, SOC2: 58, HIPAA: 81, "PCI-DSS": 45 };

export const agents: AgentStatus[] = [
  { name: "PR Monitor", active: true, lastHeartbeat: "2m ago", findingsCount: 12 },
  { name: "Slack Monitor", active: true, lastHeartbeat: "30s ago", findingsCount: 8 },
  { name: "Doc Crawler", active: false, lastHeartbeat: "15m ago", findingsCount: 3 },
  { name: "Orchestrator", active: true, lastHeartbeat: "5s ago", findingsCount: 0 },
];

export const findings: Finding[] = [
  { id: "F-001", title: "PII exposure in user-export endpoint", description: "PR #847 adds a CSV export that includes unmasked email addresses and phone numbers, violating GDPR Article 25 data minimization.", severity: "critical", framework: "GDPR", source: "PR #847", confidence: 0.94, timestamp: "2 min ago" },
  { id: "F-002", title: "Missing encryption-at-rest for audit logs", description: "New S3 bucket for audit logs lacks SSE-KMS encryption, failing SOC2 CC6.1 control.", severity: "high", framework: "SOC2", source: "PR #832", confidence: 0.87, timestamp: "18 min ago" },
  { id: "F-003", title: "Slack discussion of patient data in #general", description: "Team member shared patient identifiers in a public Slack channel, potential HIPAA violation.", severity: "high", framework: "HIPAA", source: "Slack #general", confidence: 0.91, timestamp: "45 min ago" },
  { id: "F-004", title: "Outdated data retention policy document", description: "Data retention policy references EU-US Privacy Shield (invalidated 2020), needs update to reflect current DPF.", severity: "medium", framework: "GDPR", source: "policy-docs/retention.md", confidence: 0.78, timestamp: "2 hours ago" },
  { id: "F-005", title: "Card data logged in debug mode", description: "Debug logging captures full PAN in payment service when LOG_LEVEL=debug, violating PCI-DSS Req 3.4.", severity: "critical", framework: "PCI-DSS", source: "PR #851", confidence: 0.96, timestamp: "5 min ago" },
  { id: "F-006", title: "Access review documentation gap", description: "Q1 2026 access review for production systems not yet documented. SOC2 CC6.2 requires quarterly reviews.", severity: "medium", framework: "SOC2", source: "compliance-docs/access-reviews/", confidence: 0.72, timestamp: "3 hours ago" },
  { id: "F-007", title: "Third-party SDK transmitting location data", description: "Analytics SDK v4.2 sends device GPS coordinates to third-party servers without explicit consent flow.", severity: "high", framework: "GDPR", source: "PR #839", confidence: 0.85, timestamp: "1 hour ago" },
];

export const reviews: Review[] = [
  { id: "R-001", findingId: "F-001", title: "PII exposure in user-export endpoint", severity: "critical", status: "pending", assignee: "Security Team", createdAt: "2 min ago" },
  { id: "R-002", findingId: "F-005", title: "Card data logged in debug mode", severity: "critical", status: "pending", assignee: "Payment Team", createdAt: "5 min ago" },
  { id: "R-003", findingId: "F-003", title: "Slack discussion of patient data", severity: "high", status: "pending", assignee: "Compliance Officer", createdAt: "45 min ago" },
  { id: "R-004", findingId: "F-004", title: "Outdated data retention policy", severity: "medium", status: "approved", assignee: "Legal Team", createdAt: "2 hours ago" },
  { id: "R-005", findingId: "F-006", title: "Access review documentation gap", severity: "medium", status: "dismissed", assignee: "IT Ops", createdAt: "3 hours ago" },
];

export const severityColor: Record<Severity, string> = {
  critical: "bg-red-500/20 text-red-400 border-red-500/30",
  high: "bg-orange-500/20 text-orange-400 border-orange-500/30",
  medium: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  low: "bg-green-500/20 text-green-400 border-green-500/30",
};
