#!/usr/bin/env python3
"""
Generate realistic-ish mock CSVs for:
- issues.csv       : issue_id, issues_type, issue_title, risk_theme
- controls.csv     : control_id, key_control, control_title, risk_theme
- external_loss.csv: reference_id_code, parent_name, description_of_event, risk_theme
- internal_loss.csv: event_id, event_title, event_type, risk_theme

NOTE: risk_theme is a SINGLE CSV field containing TWO items:
  "<Theme>, <Subtheme>"  (comma-separated in one cell)

Usage (defaults shown):
  python make_mock_risk_data.py --out . \
    --n_issues 200 --n_controls 150 --n_external 120 --n_internal 180
"""
import argparse
import csv
import os
import random
from datetime import datetime

# ------------------------- domain vocab --------------------------------------
# Cleaned themes: slashes removed, '&' -> 'and'
RISK_THEMES = [
    "Cybersecurity",
    "Fraud and Financial Crime",
    "Regulatory Compliance",
    "Third Party Vendor",
    "Operational Resilience",
    "Data Quality Integrity",
    "Technology Change",
    "Conduct and Culture",
    "Model Risk",
    "AML Sanctions",
]

# Clean subthemes (aligned to themes above; no slashes)
RISK_SUBTHEMES = {
    "Cybersecurity": ["Phishing", "Ransomware", "Unauthorized Access", "Data Breach"],
    "Fraud and Financial Crime": ["Card Not Present", "Account Takeover", "Internal Fraud", "Check Fraud"],
    "Regulatory Compliance": ["Reporting Error", "KYC CDD Gap", "MiFID II Breach", "Record Retention"],
    "Third Party Vendor": ["SLA Breach", "Outage", "Data Processing Risk", "Onboarding Gap"],
    "Operational Resilience": ["BCP Gap", "Disaster Recovery", "Single Point of Failure", "Capacity Scaling"],
    "Data Quality Integrity": ["Missing Values", "Duplication", "Lineage Gap", "Reference Data Error"],
    "Technology Change": ["Release Regression", "Config Drift", "Failed Deployment", "Change Collision"],
    "Conduct and Culture": ["Inappropriate Communication", "Sales Practice", "Conflicts of Interest", "Insider Trading"],
    "Model Risk": ["Validation Finding", "Concept Drift", "Calibration Error", "Use Case Misalignment"],
    "AML Sanctions": ["Name Screening Miss", "Alert Backlog", "Evasion Typology", "Sanctions Hit Handling"],
}

ISSUE_TYPES = [
    "Policy Exception",
    "Process Gap",
    "Audit Finding",
    "Regulatory Finding",
    "Incident Post-Mortem Action",
    "Risk Assessment Action",
]

CONTROL_TITLES = [
    "Daily Reconciliation Review",
    "Transaction Monitoring Ruleset",
    "Privileged Access Review",
    "Release Change Approval",
    "KYC Periodic Refresh",
    "Vendor SLA Monitoring",
    "Model Performance Backtesting",
    "Data Quality Dashboard Check",
    "Sanctions Screening Tuning",
    "Disaster Recovery Drill",
]

EVENT_TYPES_INTERNAL = [
    "System Outage",
    "Data Entry Error",
    "Processing Error",
    "Information Security Incident",
    "Theft or Fraud",
    "Compliance Breach",
]

PARENTS_EXTERNAL = [
    "Global Payments Ltd",
    "FinPay Services AG",
    "NorthBridge Bank plc",
    "EuroTrade Clearing SA",
    "Acme Vendor Corp",
    "CloudCompute Inc",
]

# ------------------------- helpers -------------------------------------------
def seed_everything(seed: int = 1337):
    random.seed(seed)

def rand_code(prefix: str, n_digits: int = 5) -> str:
    return f"{prefix}-{datetime.now().year}-{random.randint(10**(n_digits-1), 10**n_digits-1)}"

def rand_words(n: int) -> str:
    sample = [
        "automated", "batch", "payment", "gateway", "latency", "spike", "customer",
        "onboarding", "workflow", "misconfiguration", "threshold", "alert",
        "reconciliation", "exception", "queue", "retry", "timeout", "security",
        "control", "policy", "breach", "investigation", "manual", "override",
        "validation", "reference", "dataset", "integration", "migration"
    ]
    words = [random.choice(sample) for _ in range(n)]
    return " ".join(words).capitalize()

