"""
Risk Assessment Utilities

Common risk calculation functions used across financial risk assessment patterns.

Reference: Pattern #2 - Parallel Orchestration (Risk Assessment)
"""

from typing import Dict, Any, List, Literal
from dataclasses import dataclass
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskScore:
    """Standardized risk score structure."""

    risk_type: str
    score: float  # 0-100, higher = more risk
    level: RiskLevel
    factors: List[str]
    recommendation: Literal["approve", "conditional", "reject"]
    details: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "risk_type": self.risk_type,
            "score": self.score,
            "level": self.level.value,
            "factors": self.factors,
            "recommendation": self.recommendation,
            "details": self.details,
        }


def calculate_credit_risk(
    credit_rating: int,
    payment_history: str,
    debt_ratio: float,
    years_in_business: int = 5,
    revenue_growth: float = 0.0
) -> RiskScore:
    """
    Calculate credit risk score.

    Args:
        credit_rating: Credit score (300-850)
        payment_history: "excellent", "good", "fair", "poor"
        debt_ratio: Debt-to-income ratio (0.0-1.0+)
        years_in_business: Years of operation
        revenue_growth: YoY revenue growth rate (-1.0 to +1.0+)

    Returns:
        RiskScore with credit risk assessment
    """
    score = 0.0
    factors = []

    # Credit rating impact (0-40 points)
    if credit_rating < 600:
        score += 40
        factors.append("Low credit score (<600)")
    elif credit_rating < 700:
        score += 20
        factors.append("Below-average credit score")
    elif credit_rating >= 750:
        score -= 10
        factors.append("Excellent credit score")

    # Payment history impact (0-30 points)
    payment_scores = {
        "excellent": -10,
        "good": 5,
        "fair": 15,
        "poor": 30
    }
    score += payment_scores.get(payment_history.lower(), 15)
    if payment_history.lower() in ["fair", "poor"]:
        factors.append(f"Payment history: {payment_history}")

    # Debt ratio impact (0-30 points)
    if debt_ratio > 0.4:
        score += 30
        factors.append(f"High debt ratio ({debt_ratio:.1%})")
    elif debt_ratio > 0.25:
        score += 15
        factors.append(f"Elevated debt ratio ({debt_ratio:.1%})")

    # Business longevity (0-10 points bonus)
    if years_in_business < 2:
        score += 10
        factors.append("Limited operating history")
    elif years_in_business >= 10:
        score -= 5

    # Revenue growth bonus
    if revenue_growth > 0.3:
        score -= 10
        factors.append(f"Strong revenue growth ({revenue_growth:.0%})")
    elif revenue_growth < -0.1:
        score += 15
        factors.append("Declining revenue")

    # Normalize score
    score = max(0, min(100, score + 25))  # Base score of 25

    # Determine level and recommendation
    if score < 30:
        level = RiskLevel.LOW
        recommendation = "approve"
        details = "Strong credit profile with minimal risk indicators."
    elif score < 60:
        level = RiskLevel.MEDIUM
        recommendation = "conditional"
        details = "Moderate credit risk. Recommend enhanced monitoring and covenants."
    else:
        level = RiskLevel.HIGH
        recommendation = "reject"
        details = "High credit risk. Significant concerns about repayment ability."

    return RiskScore(
        risk_type="credit_risk",
        score=score,
        level=level,
        factors=factors if factors else ["No significant risk factors"],
        recommendation=recommendation,
        details=details
    )


def calculate_market_risk(
    customer_concentration: float,
    industry_volatility: str,
    geographic_concentration: float,
    market_position: str = "established"
) -> RiskScore:
    """
    Calculate market risk score.

    Args:
        customer_concentration: % of revenue from top 3 customers (0.0-1.0)
        industry_volatility: "low", "medium", "high"
        geographic_concentration: % of revenue from primary region (0.0-1.0)
        market_position: "startup", "growth", "established", "mature"

    Returns:
        RiskScore with market risk assessment
    """
    score = 0.0
    factors = []

    # Customer concentration (0-40 points)
    if customer_concentration > 0.5:
        score += 40
        factors.append(f"High customer concentration ({customer_concentration:.0%})")
    elif customer_concentration > 0.3:
        score += 25
        factors.append(f"Moderate customer concentration ({customer_concentration:.0%})")

    # Industry volatility (0-30 points)
    volatility_scores = {
        "low": 5,
        "medium": 20,
        "high": 30
    }
    score += volatility_scores.get(industry_volatility.lower(), 20)
    if industry_volatility.lower() == "high":
        factors.append("High industry volatility")

    # Geographic concentration (0-20 points)
    if geographic_concentration > 0.8:
        score += 20
        factors.append(f"Geographic concentration ({geographic_concentration:.0%})")
    elif geographic_concentration > 0.6:
        score += 10

    # Market position (0-10 points)
    position_scores = {
        "startup": 10,
        "growth": 5,
        "established": 0,
        "mature": -5
    }
    score += position_scores.get(market_position.lower(), 0)
    if market_position.lower() == "startup":
        factors.append("Early-stage company")

    # Normalize
    score = max(0, min(100, score + 10))  # Base score of 10

    # Determine level
    if score < 35:
        level = RiskLevel.LOW
        recommendation = "approve"
        details = "Well-diversified market exposure with manageable risks."
    elif score < 65:
        level = RiskLevel.MEDIUM
        recommendation = "conditional"
        details = "Moderate market risk. Recommend diversification covenants."
    else:
        level = RiskLevel.HIGH
        recommendation = "reject"
        details = "High market concentration risk. Significant exposure to market changes."

    return RiskScore(
        risk_type="market_risk",
        score=score,
        level=level,
        factors=factors if factors else ["No significant market risks"],
        recommendation=recommendation,
        details=details
    )


