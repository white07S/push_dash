"""Mock AI functions for testing and development."""
import hashlib
import random
from typing import Dict, List, Any
from datetime import datetime

def _seed_random(id_str: str) -> None:
    """Seed random based on ID for deterministic output."""
    hash_val = int(hashlib.md5(id_str.encode()).hexdigest()[:8], 16)
    random.seed(hash_val)

def get_controls_ai_taxonomy(id: str, description: str) -> Dict[str, Any]:
    """Mock AI taxonomy generation for controls."""
    _seed_random(id)

    taxonomies = [
        ["Fraud", "Cyber"],
        ["Operational", "Third-Party"],
        ["Compliance", "Fraud"],
        ["Cyber", "Data Privacy"],
        ["Financial", "Market Risk"],
        ["Technology", "Cyber", "Cloud"],
        ["Regulatory", "Compliance"],
        ["Third-Party", "Vendor Risk"],
        ["Operational", "Process"],
        ["Fraud", "Anti-Money Laundering"]
    ]

    selected = random.choice(taxonomies)

    return {
        "ai_taxonomy": selected,
        "confidence": round(random.uniform(0.75, 0.99), 2),
        "reasoning": f"Based on analysis of the control description, identified {len(selected)} risk categories"
    }

def get_controls_ai_root_causes(id: str, description: str) -> Dict[str, Any]:
    """Mock root cause analysis for controls."""
    _seed_random(id)

    root_causes = [
        {
            "category": "Process Gap",
            "description": "Lack of standardized procedures",
            "severity": "High",
            "likelihood": "Medium"
        },
        {
            "category": "Technology Failure",
            "description": "System integration issues",
            "severity": "Medium",
            "likelihood": "Low"
        },
        {
            "category": "Human Error",
            "description": "Insufficient training",
            "severity": "Medium",
            "likelihood": "High"
        }
    ]

    num_causes = random.randint(1, 3)
    selected_causes = random.sample(root_causes, num_causes)

    return {
        "root_causes": selected_causes,
        "total_risk_score": round(random.uniform(3.0, 8.5), 1),
        "recommendations": [
            "Implement automated monitoring",
            "Enhance training programs",
            "Review and update procedures quarterly"
        ][:num_causes]
    }

def get_controls_ai_enrichment(id: str, description: str) -> Dict[str, Any]:
    """Mock enrichment data for controls."""
    _seed_random(id)

    entities = [
        {"type": "Department", "name": "Risk Management", "relevance": 0.9},
        {"type": "System", "name": "SAP Finance", "relevance": 0.8},
        {"type": "Regulation", "name": "SOX Compliance", "relevance": 0.85},
        {"type": "Process", "name": "Payment Authorization", "relevance": 0.75},
        {"type": "Technology", "name": "AWS Cloud", "relevance": 0.7}
    ]

    num_entities = random.randint(2, 4)
    selected_entities = random.sample(entities, num_entities)

    links = [
        {"type": "reference", "url": "https://internal.docs/control-framework", "title": "Control Framework Guide"},
        {"type": "policy", "url": "https://policies.corp/risk-management", "title": "Risk Management Policy"},
        {"type": "training", "url": "https://training.corp/controls-101", "title": "Controls Training Module"}
    ]

    num_links = random.randint(1, 3)
    selected_links = random.sample(links, num_links)

    return {
        "entities": selected_entities,
        "links": selected_links,
        "metadata": {
            "last_reviewed": "2024-10-15",
            "review_frequency": "Quarterly",
            "owner": "Risk Department"
        }
    }

