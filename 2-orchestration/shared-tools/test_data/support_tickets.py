"""Sample support tickets for testing supervisor and handoff patterns."""

FINANCIAL_TICKET = """
Support Ticket: TKT-000123

From: john.doe@example.com
Customer: John Doe
Account: Standard
Created: 2025-11-18 09:15 AM

Subject: Refund Request for Order #45829

Message:
Hi,

I placed an order last week (Order #45829) for $1,247.50, but I received the wrong
items. The package contained 3 wireless keyboards instead of the laptop I ordered.

I've already initiated a return through your portal, and the items were picked up
yesterday. I would like to request a full refund to my original payment method
(Visa ending in 4532).

Can you please process this refund as soon as possible? I need to reorder the
correct item urgently.

Thank you,
John Doe
"""

LEGAL_TICKET = """
Support Ticket: TKT-000124

From: compliance@medtech.com
Customer: Sarah Martinez (Compliance Officer)
Account: Enterprise
Created: 2025-11-18 10:30 AM

Subject: HIPAA Compliance Documentation Request - URGENT

Message:
Hello,

We are a healthcare provider currently undergoing a HIPAA compliance audit. Our
auditors have requested documentation regarding data processing agreements and
security measures for all third-party vendors.

We need the following documents within 48 hours:
1. Current Business Associate Agreement (BAA)
2. SOC 2 Type II audit report
3. Data encryption specifications
4. Incident response procedures
5. Data retention and deletion policies

This is time-sensitive as our audit is scheduled for this Friday. Please escalate
to your legal and compliance team immediately.

Our auditor's contact: jane.smith@healthauditors.com

Best regards,
Sarah Martinez, CISA, CISM
Compliance Officer, MedTech Solutions
"""

TECHNICAL_TICKET = """
Support Ticket: TKT-000125

From: devops@startup.io
Customer: Mike Chen (DevOps Engineer)
Account: Premium
Created: 2025-11-18 11:45 AM

Subject: API Gateway Returning 503 Errors - Production Down

Message:
URGENT - PRODUCTION ISSUE

Our production API gateway started returning 503 errors approximately 30 minutes
ago. This is affecting all our customers.

Error details:
- Endpoint: https://api.startup.io/v2/*
- Status: 503 Service Unavailable
- Error rate: 85% of requests
- Started: 11:15 AM PST
- Impact: ~5,000 active users affected

What we've tried:
1. Restarted API gateway instances - no change
2. Checked database connections - all healthy
3. Reviewed CloudWatch logs - showing timeout errors
4. Increased instance count - errors persist

Our monitoring shows your CDN edge nodes are timing out. Can you please:
1. Check if there's an ongoing incident on your end
2. Review our account's rate limiting configuration
3. Provide ETA for resolution

This is costing us $500/minute in lost revenue. We need immediate assistance.

Mike Chen
DevOps Lead, Startup.io
Phone: (415) 555-0199
"""

VIP_TICKET = """
Support Ticket: TKT-000126

From: cto@fortune500.com
Customer: Jennifer Liu (CTO)
Account: Enterprise VIP (Platinum)
Created: 2025-11-18 02:00 PM

Subject: Urgent: Security Breach Investigation Required

Message:
CONFIDENTIAL - SECURITY INCIDENT

We have detected suspicious activity in our account and require immediate
escalation to your security incident response team.

Incident Summary:
- Unusual API calls from unknown IP addresses
- Attempted access to sensitive customer data repositories
- Occurred: November 18, 2025, between 12:00 AM - 3:00 AM PST
- Potentially affected records: Unknown (requires investigation)

Immediate Actions Requested:
1. Suspend all API access from IP ranges outside our approved list
2. Full audit log export for the past 72 hours
3. Engagement of your security incident response team
4. Joint investigation call within 2 hours

Our legal team requires:
- Incident timeline
- Breach assessment
- Potential data exposure analysis
- Regulatory notification recommendations (GDPR, CCPA)

DO NOT share details via email. Please call my direct line immediately:
Jennifer Liu, CTO
Direct: (212) 555-0147
Mobile: (212) 555-0148

Account Manager CC'd: robert.taylor@yourcompany.com

This is our highest priority. Our legal counsel is standing by.

Jennifer Liu
Chief Technology Officer
Fortune 500 Corp
"""

GENERAL_TICKET = """
Support Ticket: TKT-000127

From: info@smallbiz.com
Customer: Tom Wilson
Account: Standard
Created: 2025-11-18 03:30 PM

Subject: Question about pricing plans

Message:
Hi there,

I'm currently on the Basic plan ($49/month) and I'm considering upgrading.
Can you help me understand the differences between your Professional and
Enterprise plans?

Specifically:
- What's the user limit on each plan?
- Do you offer annual billing discounts?
- Can I try the Professional plan for a month before committing?
- Is there a migration path if we outgrow Professional?

Also, I noticed your website mentions "custom integrations" on the Enterprise
plan. What does that include?

Not urgent - just planning for next quarter's budget.

Thanks,
Tom Wilson
Small Business Owner
"""
