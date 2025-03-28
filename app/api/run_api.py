import os
import uvicorn
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def run_api():
    uvicorn.run(
        "app.api.main:app",
        host=os.environ.get("API_HOST", "0.0.0.0"),
        port=int(os.environ.get("API_PORT", 8000)),
        log_level="info",
        reload=True if os.environ.get("DEBUG", "False").lower() == "true" else False
    )

if __name__ == "__main__":
    run_api() 