import os
import subprocess
import logging
import platform
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PDFService')

class PDFService:   
    def __init__(self, timeout=30):
        self.timeout = timeout
        self.system = platform.system()
        self.libreoffice_available = self._check_command("libreoffice", "--version")
        logger.info("Окружение: %s", self.system)
        logger.info("LibreOffice доступен: %s", self.libreoffice_available)
    
    def _check_command(self, command, arg):
        try:
            result = subprocess.run(
                [command, arg], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                timeout=5,
                check=False
            )
            return result.returncode == 0
        except:
            return False
            
    def _run_command_with_retry(self, cmd, max_retries=3, retry_delay=2):
        attempts = 0
        while attempts < max_retries:
            attempts += 1
            try:
                logger.info("Выполнение команды (попытка %d/%d): %s", attempts, max_retries, " ".join(cmd))
                process = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=self.timeout,
                    check=False
                )
                
                stdout = process.stdout.decode('utf-8', errors='replace').strip()
                stderr = process.stderr.decode('utf-8', errors='replace').strip()
                
                if process.returncode == 0:
                    logger.info("Команда успешно выполнена")
                    return True, stdout, stderr
                
                logger.warning(
                    "Ошибка выполнения команды (код: %d): %s", 
                    process.returncode, 
                    stderr
                )
                
                if attempts >= max_retries:
                    return False, stdout, stderr
                
                logger.info("Ожидание %d секунд перед повторной попыткой...", retry_delay)
                time.sleep(retry_delay)
                
            except subprocess.TimeoutExpired:
                logger.error("Превышено время ожидания (%d сек) для команды", self.timeout)
                if attempts >= max_retries:
                    return False, "", f"Превышено время ожидания ({self.timeout} сек)"
                logger.info("Ожидание %d секунд перед повторной попыткой...", retry_delay)
                time.sleep(retry_delay)
                
            except Exception as e:
                logger.error("Неожиданная ошибка при выполнении команды: %s", str(e))
                if attempts >= max_retries:
                    return False, "", str(e)
                logger.info("Ожидание %d секунд перед повторной попыткой...", retry_delay)
                time.sleep(retry_delay)
        
        return False, "", "Превышено максимальное количество попыток"
    
    def convert_to_pdf(self, excel_path):
        if not os.path.exists(excel_path):
            logger.error("Excel файл не найден: %s", excel_path)
            return None
        
        pdf_path = os.path.splitext(excel_path)[0] + ".pdf"
        
        if self.libreoffice_available:
            result = self._convert_with_libreoffice(excel_path, pdf_path)
            if result:
                logger.info("Файл успешно конвертирован в PDF: %s", pdf_path)
                return pdf_path
        else:
            logger.error("LibreOffice недоступен для конвертации")
        
        logger.error("Не удалось конвертировать файл в PDF: %s", excel_path)
        return None
    
    def _convert_with_libreoffice(self, excel_path, pdf_path):
        logger.info("Попытка конвертации с помощью LibreOffice: %s", excel_path)
        
        output_dir = os.path.dirname(pdf_path)
        if not output_dir:
            output_dir = "."
            
        os.makedirs(output_dir, exist_ok=True)
        
        cmd = [
            "libreoffice", 
            "--headless", 
            "--convert-to", 
            "pdf", 
            "--outdir", 
            output_dir, 
            excel_path
        ]
        
        success, stdout, stderr = self._run_command_with_retry(cmd)
        if success:
            pdf_name = os.path.basename(os.path.splitext(excel_path)[0] + ".pdf")
            generated_pdf_path = os.path.join(output_dir, pdf_name)
            
            if os.path.exists(generated_pdf_path):
                logger.info("PDF создан с помощью LibreOffice: %s", generated_pdf_path)
                
                if generated_pdf_path != pdf_path:
                    try:
                        os.rename(generated_pdf_path, pdf_path)
                        logger.info("PDF переименован в %s", pdf_path)
                    except Exception as e:
                        logger.error("Ошибка при переименовании PDF: %s", str(e))
                        return False
                
                return True
            logger.warning("LibreOffice завершен успешно, но PDF файл не создан")
        else:
            logger.error("Ошибка при конвертации с помощью LibreOffice: %s", stderr)
        
        return False 
    