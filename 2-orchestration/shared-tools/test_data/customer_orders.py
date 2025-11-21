"""Sample customer orders for testing orchestration patterns."""

SAMPLE_ORDER_SIMPLE = """
New customer order received:

Customer: Sarah Johnson
Email: sarah.johnson@techcorp.com

Order Items:
- Laptop Computer (Model XPS-15): Quantity 2, Price $1,299 each
- Wireless Mouse: Quantity 2, Price $49 each
- USB-C Hub: Quantity 1, Price $79

Shipping Address:
123 Innovation Drive
San Francisco, CA 94105

Please process this order.
"""

SAMPLE_ORDER_LARGE = """
New customer order received:

Customer: Michael Chen
Email: michael.chen@enterprise.com

Order Items:
- Server Rack Unit (42U): Quantity 5, Price $2,499 each
- Enterprise Switch (48-port): Quantity 3, Price $3,299 each
- UPS System (10kVA): Quantity 2, Price $4,999 each
- Network Cables (Cat6, 100ft): Quantity 50, Price $29 each

Shipping Address:
DataCenter Building A
456 Technology Parkway
Austin, TX 78701

Requested delivery: Next week
Payment terms: Net 60
"""

SAMPLE_ORDER_VIP = """
New customer order received:

Customer: Jennifer Martinez
Email: jmartinez@globalcorp.com
VIP Customer ID: VIP-8291

Order Items:
- Executive Workstation Setup: Quantity 10, Price $4,500 each
- 4K Monitor (32"): Quantity 20, Price $899 each
- Standing Desk (Electric): Quantity 10, Price $1,200 each
- Ergonomic Chair (Premium): Quantity 10, Price $1,400 each

Shipping Address:
GlobalCorp Headquarters
789 Executive Boulevard
New York, NY 10001

Special Instructions:
- White glove delivery required
- Installation included
- Weekend delivery preferred
- Contact facilities manager: (212) 555-0100

Payment: Corporate account (pre-approved $150K credit line)
"""

SAMPLE_ORDER_INTERNATIONAL = """
New customer order received:

Customer: Hans Schmidt
Email: h.schmidt@eurotech.de

Order Items:
- Industrial Sensor Array: Quantity 100, Price $350 each
- Control Module: Quantity 25, Price $1,200 each
- Power Supply Units: Quantity 50, Price $180 each

Shipping Address:
EuroTech Manufacturing GmbH
Industriestraße 42
80331 München, Germany

Special Requirements:
- Export documentation required
- CE certification needed
- Customs declaration for electronics
- Incoterms: DDP (Delivered Duty Paid)
- Currency: EUR
"""
