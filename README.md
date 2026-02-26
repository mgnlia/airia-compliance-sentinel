# 🛡️ Compliance Sentinel

**Multi-Agent RegTech Compliance Monitoring System** — Built with [Airia](https://airia.com) for the [Airia AI Agents Hackathon](https://airia-hackathon.devpost.com/)

## Problem

Organizations struggle to maintain regulatory compliance (GDPR, SOC2, HIPAA) across their entire tech stack. Code changes, team communications, and documentation can silently drift from compliance policies — creating risk that's only discovered during costly audits.

## Solution

Compliance Sentinel is a multi-agent system that **continuously monitors** your GitHub PRs, Slack conversations, and documents to detect regulatory drift in real-time. It aggregates signals across all channels, scores risk, and triggers human-in-the-loop review before violations reach production.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Orchestrator Agent              │
│         (Risk Aggregation + HITL Triggers)       │
├──────────┬──────────────┬───────────────────────┤
│  PR      │   Slack      │   Document            │
│  Monitor │   Monitor    │   Crawler             │
│  Agent   │   Agent      │   Agent               │
├──────────┼──────────────┼───────────────────────┤
│ GitHub   │   Slack      │   SharePoint /        │
│ Webhooks │   Events     │   Google Docs         │
└──────────┴──────────────┴───────────────────────┘
                    ↓
        ┌───────────────────────┐
        │   Next.js Dashboard   │
        │  Real-time Risk Feed  │
        │   HITL Approval UI    │
        └───────────────────────┘
```

### Agents

| Agent | Role | Data Source |
|-------|------|-------------|
| **PR Monitor** | Scans code diffs for compliance-relevant changes | GitHub webhooks |
| **Slack Monitor** | Flags policy-relevant conversations | Slack events API |
| **Document Crawler** | Detects outdated compliance language | Document APIs |
| **Orchestrator** | Aggregates signals, scores risk, triggers HITL review | All agents |

## Tech Stack

- **Agent Platform:** [Airia](https://airia.com) — Agent orchestration & community publishing
- **Backend:** Python 3.12+ / FastAPI / uv
- **Frontend:** Next.js 14 / React / Tailwind CSS
- **AI Models:** Claude / GPT-4 via Airia platform
- **Deployment:** Railway (backend) + Vercel (frontend)

## Quick Start

```bash
# Backend
cd backend
uv sync
uv run uvicorn src.api.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Hackathon Track

**Active Agents** — Multi-agent workflows across your tech stack

## Team

Built by [mgnlia](https://github.com/mgnlia)

## License

MIT