def get_controls_similar_controls(id: str, description: str) -> Dict[str, Any]:
    """Mock similar controls identification."""
    _seed_random(id)

    # Generate similar control IDs
    base_num = int(''.join(filter(str.isdigit, id)) or '100')
    similar_ids = []

    for i in range(random.randint(3, 7)):
        offset = random.randint(1, 50)
        similar_id = f"CTR-{base_num + offset:04d}"
        if similar_id != id:
            similar_ids.append({
                "control_id": similar_id,
                "similarity_score": round(random.uniform(0.65, 0.95), 2),
                "common_tags": random.sample(["fraud", "cyber", "operational", "compliance"], random.randint(1, 3))
            })

    similar_ids.sort(key=lambda x: x['similarity_score'], reverse=True)

    return {
        "similar_controls": similar_ids[:5],
        "clustering_method": "semantic_similarity",
        "threshold": 0.65
    }

def get_external_loss_ai_taxonomy(id: str, description: str) -> Dict[str, Any]:
    """Mock AI taxonomy for external losses."""
    _seed_random(id)

    taxonomies = [
        ["Market Risk", "Trading"],
        ["Credit Risk", "Default"],
        ["Operational", "External Fraud"],
        ["Cyber", "Data Breach"],
        ["Regulatory", "Fine"],
        ["Natural Disaster", "Business Continuity"],
        ["Third-Party", "Vendor Failure"],
        ["Litigation", "Legal"]
    ]

    selected = random.choice(taxonomies)

    return {
        "ai_taxonomy": selected,
        "confidence": round(random.uniform(0.70, 0.95), 2),
        "impact_assessment": random.choice(["High", "Medium", "Low"]),
        "recovery_time": f"{random.randint(1, 90)} days"
    }

def get_external_loss_ai_root_causes(id: str, description: str) -> Dict[str, Any]:
    """Mock root cause analysis for external losses."""
    _seed_random(id)

    root_causes = [
        {
            "category": "Market Conditions",
            "description": "Adverse market movements",
            "impact": "High",
            "controllable": False
        },
        {
            "category": "Counterparty Risk",
            "description": "Counterparty default",
            "impact": "Medium",
            "controllable": True
        },
        {
            "category": "External Event",
            "description": "Regulatory change",
            "impact": "Medium",
            "controllable": False
        }
    ]

    num_causes = random.randint(1, 3)
    selected_causes = random.sample(root_causes, num_causes)

    return {
        "root_causes": selected_causes,
        "loss_amount": f"${random.randint(10000, 5000000):,}",
        "recovery_status": random.choice(["Pending", "Partial", "Complete", "Written Off"]),
        "lessons_learned": [
            "Enhance monitoring systems",
            "Improve hedging strategies",
            "Update risk models"
        ][:num_causes]
    }

def get_external_loss_ai_enrichment(id: str, description: str) -> Dict[str, Any]:
    """Mock enrichment for external losses."""
    _seed_random(id)

    return {
        "entities": [
            {"type": "Industry", "name": random.choice(["Banking", "Insurance", "Asset Management"]), "relevance": 0.9},
            {"type": "Region", "name": random.choice(["North America", "Europe", "Asia Pacific"]), "relevance": 0.8},
            {"type": "Product", "name": random.choice(["Derivatives", "Loans", "Securities"]), "relevance": 0.85}
        ],
        "similar_incidents": [
            {"date": "2024-03-15", "loss_amount": f"${random.randint(50000, 2000000):,}", "similarity": 0.78},
            {"date": "2024-01-20", "loss_amount": f"${random.randint(50000, 2000000):,}", "similarity": 0.72}
        ],
        "regulatory_implications": random.choice(["Report to regulator required", "No regulatory impact", "Under review"])
    }

def get_external_loss_similar_external_loss(id: str, description: str) -> Dict[str, Any]:
    """Mock similar external losses."""
    _seed_random(id)

    base_num = int(''.join(filter(str.isdigit, id)) or '1000')
    similar = []

    for i in range(random.randint(2, 5)):
        offset = random.randint(1, 100)
        similar_id = f"EXT-{base_num + offset:05d}"
        if similar_id != id:
            similar.append({
                "loss_id": similar_id,
                "similarity_score": round(random.uniform(0.60, 0.92), 2),
                "loss_amount": f"${random.randint(10000, 5000000):,}",
                "date": f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            })

    similar.sort(key=lambda x: x['similarity_score'], reverse=True)

    return {
        "similar_losses": similar[:3],
        "pattern_detected": random.choice(["Seasonal trend", "Regional cluster", "Product-specific", "No pattern"])
    }

