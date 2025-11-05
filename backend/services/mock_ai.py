"""Mock AI functions for testing and development."""
import hashlib
import random
from typing import Any, Dict, List


def _seed_random(id_str: str) -> None:
    """Seed random based on ID for deterministic output."""
    hash_val = int(hashlib.md5(id_str.encode()).hexdigest()[:8], 16)
    random.seed(hash_val)


def _reasoning_lines(topic: str) -> List[str]:
    phrases = [
        "Historic incidents show recurring gaps.",
        "Control evidence indicates limited coverage.",
        "Process walkthroughs highlight missing ownership.",
        "Audit observations describe inconsistent execution.",
        "Frontline testing reveals delayed remediation.",
    ]
    return [
        f"{topic}: {random.choice(phrases)}",
        f"Further monitoring recommended around {topic.lower()}.",
    ]


def _pick_distinct(values: List[str]) -> List[str]:
    first = random.choice(values)
    remaining = [v for v in values if v != first]
    second = random.choice(remaining) if remaining else first
    return [first, second]


# ---------------------------------------------------------------------------
# Taxonomy helpers shared across datasets

ISSUE_PRIMARY = [
    "Operational Resilience",
    "Conduct & Culture",
    "Technology Change",
    "Regulatory Compliance",
    "Fraud & Financial Crime",
]

ISSUE_SECONDARY = [
    "Process Oversight",
    "Training Gap",
    "Latency Management",
    "Data Integrity",
    "Vendor Oversight",
    "Threshold Calibration",
]

ROOT_CAUSE_PRIMARY = [
    "Process Breakdown",
    "Human Factors",
    "Technology Defect",
    "Governance Gap",
    "Third-Party Exposure",
]

ROOT_CAUSE_SECONDARY = [
    "Change Collision",
    "Insufficient Monitoring",
    "Incomplete Playbook",
    "Policy Misalignment",
    "Delayed Detection",
]

CONTROL_TAXONOMY_PRIMARY = [
    "Preventive Control",
    "Detective Control",
    "Corrective Control",
    "Compensating Control",
]

CONTROL_TAXONOMY_SECONDARY = [
    "Application Embedded",
    "Procedural",
    "Automated Monitoring",
    "Manual Review",
]


# ---------------------------------------------------------------------------
# Issues / Losses

def get_issues_taxonomy(id: str, context: str) -> Dict[str, Any]:
    _seed_random(id)
    primary, secondary = _pick_distinct(ISSUE_PRIMARY + ISSUE_SECONDARY)
    return {
        "primary_taxonomy": primary,
        "secondary_taxonomy": secondary,
        "primary_taxonomy_reasoning": _reasoning_lines(primary),
        "secondary_taxonomy_reasoning": _reasoning_lines(secondary),
    }


def get_issues_root_cause(id: str, context: str) -> Dict[str, Any]:
    _seed_random(id)
    primary, secondary = _pick_distinct(ROOT_CAUSE_PRIMARY + ROOT_CAUSE_SECONDARY)
    return {
        "primary_root_cause": primary,
        "secondary_root_cause": secondary,
        "primary_root_cause_reasoning": _reasoning_lines(primary),
        "secondary_root_cause_reasoning": _reasoning_lines(secondary),
    }


def get_issues_enrichment(id: str, context: str) -> Dict[str, Any]:
    _seed_random(id)
    return {
        "summary": f"Case {id} highlights {random.choice(['persistent gaps', 'heightened exposure', 'escalating oversight needs'])} within the current workflow.",
        "impacts": {
            "financial": random.choice(["High", "Medium", "Low"]),
            "reputation": random.choice(["Moderate", "Elevated", "Contained"]),
            "regulatory": random.choice(["Reportable", "Monitoring Only", "Advisory"]),
        },
        "factors": {
            "internal": random.sample(
                ["Process complexity", "Legacy tooling", "Manual workarounds", "Competing priorities"], 2
            ),
            "external": random.sample(
                ["Vendor dependency", "Market pressure", "Regulatory change", "Customer expectations"], 2
            ),
        },
        "dealing": {
            "immediate": random.choice(
                [
                    "Stabilize impacted workflow and add oversight.",
                    "Pause non-critical deployments and conduct validation.",
                    "Issue interim guidance to frontline teams.",
                ]
            ),
            "long_term": random.choice(
                [
                    "Embed automated controls and real-time monitoring.",
                    "Refresh policy playbooks and training cadence.",
                    "Strengthen handoffs with accountable owners.",
                ]
            ),
            "owner": random.choice(["First Line", "Second Line", "Product Team", "Operations Lead"]),
        },
    }


