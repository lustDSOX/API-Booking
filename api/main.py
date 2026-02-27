from fastapi import FastAPI

from api.routers import events, tickets, users

app = FastAPI(
    title="Booking concert API",
    description="API for sale tickets on events",
    version="0.1.0"
)

app.include_router(events.router)
app.include_router(users.router)
app.include_router(tickets.router)

@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug", reload=True)