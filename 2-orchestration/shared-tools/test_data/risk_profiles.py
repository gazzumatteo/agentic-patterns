"""Sample risk assessment profiles for testing parallel orchestration."""

LOW_RISK_PROFILE = """
Risk Assessment Request for Corporate Lending

Company: Established Tech Solutions Inc.
Industry: Enterprise Software (B2B SaaS)
Loan Amount: $1,500,000
Purpose: Working capital

Credit Profile:
- Credit Score: 780
- Years in Business: 12
- Annual Revenue: $15M (growing 25% YoY)
- Current Debt: $800K
- Payment History: Excellent (no late payments, no defaults)
- Profitability: EBITDA margin of 22%

Market Exposure:
- Primary Market: Enterprise resource planning software
- Geographic Focus: North America (65%), Europe (25%), Asia (10%)
- Top 3 customers represent 28% of revenue
- Industry: Stable with steady growth
- Customer base: 450+ active enterprise clients
- Customer retention: 95% annual retention rate

Regulatory Considerations:
- Incorporated in Delaware, USA
- SOC 2 Type II certified
- ISO 27001 certified
- GDPR compliant
- Financial audits up to date (Big 4 auditor)
- No regulatory violations
- No pending litigation
- Strong compliance team (5 FTE)

Requested Credit Line: $1.5M at 7.5% APR, 5-year term
"""

MEDIUM_RISK_PROFILE = """
Risk Assessment Request for Corporate Lending

Company: TechStartup Inc.
Industry: Software as a Service (SaaS)
Loan Amount: $2,500,000
Purpose: Working capital and expansion

Credit Profile:
- Credit Score: 720
- Years in Business: 5
- Annual Revenue: $8M (growing 40% YoY)
- Current Debt: $1.2M
- Payment History: Excellent (no late payments)
- Profitability: EBITDA margin of 8% (improving)

Market Exposure:
- Primary Market: Enterprise software
- Geographic Focus: North America (80%), Europe (20%)
- Top 3 customers represent 45% of revenue
- Industry: High growth but competitive
- Customer base: 120 active clients
- Customer retention: 85% annual retention rate
- Facing competition from larger players

Regulatory Considerations:
- Incorporated in Delaware, USA
- SOC 2 Type II certified
- GDPR compliant
- Financial audits up to date
- No regulatory violations or pending litigation
- Growing compliance needs

Requested Credit Line: $2.5M at 8.5% APR, 5-year term
"""

HIGH_RISK_PROFILE = """
Risk Assessment Request for Corporate Lending

Company: Rapid Growth Ventures LLC
Industry: Consumer Mobile Apps (B2C)
Loan Amount: $5,000,000
Purpose: Marketing and user acquisition

Credit Profile:
- Credit Score: 650
- Years in Business: 2
- Annual Revenue: $3M (grew from $500K last year)
- Current Debt: $2.5M (multiple tranches)
- Payment History: Two late payments in past 12 months
- Profitability: Negative EBITDA (burn rate $250K/month)
- Runway: 8 months at current burn rate

Market Exposure:
- Primary Market: Social media mobile apps
- Geographic Focus: USA only (95% of revenue)
- Top 3 customers (advertisers) represent 72% of revenue
- Industry: Extremely competitive, high volatility
- User base: Growing but engagement declining
- Market saturation risks
- Dependent on platform policies (iOS/Android)

Regulatory Considerations:
- Incorporated in Delaware, USA
- No SOC 2 certification
- COPPA compliance concerns (handles minor user data)
- Privacy policy under review
- One regulatory inquiry (state AG, ongoing)
- Pending litigation (IP dispute with competitor)
- Limited compliance infrastructure

Requested Credit Line: $5M at 12% APR, 3-year term
"""

CRITICAL_RISK_PROFILE = """
Risk Assessment Request for Corporate Lending

Company: DistressedCo Industries
Industry: Retail (brick and mortar)
Loan Amount: $10,000,000
Purpose: Debt restructuring and operational turnaround

Credit Profile:
- Credit Score: 590
- Years in Business: 8
- Annual Revenue: $12M (declining 30% YoY)
- Current Debt: $15M (including $3M past due)
- Payment History: Multiple defaults, vendor payment issues
- Profitability: Negative EBITDA, operating losses for 3 consecutive years
- Cash position: Critical (less than 30 days operating cash)

Market Exposure:
- Primary Market: Consumer electronics retail
- Geographic Focus: Regional (struggling market)
- Heavy competition from e-commerce
- Top 5 locations represent 80% of revenue
- Multiple store closures in past year
- Declining foot traffic (down 45%)
- Inventory obsolescence issues

Regulatory Considerations:
- Incorporated in Nevada
- No current compliance certifications
- Sales tax compliance issues (2 states)
- EPA violation notice (improper disposal)
- Labor law complaint pending
- Multiple vendor lawsuits filed
- Potential bankruptcy filing being considered

Requested Credit Line: $10M at 18% APR, 2-year term with personal guarantees
"""