# ---------------------------------------------------------------------------
# Controls

def get_controls_taxonomy(id: str, context: str) -> Dict[str, Any]:
    _seed_random(id)
    primary, secondary = _pick_distinct(CONTROL_TAXONOMY_PRIMARY + CONTROL_TAXONOMY_SECONDARY)
    return {
        "primary_taxonomy": primary,
        "secondary_taxonomy": secondary,
        "primary_taxonomy_reasoning": _reasoning_lines(primary),
        "secondary_taxonomy_reasoning": _reasoning_lines(secondary),
    }


def get_controls_root_cause(id: str, context: str) -> Dict[str, Any]:
    # For controls this describes why the control is critical or what risks it mitigates
    return get_issues_root_cause(id, context)


def get_controls_enrichment(id: str, context: str) -> Dict[str, Any]:
    _seed_random(id)
    return {
        "summary": f"Control {id} addresses the primary risk scenario described in the context.",
        "5ws": {
            "who": random.choice(["Risk Operations", "Front Office", "Technology", "Compliance"]),
            "what": random.choice(
                ["Monitors critical thresholds", "Approves key changes", "Reviews exception queues", "Validates inputs"]
            ),
            "when": random.choice(["Daily", "Weekly", "Per deployment", "Real-time"]),
            "where": random.choice(["Global platform", "Regional process", "Shared service center", "Cloud workload"]),
            "why": random.choice(
                ["Maintains regulatory obligations", "Prevents fraud scenarios", "Ensures service availability", "Protects customer outcomes"]
            ),
        },
        "factors": {
            "coverage": random.choice(["End-to-end", "Partial", "Targeted"]),
            "automation_level": random.choice(["Manual", "Semi-automated", "Fully automated"]),
            "dependencies": random.sample(
                ["IAM", "Logging", "Alerting", "Vendor feeds", "Ticketing"], 2
            ),
        },
        "dealing": {
            "immediate": random.choice(
                [
                    "Validate the latest control execution evidence.",
                    "Confirm fallback procedures and manual oversight.",
                    "Escalate exceptions to accountable owner.",
                ]
            ),
            "long_term": random.choice(
                [
                    "Integrate telemetry to monitor adherence.",
                    "Embed control within deployment toolchain.",
                    "Consolidate duplicative steps with automation.",
                ]
            ),
            "owner": random.choice(["Control Office", "Product Risk Lead", "Process Owner"]),
        },
    }


# ---------------------------------------------------------------------------
# Loss datasets reuse issue logic

def get_external_loss_taxonomy(id: str, context: str) -> Dict[str, Any]:
    return get_issues_taxonomy(id, context)


def get_external_loss_root_cause(id: str, context: str) -> Dict[str, Any]:
    return get_issues_root_cause(id, context)


def get_external_loss_enrichment(id: str, context: str) -> Dict[str, Any]:
    return get_issues_enrichment(id, context)


def get_internal_loss_taxonomy(id: str, context: str) -> Dict[str, Any]:
    return get_issues_taxonomy(id, context)


def get_internal_loss_root_cause(id: str, context: str) -> Dict[str, Any]:
    return get_issues_root_cause(id, context)


def get_internal_loss_enrichment(id: str, context: str) -> Dict[str, Any]:
    return get_issues_enrichment(id, context)

