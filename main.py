from fastapi import FastAPI
from pydantic import BaseModel
import docker
import uuid
import os
from requests.exceptions import ReadTimeout, ConnectionError

app = FastAPI(title="Compiler API")
client = docker.from_env()

class Code(BaseModel):
    source_code: str
    input_data: dict 

@app.post("/run")
async def run_code(code: Code):
    user_code = code.source_code
    input_dict = code.input_data

    try:
        input_values = [str(v) for v in input_dict.values()]
        input_string = "\n".join(input_values)
    except Exception as e:
        return {"error": f"Failed to process input data: {str(e)}"}

    os.makedirs("temp", exist_ok=True)
    unique_id = uuid.uuid4().hex
    
    filename_code = f"temp/{unique_id}.py"
    filename_input = f"temp/{unique_id}.txt"


    with open(filename_code, "w") as f:
        f.write(user_code)
        
    with open(filename_input, "w") as f:
        f.write(input_string)




    try:
        container = client.containers.run(
            image="python:3.11-slim",
            command=[
                "/bin/sh", 
                "-c", 
                f"python -u /app/temp/{os.path.basename(filename_code)} < /app/temp/{os.path.basename(filename_input)}"
            ],
            volumes={
                "shared_compiler_vol": {"bind": "/app/temp", "mode": "ro"}
            },
            detach=True,
            mem_limit="128m",
            network_disabled=True,
            # remove=True
        )
        
        try:
            container.wait(timeout=5)
            output = container.logs()
            return {"output": output.decode().strip()}
        except (ReadTimeout, ConnectionError):
            try:
                container.kill()
            except:
                pass
            return {"error": "Execution timed out."}


    except docker.errors.ContainerError as e: # type: ignore
        return {"error": e.stderr.decode().strip()}

    finally:
        if container:
            try:
                container.remove(force=True)
            except:
                pass
        if os.path.exists(filename_code):
            os.remove(filename_code)
        if os.path.exists(filename_input):
            os.remove(filename_input)