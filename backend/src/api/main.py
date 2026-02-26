"""FastAPI backend for Compliance Sentinel dashboard."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.agents.orchestrator import OrchestratorAgent
from src.agents.pr_monitor import PRMonitorAgent
from src.agents.slack_monitor import SlackMonitorAgent
from src.agents.doc_crawler import DocCrawlerAgent
from src.models.compliance import ComplianceFramework, Severity

# Global agent instances
orchestrator = OrchestratorAgent()
pr_monitor = PRMonitorAgent()
slack_monitor = SlackMonitorAgent()
doc_crawler = DocCrawlerAgent()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown."""
    orchestrator.update_agent_status("pr_monitor", is_active=True)
    orchestrator.update_agent_status("slack_monitor", is_active=True)
    orchestrator.update_agent_status("doc_crawler", is_active=True)
    yield
    await pr_monitor.close()


app = FastAPI(
    title="Compliance Sentinel API",
    description="Multi-Agent RegTech Compliance Monitoring System",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request models ---

class AnalyzePRRequest(BaseModel):
    owner: str
    repo: str
    pr_number: int


class AnalyzeSlackRequest(BaseModel):
    channel: str
    user: str
    text: str
    timestamp: str = ""


class AnalyzeDocRequest(BaseModel):
    doc_id: str
    title: str
    content: str
    doc_url: Optional[str] = None


class ResolveReviewRequest(BaseModel):
    status: str  # approved | dismissed | escalated
    reviewer: str
    notes: Optional[str] = None


# --- Endpoints ---

@app.get("/")
async def root():
    return {"service": "Compliance Sentinel", "version": "0.1.0", "status": "operational"}


@app.get("/health")
async def health():
    return {"status": "healthy", "agents": len(orchestrator.agent_statuses)}


@app.get("/dashboard")
async def dashboard():
    """Get full dashboard summary."""
    return orchestrator.get_dashboard_summary()


@app.get("/risk")
async def risk_score():
    """Get current risk score."""
    return orchestrator.get_risk_score().model_dump()


@app.get("/findings")
async def list_findings(
    severity: Optional[Severity] = None,
    framework: Optional[ComplianceFramework] = None,
    limit: int = 50,
):
    """List findings with optional filters."""
    findings = orchestrator.findings

    if severity:
        findings = [f for f in findings if f.severity == severity]
    if framework:
        findings = [f for f in findings if framework in f.frameworks]

    findings = sorted(findings, key=lambda x: x.detected_at, reverse=True)[:limit]
    return [f.model_dump() for f in findings]


@app.post("/analyze/pr")
async def analyze_pr(req: AnalyzePRRequest):
    """Analyze a GitHub PR for compliance issues."""
    findings = await pr_monitor.analyze_pr(req.owner, req.repo, req.pr_number)
    risk = orchestrator.ingest_findings(findings)
    orchestrator.update_agent_status("pr_monitor", is_active=True, findings_today=len(findings))
    return {
        "findings_count": len(findings),
        "risk_score": risk.model_dump(),
        "findings": [f.model_dump() for f in findings],
    }


@app.post("/analyze/slack")
async def analyze_slack(req: AnalyzeSlackRequest):
    """Analyze a Slack message for compliance signals."""
    findings = await slack_monitor.analyze_message(
        req.channel, req.user, req.text, req.timestamp
    )
    risk = orchestrator.ingest_findings(findings)
    orchestrator.update_agent_status("slack_monitor", is_active=True, findings_today=len(findings))
    return {
        "findings_count": len(findings),
        "risk_score": risk.model_dump(),
        "findings": [f.model_dump() for f in findings],
    }


@app.post("/analyze/document")
async def analyze_document(req: AnalyzeDocRequest):
    """Analyze a document for compliance issues."""
    findings = await doc_crawler.analyze_document(
        doc_id=req.doc_id,
        title=req.title,
        content=req.content,
        doc_url=req.doc_url,
    )
    risk = orchestrator.ingest_findings(findings)
    orchestrator.update_agent_status("doc_crawler", is_active=True, findings_today=len(findings))
    return {
        "findings_count": len(findings),
        "risk_score": risk.model_dump(),
        "findings": [f.model_dump() for f in findings],
    }


@app.get("/reviews")
async def list_reviews(status: Optional[str] = None):
    """List HITL reviews."""
    reviews = orchestrator.reviews
    if status:
        reviews = [r for r in reviews if r.status == status]
    return [r.model_dump() for r in reviews]


@app.post("/reviews/{review_id}/resolve")
async def resolve_review(review_id: str, req: ResolveReviewRequest):
    """Resolve a HITL review."""
    review = orchestrator.resolve_review(review_id, req.status, req.reviewer, req.notes)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review.model_dump()
