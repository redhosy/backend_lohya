from typing import List, Dict, Any
from datetime import datetime
from collections import defaultdict
from sqlalchemy.orm import Session
from app.models.riwayat_klasifikasi_model import RiwayatKlasifikasi


def ambil_trend(
    db: Session,
    user_id: int,
    start_date: str,
    end_date: str,
) -> List[Dict[str, Any]]:
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d").replace(
        hour=23, minute=59, second=59
    )

    histories = (
        db.query(RiwayatKlasifikasi)
        .filter(
            RiwayatKlasifikasi.id_user == user_id,
            RiwayatKlasifikasi.created_at >= start,
            RiwayatKlasifikasi.created_at <= end,
        )
        .all()
    )

    result = defaultdict(lambda: {"sehat": 0, "keriting": 0, "bercak": 0})

    for item in histories:
        day = item.created_at.strftime("%Y-%m-%d")
        if item.kategori == "Daun Sehat":
            result[day]["sehat"] += 1
        elif item.kategori == "Daun Keriting":
            result[day]["keriting"] += 1
        elif item.kategori == "Daun Bercak":
            result[day]["bercak"] += 1

    return [
        {"date": key, "sehat": value["sehat"], "keriting": value["keriting"], "bercak": value["bercak"]}
        for key, value in sorted(result.items())
    ]
