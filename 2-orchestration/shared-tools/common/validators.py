"""
Pydantic Validators and Schemas

Common data validation schemas used across orchestration patterns.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime


class OrderItem(BaseModel):
    """Individual order item."""
    product: str = Field(..., min_length=1, description="Product name")
    quantity: int = Field(..., gt=0, description="Quantity ordered")
    unit_price: float = Field(..., gt=0, description="Price per unit")

    @property
    def total(self) -> float:
        """Calculate total for this item."""
        return self.quantity * self.unit_price


class OrderSchema(BaseModel):
    """Customer order validation schema."""
    customer_name: str = Field(..., min_length=1)
    customer_email: EmailStr
    order_items: List[OrderItem] = Field(..., min_items=1)
    shipping_address: str = Field(..., min_length=5)
    total_amount: Optional[float] = None

    @validator('total_amount', always=True)
    def calculate_total(cls, v, values):
        """Auto-calculate total if not provided."""
        if v is None and 'order_items' in values:
            return sum(item.total for item in values['order_items'])
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "customer_name": "Sarah Johnson",
                "customer_email": "sarah@example.com",
                "order_items": [
                    {"product": "Laptop", "quantity": 1, "unit_price": 1299.00}
                ],
                "shipping_address": "123 Main St, San Francisco, CA 94105",
                "total_amount": 1299.00
            }
        }


class RiskAssessmentSchema(BaseModel):
    """Risk assessment result schema."""
    risk_type: str = Field(..., description="Type of risk assessed")
    risk_score: float = Field(..., ge=0, le=100, description="Risk score 0-100")
    risk_level: Literal["low", "medium", "high", "critical"]
    key_factors: List[str] = Field(default_factory=list)
    recommendation: Literal["approve", "conditional", "reject"]
    details: str = Field(..., min_length=10)

    class Config:
        json_schema_extra = {
            "example": {
                "risk_type": "credit_risk",
                "risk_score": 25.0,
                "risk_level": "low",
                "key_factors": ["Excellent credit score", "Strong payment history"],
                "recommendation": "approve",
                "details": "Customer demonstrates strong creditworthiness."
            }
        }


class InvoiceSchema(BaseModel):
    """Invoice document schema."""
    invoice_number: str = Field(..., pattern=r"^INV-\d{8}-\d{4}$")
    invoice_date: datetime = Field(default_factory=datetime.now)
    customer_name: str
    customer_email: EmailStr
    items: List[OrderItem]
    subtotal: float = Field(..., gt=0)
    tax_rate: float = Field(default=0.08, ge=0, le=1)
    tax_amount: float = Field(..., ge=0)
    shipping: float = Field(default=15.00, ge=0)
    total: float = Field(..., gt=0)
    payment_terms: str = Field(default="Net 30")
    status: Literal["draft", "sent", "paid", "overdue"] = Field(default="draft")

    @validator('tax_amount', always=True)
    def calculate_tax(cls, v, values):
        """Calculate tax amount."""
        if 'subtotal' in values and 'tax_rate' in values:
            return round(values['subtotal'] * values['tax_rate'], 2)
        return v

    @validator('total', always=True)
    def calculate_total(cls, v, values):
        """Calculate total amount."""
        subtotal = values.get('subtotal', 0)
        tax = values.get('tax_amount', 0)
        shipping = values.get('shipping', 0)
        return round(subtotal + tax + shipping, 2)


class SupportTicketSchema(BaseModel):
    """Support ticket schema."""
    ticket_id: str = Field(..., pattern=r"^TKT-\d{6}$")
    created_at: datetime = Field(default_factory=datetime.now)
    customer_name: str
    customer_email: EmailStr
    subject: str = Field(..., min_length=5)
    description: str = Field(..., min_length=20)
    priority: Literal["low", "medium", "high", "urgent"] = Field(default="medium")
    category: Optional[Literal["financial", "legal", "technical", "general"]] = None
    status: Literal["new", "assigned", "in_progress", "resolved", "closed"] = Field(default="new")
    assigned_to: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "ticket_id": "TKT-000123",
                "customer_name": "John Doe",
                "customer_email": "john@example.com",
                "subject": "Refund request for order #12345",
                "description": "I would like to request a refund for my recent purchase...",
                "priority": "high",
                "category": "financial",
                "status": "new"
            }
        }


class CreditValidationResult(BaseModel):
    """Credit validation result."""
    validation_status: Literal["approved", "rejected", "review_required"]
    credit_limit: float = Field(..., ge=0)
    risk_score: float = Field(..., ge=0, le=100)
    flags: List[str] = Field(default_factory=list)
    recommendation: str = Field(..., min_length=10)


class ContextTransferPackage(BaseModel):
    """Package for transferring context between agents."""
    source_agent: str
    target_agent: str
    conversation_history: List[str]
    customer_data: dict
    issue_summary: str
    previous_attempts: List[str] = Field(default_factory=list)
    priority: Literal["low", "medium", "high", "urgent"]
    metadata: dict = Field(default_factory=dict)
