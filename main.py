from fastapi import FastAPI
from pydantic import BaseModel
import docker
import uuid
import os

app = FastAPI(title="Compiler API")

client = docker.from_env()


class Code(BaseModel):
    source_code: str
    input_data: str | None = None


@app.post("/run")
async def run_code(code: Code):
    user_code = code.source_code
    user_input = code.input_data or ""

    os.makedirs("temp", exist_ok=True)
    
    unique_id = uuid.uuid4().hex
    code_filename = f"temp/{unique_id}.py"
    input_filename = f"temp/{unique_id}.txt"  
    
    with open(code_filename, "w") as f:
        f.write(user_code)
    
    with open(input_filename, "w") as f:
        f.write(user_input)

    try:
        output = client.containers.run(
            image="python:3.11-slim",
            command=[
                "/bin/sh", 
                "-c", 
                f"python -u /app/temp/{os.path.basename(code_filename)} < /app/temp/{os.path.basename(input_filename)}"
            ],
            volumes={
                "shared_compiler_vol": {"bind": "/app/temp", "mode": "ro"}
            },
            environment={
                "PROGRAM_INPUT": user_input
            },
            remove=True
        )

        return {"output": output.decode().strip()}

    except docker.errors.ContainerError as e: # type: ignore
        return {"error": e.stderr.decode().strip()}

    finally:
        if os.path.exists(code_filename):
            os.remove(code_filename)
        if os.path.exists(input_filename):
            os.remove(input_filename)