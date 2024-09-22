from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Connect 4 API",
    description="API for the Connect 4 game...add documentation here",
    version="0.1",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Connect 4 API! For more information, visit /docs."}

app.include_router(router)

# POST /games to create a new game
# GET /games/{game_id} to get the current state of a game
# POST /games/{game_id}/move to make a move in a game