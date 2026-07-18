from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def root():
    return {"message": "Pantau Cabai API berjalan."}
