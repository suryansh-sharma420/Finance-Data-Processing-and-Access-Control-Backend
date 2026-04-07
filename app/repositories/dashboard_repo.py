from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import date as dt_date
from app.db.models.record import Record

def get_global_metrics(db: Session, user_id: Optional[int] = None, start_date: Optional[dt_date] = None, end_date: Optional[dt_date] = None) -> Dict[str, float]:
    """Provides high-level totals of income, expense, and net balance."""
    q = db.query(
        func.sum(case((Record.type == "Income", Record.amount), else_=0)).label("income"),
        func.sum(case((Record.type == "Expense", Record.amount), else_=0)).label("expense")
    )
    if user_id:
        q = q.filter(Record.user_id == user_id)
    if start_date:
        q = q.filter(func.date(Record.date) >= start_date)
    if end_date:
        q = q.filter(func.date(Record.date) <= end_date)
    
    res = q.first()
    income = res.income or 0.0
    expense = res.expense or 0.0
    return {
        "income": float(income),
        "expense": float(expense),
        "balance": float(income - expense)
    }

def get_monthly_totals_by_type(db: Session, user_id: Optional[int] = None, months: int = 12) -> List[Dict[str, Any]]:
    """Calculates month-over-month performance for trend visualization."""
    month_col = func.strftime("%Y-%m", Record.date).label("month")
    q = db.query(
        month_col,
        func.sum(case((Record.type == "Income", Record.amount), else_=0)).label("income"),
        func.sum(case((Record.type == "Expense", Record.amount), else_=0)).label("expenses")
    )
    if user_id:
        q = q.filter(Record.user_id == user_id)
    
    results = q.group_by("month").order_by(month_col.desc()).limit(months).all()
    # Reverse to return older months first
    results = results[::-1]
    
    return [
        {"month": r.month, "income": float(r.income), "expenses": float(r.expenses)}
        for r in results
    ]

def get_category_aggregates(db: Session, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Groups transaction amounts by category and calculates percentage distribution."""
    # 1. Get total for percentage calculation
    total_q = db.query(func.sum(Record.amount))
    if user_id:
        total_q = total_q.filter(Record.user_id == user_id)
    total_sum = total_q.scalar() or 1.0 # 1.0 to avoid zero division if empty
    
    # 2. Get grouped results
    q = db.query(
        Record.category,
        func.sum(Record.amount).label("amount")
    )
    if user_id:
        q = q.filter(Record.user_id == user_id)
    
    results = q.group_by(Record.category).all()
    return [
        {
            "category": r.category,
            "amount": float(r.amount),
            "percentage": round(float(r.amount / total_sum * 100), 2)
        }
        for r in results
    ]
