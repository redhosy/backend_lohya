from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from app.models.riwayat_klasifikasi_model import RiwayatKlasifikasi


def _hybrid_round(values: List[Tuple[str, float]], total: int) -> Dict[str, float]:
    """
    Largest Remainder Method:
    1. Floor semua nilai
    2. Hitung sisa (100 - total floored)
    3. Tambahkan 1 ke N nilai dengan desimal terbesar
    """
    if total == 0:
        return {name: 0.0 for name, _ in values}

    # Hitung raw percentage
    raw = [(name, (count / total) * 100) for name, count in values]

    # Floor semua nilai
    floored = [(name, int(pct)) for name, pct in raw]

    # Hitung sisa
    total_floored = sum(pct for _, pct in floored)
    remainder = 100 - total_floored

    # Sort berdasarkan fractional part (descending)
    with_frac = [(name, pct, raw_pct - pct) for (name, pct), (_, raw_pct) in zip(floored, raw)]
    with_frac.sort(key=lambda x: x[2], reverse=True)

    # Distribusikan sisa ke N nilai dengan desimal terbesar
    result = {}
    for i, (name, pct, _) in enumerate(with_frac):
        if i < remainder:
            result[name] = float(pct + 1)
        else:
            result[name] = float(pct)

    return result


def ambil_dashboard(db: Session, user_id: int) -> Dict[str, Any]:
    histories = (
        db.query(RiwayatKlasifikasi)
        .filter(RiwayatKlasifikasi.id_user == user_id)
        .all()
    )

    total = len(histories)
    sehat = sum(1 for h in histories if h.kategori == "Daun Sehat")
    bercak = sum(1 for h in histories if h.kategori == "Daun Bercak")
    keriting = sum(1 for h in histories if h.kategori == "Daun Keriting")
    terinfeksi = bercak + keriting

    if total == 0:
        return {
            "simpulan": {
                "daun_sehat": 0,
                "daun_terinfeksi": 0,
                "total_deteksi": 0,
            },
            "pie_chart": {
                "sehat": 0.0,
                "bercak": 0.0,
                "keriting": 0.0,
            },
        }

    # Hitung pie chart dengan hybrid rounding
    pie_values = [
        ("sehat", sehat),
        ("bercak", bercak),
        ("keriting", keriting),
    ]
    pie_chart = _hybrid_round(pie_values, total)

    return {
        "simpulan": {
            "daun_sehat": sehat,
            "daun_terinfeksi": terinfeksi,
            "total_deteksi": total,
        },
        "pie_chart": pie_chart,
    }
