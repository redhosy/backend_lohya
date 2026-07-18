from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.chart_schema import (
    DashboardResponse,
    TrendItemRespon,
)
from app.services.charts_service import ambil_dashboard
from app.services.charts_trend_service import ambil_trend

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard_endpoint(
    user_id: int = Query(..., description="ID user"),
    db: Session = Depends(get_db),
):
    try:
        return ambil_dashboard(db, user_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal memuat data dashboard: {str(e)}",
        )


@router.get("/trend", response_model=List[TrendItemRespon])
def trend_endpoint(
    user_id: int = Query(..., description="ID user"),
    start_date: str = Query(..., description="Tanggal awal (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Tanggal akhir (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    try:
        return ambil_trend(db, user_id, start_date, end_date)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Format tanggal tidak valid. Gunakan format YYYY-MM-DD.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal memuat data trend: {str(e)}",
        )
