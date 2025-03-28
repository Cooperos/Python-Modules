import os
import shutil
from typing import Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from ..core.diploma_generator import DiplomaService
from ..models.diploma_repository import DiplomaRepository
from .auth import authenticate_user

router = APIRouter(prefix="/diploma", tags=["diploma"])

class DiplomaResponse(BaseModel):
    message: str
    links: Dict[str, str]

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
PUBLIC_DIR = os.path.join(SCRIPT_DIR, "public")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PUBLIC_DIR, exist_ok=True)

@router.get("/generate", response_model=DiplomaResponse)
async def generate_diploma(
    topicId: int = Query(..., description="ID темы"),
    userId: int = Query(..., description="ID пользователя"),
    current_user = Depends(authenticate_user)
):
    try:
        user = DiplomaRepository.get_user_by_id(userId)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с ID {userId} не найден"
            )

        topic = DiplomaRepository.get_topic_by_id(topicId)
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Тема с ID {topicId} не найдена"
            )

        logo_path = os.path.join(ASSETS_DIR, "headIco.png")
        if not os.path.exists(logo_path):
            logo_path = None
        
        diploma_service = DiplomaService(
            logo_path=logo_path,
            diploma_template=os.path.join(SCRIPT_DIR, "assets", "diploma.xlsx"),
            appendix_template=os.path.join(SCRIPT_DIR, "assets", "diploma-addition.xlsx")
        )
        
        result = diploma_service.generate_diploma_by_user_and_topic(
            user_id=userId,
            topic_id=topicId,
            output_dir=OUTPUT_DIR,
            issued_by="Welding & Sons"
        )

        filename_base = os.path.basename(result['diploma_excel']).replace('.xlsx', '')
        
        public_files = {}
        for key, filepath in result.items():
            if filepath and key.endswith('_pdf'):
                filename = os.path.basename(filepath)
                public_path = os.path.join(PUBLIC_DIR, filename)
                shutil.copy2(filepath, public_path)
                if key == 'diploma_pdf':
                    public_files['diploma'] = f"/public/{filename}"
                elif key == 'appendix_pdf':
                    public_files['appendix'] = f"/public/{filename}"
        try:
            if 'diploma_excel' in result and result['diploma_excel'] and os.path.exists(result['diploma_excel']):
                os.remove(result['diploma_excel'])
                
            if 'appendix_excel' in result and result['appendix_excel'] and os.path.exists(result['appendix_excel']):
                os.remove(result['appendix_excel'])
        except Exception as e:
            print(f"Ошибка при удалении Excel файлов: {e}")
        return DiplomaResponse(
            message=f"Диплом успешно сгенерирован для {user['full_name']} по теме '{topic['title']}'",
            links=public_files
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Произошла ошибка при генерации диплома: {str(e)}"
        ) 
    