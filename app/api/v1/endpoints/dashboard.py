from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.api import deps
from app.schemas import dashboard as dashboard_schema
from app.services import dashboard_service as service
from app.db.session import get_db

router = APIRouter()

@router.get("/summary", response_model=dashboard_schema.SummaryMetrics)
def get_financial_summary(
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_user),
    start_date: Optional[date] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[date] = Query(None, description="End date in YYYY-MM-DD format")
):
    """Provides high-level totals (Income, Expense, Balance). Filters apply if admin/analyst."""
    user_scope = current_user.id if current_user.role == "Viewer" else None
    return service.calculate_summary_metrics(db, user_id=user_scope, start_date=start_date, end_date=end_date)

@router.get("/trends", response_model=List[dashboard_schema.MonthlyTrend])
def get_financial_trends(
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_user),
    months: int = Query(12, description="Number of past months to include in the trend line")
):
    """Provides month-over-month performance trend data."""
    user_scope = current_user.id if current_user.role == "Viewer" else None
    return service.calculate_monthly_trends(db, user_id=user_scope, months=months)

@router.get("/category-breakdown", response_model=List[dashboard_schema.CategoryBreakdown])
def get_category_breakdown(
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_user)
):
    """Provides categorical spending/revenue distribution data."""
    user_scope = current_user.id if current_user.role == "Viewer" else None
    return service.calculate_category_breakdown(db, user_id=user_scope)
