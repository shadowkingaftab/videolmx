from fastapi import FastAPI

app = FastAPI(title="VideoLMX")

@app.get("/health")
def health_check():
    return {"status": "ok"}