def get_internal_loss_ai_taxonomy(id: str, description: str) -> Dict[str, Any]:
    """Mock AI taxonomy for internal losses."""
    _seed_random(id)

    taxonomies = [
        ["Operational", "Process Failure"],
        ["Technology", "System Outage"],
        ["People", "Human Error"],
        ["Fraud", "Internal"],
        ["Compliance", "Breach"],
        ["Data", "Quality Issue"]
    ]

    selected = random.choice(taxonomies)

    return {
        "ai_taxonomy": selected,
        "confidence": round(random.uniform(0.72, 0.96), 2),
        "department_impact": random.sample(["Operations", "IT", "Finance", "Risk", "Compliance"], random.randint(1, 3))
    }

def get_internal_loss_ai_root_causes(id: str, description: str) -> Dict[str, Any]:
    """Mock root cause analysis for internal losses."""
    _seed_random(id)

    root_causes = [
        {
            "category": "Process Design",
            "description": "Inadequate process controls",
            "responsibility": "Process Owner",
            "remediation_status": "In Progress"
        },
        {
            "category": "System Configuration",
            "description": "Incorrect system parameters",
            "responsibility": "IT Department",
            "remediation_status": "Completed"
        },
        {
            "category": "Training Gap",
            "description": "Insufficient staff training",
            "responsibility": "HR/Training",
            "remediation_status": "Planned"
        }
    ]

    num_causes = random.randint(1, 3)
    selected_causes = random.sample(root_causes, num_causes)

    return {
        "root_causes": selected_causes,
        "total_loss": f"${random.randint(5000, 1000000):,}",
        "recovery_amount": f"${random.randint(0, 500000):,}",
        "preventive_measures": [
            "Implement additional controls",
            "Enhance monitoring",
            "Regular audits",
            "Staff training program"
        ][:num_causes + 1]
    }

def get_internal_loss_ai_enrichment(id: str, description: str) -> Dict[str, Any]:
    """Mock enrichment for internal losses."""
    _seed_random(id)

    return {
        "entities": [
            {"type": "Business Unit", "name": random.choice(["Retail Banking", "Corporate Banking", "Trading"]), "relevance": 0.9},
            {"type": "Process", "name": random.choice(["Payment Processing", "Account Opening", "Trade Settlement"]), "relevance": 0.85},
            {"type": "System", "name": random.choice(["Core Banking", "Trading Platform", "Risk System"]), "relevance": 0.8}
        ],
        "control_gaps": [
            "Missing approval step",
            "Insufficient system validation",
            "Lack of reconciliation"
        ][:random.randint(1, 3)],
        "audit_findings": random.choice(["Critical", "High", "Medium", "Low"])
    }

def get_internal_loss_similar_internal_loss(id: str, description: str) -> Dict[str, Any]:
    """Mock similar internal losses."""
    _seed_random(id)

    base_num = int(''.join(filter(str.isdigit, id)) or '5000')
    similar = []

    for i in range(random.randint(2, 4)):
        offset = random.randint(1, 200)
        similar_id = f"INT-{base_num + offset:06d}"
        if similar_id != id:
            similar.append({
                "loss_id": similar_id,
                "similarity_score": round(random.uniform(0.65, 0.93), 2),
                "common_factors": random.sample(["Same department", "Similar process", "Same system", "Same root cause"], random.randint(1, 3))
            })

    similar.sort(key=lambda x: x['similarity_score'], reverse=True)

    return {
        "similar_losses": similar,
        "trend_analysis": random.choice(["Increasing frequency", "Decreasing severity", "Stable", "Seasonal pattern"])
    }