def calculate_regulatory_risk(
    compliance_status: str,
    certifications: List[str],
    violations_history: int = 0,
    pending_litigation: bool = False,
    industry_regulation: str = "moderate"
) -> RiskScore:
    """
    Calculate regulatory compliance risk.

    Args:
        compliance_status: "excellent", "good", "fair", "poor"
        certifications: List of compliance certifications (SOC2, GDPR, etc.)
        violations_history: Number of past violations
        pending_litigation: Whether there is pending litigation
        industry_regulation: "low", "moderate", "high", "critical"

    Returns:
        RiskScore with regulatory risk assessment
    """
    score = 0.0
    factors = []

    # Compliance status (0-40 points)
    compliance_scores = {
        "excellent": 0,
        "good": 10,
        "fair": 25,
        "poor": 40
    }
    score += compliance_scores.get(compliance_status.lower(), 25)
    if compliance_status.lower() in ["fair", "poor"]:
        factors.append(f"Compliance status: {compliance_status}")

    # Certifications bonus (up to -20 points)
    cert_bonus = min(20, len(certifications) * 7)
    score -= cert_bonus
    if len(certifications) >= 2:
        factors.append(f"Strong certifications ({', '.join(certifications[:3])})")

    # Violations history (0-30 points)
    if violations_history > 0:
        score += min(30, violations_history * 15)
        factors.append(f"{violations_history} past violation(s)")

    # Pending litigation (0-20 points)
    if pending_litigation:
        score += 20
        factors.append("Pending regulatory litigation")

    # Industry regulation level
    regulation_scores = {
        "low": -5,
        "moderate": 0,
        "high": 10,
        "critical": 20
    }
    score += regulation_scores.get(industry_regulation.lower(), 0)
    if industry_regulation.lower() in ["high", "critical"]:
        factors.append(f"Highly regulated industry ({industry_regulation})")

    # Normalize
    score = max(0, min(100, score + 15))  # Base score of 15

    # Determine level
    if score < 25:
        level = RiskLevel.LOW
        recommendation = "approve"
        details = "Strong compliance posture with minimal regulatory concerns."
    elif score < 50:
        level = RiskLevel.MEDIUM
        recommendation = "conditional"
        details = "Some regulatory considerations. Recommend ongoing compliance monitoring."
    else:
        level = RiskLevel.HIGH
        recommendation = "reject"
        details = "Significant regulatory risks. Compliance concerns require resolution."

    return RiskScore(
        risk_type="regulatory_risk",
        score=score,
        level=level,
        factors=factors if factors else ["Strong regulatory compliance"],
        recommendation=recommendation,
        details=details
    )


def aggregate_risk_scores(
    risk_scores: List[RiskScore],
    weights: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Aggregate multiple risk scores into overall assessment.

    Args:
        risk_scores: List of individual risk scores
        weights: Optional weights for each risk type (default: equal weighting)

    Returns:
        Aggregated risk assessment with overall score and recommendation
    """
    if not risk_scores:
        raise ValueError("At least one risk score required")

    # Default equal weights
    if weights is None:
        weights = {rs.risk_type: 1.0 / len(risk_scores) for rs in risk_scores}

    # Calculate weighted average score
    total_score = sum(rs.score * weights.get(rs.risk_type, 0) for rs in risk_scores)

    # Determine overall recommendation (most conservative)
    recommendations = [rs.recommendation for rs in risk_scores]
    if "reject" in recommendations:
        overall_recommendation = "reject"
    elif "conditional" in recommendations:
        overall_recommendation = "conditional"
    else:
        overall_recommendation = "approve"

    # Determine overall level
    if total_score < 30:
        overall_level = RiskLevel.LOW
    elif total_score < 60:
        overall_level = RiskLevel.MEDIUM
    else:
        overall_level = RiskLevel.HIGH

    # Collect all factors
    all_factors = []
    for rs in risk_scores:
        all_factors.extend(rs.factors)

    return {
        "overall_score": round(total_score, 1),
        "overall_level": overall_level.value,
        "overall_recommendation": overall_recommendation,
        "risk_breakdown": {rs.risk_type: rs.to_dict() for rs in risk_scores},
        "key_factors": all_factors,
        "weights_used": weights,
    }
