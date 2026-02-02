from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import scenarios, sensitivity, shocks

app = FastAPI(
    title="pyvensim API",
    description="REST API for the pyvensim system dynamics simulation library",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scenarios.router, prefix="/scenarios", tags=["scenarios"])
app.include_router(
    sensitivity.router, prefix="/scenarios", tags=["sensitivity"]
)
app.include_router(shocks.router, prefix="/scenarios", tags=["shocks"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
