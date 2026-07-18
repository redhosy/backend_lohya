from pydantic import BaseModel

class KesimpulanChartRespon(BaseModel):
    daun_sehat: int
    daun_terinfeksi: int
    total_deteksi: int

class PieChartRespon(BaseModel):
    sehat: float
    bercak: float
    keriting: float

class DashboardResponse(BaseModel):
    simpulan: KesimpulanChartRespon
    pie_chart: PieChartRespon

class TrendItemRespon(BaseModel):
    date: str
    sehat: int
    keriting: int
    bercak: int