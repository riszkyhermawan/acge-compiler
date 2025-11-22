from fastapi import FastAPI
from pydantic import BaseModel
import docker
import shlex

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
    user_input = code.input_data or None
    
    escaped_code = shlex.quote(user_code)
    
    try:
        if user_input:
            input_escaped = shlex.quote(user_input)
            run_code = f"echo {input_escaped} | python -u -c {escaped_code}"
        else:
            run_code = f"python -u -c {escaped_code}"
        output = client.containers.run(
            "python:3.11-slim", 
            ["/bin/sh", "-c", run_code],
            remove=True
        )
        return {"output": output.decode("utf-8").strip()}
    except docker.errors.ContainerError as e: # type: ignore
        return {"error": e.stderr.decode("utf-8").strip()}