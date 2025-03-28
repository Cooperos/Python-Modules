import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .diploma import router as diploma_router

app = FastAPI(
    title="Генератор дипломов API",
    description="API для генерации дипломов и приложений к ним",
    version="1.0.0"
)

app.include_router(diploma_router)

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PUBLIC_DIR = os.path.join(SCRIPT_DIR, "public")

os.makedirs(PUBLIC_DIR, exist_ok=True)

app.mount("/public", StaticFiles(directory=PUBLIC_DIR), name="public")

@app.get("/")
async def root():
    return {
        "application": "Генератор дипломов API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "diploma_generate": "/diploma/generate?topicId=1&userId=1",
            "public_files": "/public/{filename}"
        }
    }

@app.get("/public/{filename}")
async def get_file(filename: str):
    file_path = os.path.join(PUBLIC_DIR, filename)
    
    if os.path.exists(file_path):
        return FileResponse(file_path)
    
    return {"error": "Файл не найден"} 
