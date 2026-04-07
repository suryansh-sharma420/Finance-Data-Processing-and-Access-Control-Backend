from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class SummaryMetrics(BaseModel):
    """Overall financial summary including income, expense, and net balance."""
    total_income: float
    total_expenses: float
    net_balance: float

class CategoryBreakdown(BaseModel):
    """Spending or revenue distribution by category."""
    category: str
    amount: float
    percentage: float

class MonthlyTrend(BaseModel):
    """Monthly financial performance comparisons."""
    month: str
    income: float
    expenses: float
    net_balance: Optional[float] = None
    savings_rate_pct: Optional[float] = None
    mom_income_growth_pct: Optional[float] = None
    mom_expense_growth_pct: Optional[float] = None

class DashboardAnalytics(BaseModel):
    """Consolidated dashboard information for the frontend."""
    metrics: SummaryMetrics
    trends: List[MonthlyTrend]
    breakdown: List[CategoryBreakdown]
