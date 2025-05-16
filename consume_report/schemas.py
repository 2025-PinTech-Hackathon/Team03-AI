from pydantic import BaseModel
from typing import List
from datetime import datetime

class Transaction(BaseModel):
    merchant_name: str
    amount: int
    timestamp: datetime

class SpendingRequest(BaseModel):
    userId: int
    role: str
    transactions: List[Transaction]

class ReviewResponse(BaseModel):
    summary: str

class MonthlyReportResponse(BaseModel):
    summary: str
    shopping: int
    food: int
    culture: int
    etc: int