def choose_theme_and_sub() -> tuple[str, str]:
    theme = random.choice(RISK_THEMES)
    sub = random.choice(RISK_SUBTHEMES[theme])
    return theme, sub

def maybe_suffix(text: str) -> str:
    # 50% chance to add a realistic qualifier
    suffixes = [" – Phase 1", " (Interim)", " – Pilot", " (Remediation)", " – v2"]
    return text + random.choice(suffixes) if random.random() < 0.5 else text

def combine_theme(theme: str, sub: str) -> str:
    # Single CSV cell holding two items, comma-separated
    return f"{theme}, {sub}"

# ------------------------- row builders --------------------------------------
def make_issue_row() -> dict:
    theme, sub = choose_theme_and_sub()
    issue_type = random.choice(ISSUE_TYPES)
    title = maybe_suffix(
        f"{issue_type}: {rand_words(2)} {random.choice(['control','process','report','feed'])} gap"
    )
    return {
        "issue_id": rand_code("ISS"),
        "issues_type": issue_type,
        "issue_title": title,
        "risk_theme": combine_theme(theme, sub),
    }

def make_control_row() -> dict:
    theme, sub = choose_theme_and_sub()
    title = random.choice(CONTROL_TITLES)
    key = random.choice(["Yes", "No"])
    return {
        "control_id": rand_code("CTRL"),
        "key_control": key,
        "control_title": title,
        "risk_theme": combine_theme(theme, sub),
    }

def make_external_loss_row() -> dict:
    theme, sub = choose_theme_and_sub()
    parent = random.choice(PARENTS_EXTERNAL)
    desc = (
        f"{parent} experienced {random.choice(['a service disruption','a security incident','an operations failure'])} "
        f"leading to {random.choice(['delayed settlements','data exposure','failed end-of-day processing'])}. "
        f"Root cause linked to {sub.lower()}."
    )
    return {
        "reference_id_code": rand_code("EXT"),
        "parent_name": parent,
        "description_of_event": desc,
        "risk_theme": combine_theme(theme, sub),
    }

def make_internal_loss_row() -> dict:
    theme, sub = choose_theme_and_sub()
    etype = random.choice(EVENT_TYPES_INTERNAL)
    title = f"{etype}: {rand_words(3)}"
    return {
        "event_id": rand_code("INT"),
        "event_title": title,
        "event_type": etype,
        "risk_theme": combine_theme(theme, sub),
    }

# ------------------------- writers -------------------------------------------
def write_csv(path: str, fieldnames: list[str], rows: list[dict]):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

# ------------------------- main ----------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Generate mock risk datasets as CSVs.")
    parser.add_argument("--out", default=".", help="Output directory")
    parser.add_argument("--n_issues", type=int, default=200)
    parser.add_argument("--n_controls", type=int, default=150)
    parser.add_argument("--n_external", type=int, default=120)
    parser.add_argument("--n_internal", type=int, default=180)
    parser.add_argument("--seed", type=int, default=1337)
    args = parser.parse_args()

    seed_everything(args.seed)

    issues_rows = [make_issue_row() for _ in range(args.n_issues)]
    controls_rows = [make_control_row() for _ in range(args.n_controls)]
    external_rows = [make_external_loss_row() for _ in range(args.n_external)]
    internal_rows = [make_internal_loss_row() for _ in range(args.n_internal)]

    write_csv(
        os.path.join(args.out, "issues.csv"),
        ["issue_id", "issues_type", "issue_title", "risk_theme"],
        issues_rows,
    )
    write_csv(
        os.path.join(args.out, "controls.csv"),
        ["control_id", "key_control", "control_title", "risk_theme"],
        controls_rows,
    )
    write_csv(
        os.path.join(args.out, "external_loss.csv"),
        ["reference_id_code", "parent_name", "description_of_event", "risk_theme"],
        external_rows,
    )
    write_csv(
        os.path.join(args.out, "internal_loss.csv"),
        ["event_id", "event_title", "event_type", "risk_theme"],
        internal_rows,
    )

    print(f"✓ Generated CSVs in: {os.path.abspath(args.out)}")
    print('Example risk_theme format: "Third Party Vendor, SLA Breach"')

if __name__ == "__main__":
    main()