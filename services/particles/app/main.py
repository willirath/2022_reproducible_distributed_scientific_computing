from fastapi import FastAPI, BackgroundTasks

from particle import Particle


app = FastAPI()
app.particle = Particle()


@app.get("/pos/")
async def pos():
    """Get current particle position."""
    return app.particle.position()


@app.post("/step/")
async def step(background_tasks: BackgroundTasks):
    """Move current particle position."""
    background_tasks.add_task(app.particle.step)
    return {"message": "stepping"}
