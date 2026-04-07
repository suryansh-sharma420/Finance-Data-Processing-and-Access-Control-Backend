from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, date
from app.repositories import dashboard_repo as repo
from app.schemas.dashboard import SummaryMetrics, MonthlyTrend, CategoryBreakdown

def calculate_summary_metrics(db: Session, user_id: Optional[int] = None, start_date: Optional[date] = None, end_date: Optional[date] = None) -> SummaryMetrics:
    """Orchestrates high-level summary retrieval."""
    metrics_data = repo.get_global_metrics(db, user_id=user_id, start_date=start_date, end_date=end_date)
    return SummaryMetrics(
        total_income=metrics_data["income"],
        total_expenses=metrics_data["expense"],
        net_balance=metrics_data["balance"]
    )

from app.repositories import record_repo

def calculate_monthly_trends(db: Session, user_id: Optional[int] = None, months: int = 12) -> List[MonthlyTrend]:
    """Retrieves month-by-month financial performance trends and applies advanced metrics."""
    # Using the new record_repo group by function as requested
    results = record_repo.get_monthly_totals_by_user(db, user_id=user_id)
    
    # Sort chronologically just to be sure (YYYY-MM string sorting matches chronological)
    results = sorted(results, key=lambda x: x["month"])
    
    # If a limit was provided, we'll slice the end chronologically
    # (Since we just sorted ascending, getting the last N items gives the most recent history in order)
    if months:
        results = results[-months:]
        
    enhanced_results = []
    prev_income = None
    prev_expense = None
    
    for r in results:
        income = float(r["income"])
        expenses = float(r["expenses"])
        
        # 1. Net Balance & Savings Rate
        net_balance = income - expenses
        savings_rate_pct = (net_balance / income * 100) if income > 0 else 0.0
        
        # 2. MoM Growth Rates
        mom_income_growth_pct = 0.0
        mom_expense_growth_pct = 0.0
        
        if prev_income is not None and prev_income > 0:
            mom_income_growth_pct = ((income - prev_income) / prev_income) * 100
            
        if prev_expense is not None and prev_expense > 0:
            mom_expense_growth_pct = ((expenses - prev_expense) / prev_expense) * 100
            
        enhanced_results.append(MonthlyTrend(
            month=r["month"],
            income=income,
            expenses=expenses,
            net_balance=round(net_balance, 2),
            savings_rate_pct=round(savings_rate_pct, 2),
            mom_income_growth_pct=round(mom_income_growth_pct, 2),
            mom_expense_growth_pct=round(mom_expense_growth_pct, 2)
        ))
        
        prev_income = income
        prev_expense = expenses
        
    return enhanced_results

def calculate_category_breakdown(db: Session, user_id: Optional[int] = None) -> List[CategoryBreakdown]:
    """Retrieves categorical spending/income distribution."""
    aggregates = repo.get_category_aggregates(db, user_id=user_id)
    return [CategoryBreakdown(**item) for item in aggregates]
