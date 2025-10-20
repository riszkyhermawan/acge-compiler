from fastapi import FastAPI

app = FastAPI(title="Compiler API")


@app.get("/")
async def read_root():
    return {"message": "Bisa nih ges Compiler API nya anjayy"}