from pydantic import BaseModel
from typing import Optional
from datetime import date


class InvoiceSchema(BaseModel):
    """
    Schema representing structured invoice data extracted from documents
    """

    invoice_number: Optional[str]
    vendor_name: Optional[str]
    buyer_name: Optional[str]
    invoice_date: Optional[date]
    total_amount: Optional[float]
    tax_amount: Optional[float]
    currency: Optional[str]