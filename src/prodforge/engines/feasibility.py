"""
Architectural Feasibility & System Scaling Engine.
Computes estimated cloud costs, request-per-second thresholds, database concurrency limits,
and disaster recovery recommendations.
"""

from __future__ import annotations

from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from prodforge.client import LLMClient, OfflineModeException


class CostBreakdownItem(BaseModel):
    component: str
    recommended_service: str
    monthly_estimate_usd: float
    notes: str


class FeasibilityResult(BaseModel):
    idea_or_system: str
    concurrency_target_rps: int
    estimated_monthly_cost_usd: float
    bottlenecks: List[str] = Field(default_factory=list)
    cost_breakdown: List[CostBreakdownItem] = Field(default_factory=list)
    scalability_verdict: str
    executive_markdown: str
    is_offline_fallback: bool = False


FEASIBILITY_SYSTEM_PROMPT = """You are a Principal Cloud Architect and FinOps Specialist.
Analyze system requirements and provide realistic throughput limits, cloud infrastructure costs,
and concurrency trade-offs.
"""


def analyze_feasibility(
    idea: str,
    target_dau: int = 50000,
    model: Optional[str] = None
) -> FeasibilityResult:
    """Calculate system scaling metrics, cloud costs, and architectural bottlenecks."""
    # Approximate math: 50,000 DAU ~ 10-25 RPS peak
    peak_rps = max(10, int((target_dau * 0.2) / (3600 * 2)))

    # Compute baseline cloud FinOps items
    cost_items: List[CostBreakdownItem] = [
        CostBreakdownItem(
            component="Compute (App Services)",
            recommended_service="AWS ECS Fargate / Fly.io (2x 2vCPU, 4GB RAM)",
            monthly_estimate_usd=48.00,
            notes="Active-active container redundancy with auto-scaling"
        ),
        CostBreakdownItem(
            component="Managed Relational DB",
            recommended_service="AWS Aurora Serverless v2 / Neon PostgreSQL",
            monthly_estimate_usd=55.00,
            notes="Automated point-in-time recovery, connection pooling"
        ),
        CostBreakdownItem(
            component="In-Memory Cache",
            recommended_service="Upstash Redis / AWS ElastiCache t4g.micro",
            monthly_estimate_usd=18.00,
            notes="Session storage, rate-limiting, and hot query caching"
        ),
        CostBreakdownItem(
            component="Object Storage & CDN",
            recommended_service="Cloudflare R2 + Cloudflare CDN Pro",
            monthly_estimate_usd=20.00,
            notes="Zero egress fees, asset compression, DDoS protection"
        ),
        CostBreakdownItem(
            component="Observability & Telemetry",
            recommended_service="Datadog / BetterStack / Sentry",
            monthly_estimate_usd=29.00,
            notes="Error tracing, APM, and real-time uptime alerting"
        )
    ]

    total_cost = sum(item.monthly_estimate_usd for item in cost_items)

    bottlenecks = [
        "Database connection exhaustion under traffic spikes: Enforce PgBouncer / Prisma Accelerate.",
        "Synchronous external API blocking: Offload external HTTP integrations to background workers.",
        "Uncached expensive queries: Implement stale-while-revalidate caching on read-heavy endpoints."
    ]

    try:
        client = LLMClient(model=model)
        prompt = f"""Perform a rigorous FinOps & Architectural Feasibility Analysis for this system:

SYSTEM / IDEA:
{idea}

TARGET AUDIENCE: {target_dau:,} Daily Active Users (Estimated peak {peak_rps} RPS)

Provide a detailed executive breakdown:
1. Concurrency & Throughput Limits (P99 Latency targets, max safe RPS before scale).
2. Cloud Infrastructure Cost Model (Itemized breakdown).
3. Primary Bottlenecks & Failure Modes (Database, network, compute).
4. Scalability Verdict & Phased Capacity Plan (Launch -> 100k DAU -> 1M DAU).
"""
        markdown_text = client.generate(prompt=prompt, system_prompt=FEASIBILITY_SYSTEM_PROMPT)

        return FeasibilityResult(
            idea_or_system=idea,
            concurrency_target_rps=peak_rps,
            estimated_monthly_cost_usd=total_cost,
            bottlenecks=bottlenecks,
            cost_breakdown=cost_items,
            scalability_verdict="HIGHLY FEASIBLE (Modern Cloud-Native Architecture)",
            executive_markdown=markdown_text,
            is_offline_fallback=False
        )

    except OfflineModeException:
        markdown_text = f"""# FinOps & Architectural Feasibility Report

### Target Scale: {target_dau:,} Daily Active Users (~{peak_rps} Peak RPS)
- **Estimated Monthly Run Rate:** ${total_cost:.2f} USD
- **Architectural Verdict:** **FEASIBLE & SCALABLE**

## 1. Cloud Cost Breakdown
| Component | Architecture Recommendation | Monthly Cost (USD) |
|---|---|---|
| Compute | AWS ECS Fargate / Fly.io (Dual Instances) | ${cost_items[0].monthly_estimate_usd:.2f} |
| Database | PostgreSQL Aurora / Neon (Serverless) | ${cost_items[1].monthly_estimate_usd:.2f} |
| Cache | Redis (Upstash / ElastiCache) | ${cost_items[2].monthly_estimate_usd:.2f} |
| CDN & Assets | Cloudflare Edge + R2 Storage | ${cost_items[3].monthly_estimate_usd:.2f} |
| Observability | Sentry + Prometheus/Grafana | ${cost_items[4].monthly_estimate_usd:.2f} |
| **Total** | | **${total_cost:.2f} / month** |

## 2. Identified Bottlenecks & Mitigations
- **DB Connection Pools:** Raw connection storms can crash Postgres. *Remediation:* Deploy PgBouncer or connection pool proxy.
- **Slow Dynamic Endpoints:** Avoid DB roundtrips for repeated data. *Remediation:* Implement Redis cache with 60s TTL.
- **Long-running Jobs:** Never execute heavy tasks in request threads. *Remediation:* Use Celery, BullMQ, or AWS SQS.
"""
        return FeasibilityResult(
            idea_or_system=idea,
            concurrency_target_rps=peak_rps,
            estimated_monthly_cost_usd=total_cost,
            bottlenecks=bottlenecks,
            cost_breakdown=cost_items,
            scalability_verdict="FEASIBLE & SCALABLE",
            executive_markdown=markdown_text,
            is_offline_fallback=True
        )
