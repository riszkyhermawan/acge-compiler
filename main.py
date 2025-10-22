from fastapi import FastAPI
from pydantic import BaseModel
import docker

app = FastAPI(title="Compiler API")


client = docker.from_env()

@app.get("/")
async def read_root():
    return {"message": "Bisa nih ges Compiler API nya anjayy"}


class Code(BaseModel):
    source_code: str
    input_data: str | None = None
    
    
@app.post("/run")
async def run_code(code: Code):
    user_code = code.source_code
    user_input = code.input_data or ""
    
    try:
        if user_input == None:
            run_code = f"echo \"{user_input}\" | python -c \"{user_code}\""
        else:
            run_code = f"python -c \"{user_code}\""
        output = client.containers.run("python", run_code)
        return {"output": output.decode("utf-8").strip()}
    except docker.errors.ContainerError as e: # type: ignore
        return {"error": e.stderr.decode("utf-8").strip()}