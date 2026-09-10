from fastapi import FastAPI

from backend.api.routes import router


app = FastAPI(title="NeuroDivSim API")


app.include_router(router)


@app.get("/")
def read_root():

    return {
        "message": "NeuroDivSim API is running"
    }