def get_issues_ai_taxonomy(id: str, description: str) -> Dict[str, Any]:
    """Mock AI taxonomy for issues."""
    _seed_random(id)

    taxonomies = [
        ["Risk", "Control Gap"],
        ["Compliance", "Regulatory"],
        ["Audit", "Finding"],
        ["Incident", "Operational"],
        ["Project", "Delay"],
        ["Quality", "Defect"]
    ]

    selected = random.choice(taxonomies)

    return {
        "ai_taxonomy": selected,
        "confidence": round(random.uniform(0.73, 0.97), 2),
        "priority": random.choice(["Critical", "High", "Medium", "Low"]),
        "estimated_resolution": f"{random.randint(1, 180)} days"
    }

def get_issues_ai_root_causes(id: str, description: str) -> Dict[str, Any]:
    """Mock root cause analysis for issues."""
    _seed_random(id)

    root_causes = [
        {
            "category": "Resource Constraint",
            "description": "Insufficient resources allocated",
            "impact_level": "High"
        },
        {
            "category": "Requirement Gap",
            "description": "Unclear or changing requirements",
            "impact_level": "Medium"
        },
        {
            "category": "Technical Debt",
            "description": "Legacy system limitations",
            "impact_level": "Medium"
        }
    ]

    num_causes = random.randint(1, 3)
    selected_causes = random.sample(root_causes, num_causes)

    return {
        "root_causes": selected_causes,
        "resolution_complexity": random.choice(["Simple", "Moderate", "Complex"]),
        "dependencies": [
            "System upgrade required",
            "Policy approval needed",
            "Third-party involvement"
        ][:random.randint(0, 2)],
        "action_items": [
            "Assign dedicated resources",
            "Create detailed action plan",
            "Schedule stakeholder review",
            "Implement interim controls"
        ][:num_causes + 1]
    }

def get_issues_ai_enrichment(id: str, description: str) -> Dict[str, Any]:
    """Mock enrichment for issues."""
    _seed_random(id)

    return {
        "entities": [
            {"type": "Owner", "name": random.choice(["John Smith", "Jane Doe", "Mike Johnson"]), "relevance": 0.95},
            {"type": "Department", "name": random.choice(["Risk", "Compliance", "Operations", "IT"]), "relevance": 0.9},
            {"type": "Project", "name": random.choice(["Digital Transformation", "Risk Remediation", "System Upgrade"]), "relevance": 0.8}
        ],
        "related_issues": [
            f"ISS-{random.randint(10000, 99999)}" for _ in range(random.randint(0, 3))
        ],
        "status_history": [
            {"date": "2024-01-15", "status": "Open", "comment": "Issue identified"},
            {"date": "2024-02-01", "status": "In Progress", "comment": "Team assigned"},
            {"date": "2024-03-01", "status": "Under Review", "comment": "Solution proposed"}
        ][:random.randint(1, 3)]
    }

def get_issues_similar_issues(id: str, description: str) -> Dict[str, Any]:
    """Mock similar issues."""
    _seed_random(id)

    base_num = int(''.join(filter(str.isdigit, id)) or '10000')
    similar = []

    for i in range(random.randint(3, 6)):
        offset = random.randint(1, 500)
        similar_id = f"ISS-{base_num + offset:05d}"
        if similar_id != id:
            similar.append({
                "issue_id": similar_id,
                "similarity_score": round(random.uniform(0.62, 0.94), 2),
                "status": random.choice(["Open", "In Progress", "Resolved", "Closed"]),
                "resolution_time": f"{random.randint(1, 365)} days" if random.choice([True, False]) else "Ongoing"
            })

    similar.sort(key=lambda x: x['similarity_score'], reverse=True)

    return {
        "similar_issues": similar[:5],
        "common_patterns": random.sample([
            "Same root cause",
            "Similar department",
            "Related systems",
            "Common stakeholders",
            "Recurring theme"
        ], random.randint(1, 3))
    }