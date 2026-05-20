from fastapi import FastAPI
from api.routes import router as api_router

app = FastAPI(
    title="Real Estate Lead Qualification API",
    description="AI-powered lead qualification using Gemini and WhatsApp",
    version="1.0.0"
)

app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "Real Estate AI MVP is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
