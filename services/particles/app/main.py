from fastapi import FastAPI

from particle import Particle


app = FastAPI()
app.particle = Particle()


@app.get("/pos/")
async def pos():
    """Get current particle position."""
    return app.particle.position()


@app.get("/step/")
async def step():
    """Move current particle position."""
    return app.particle.step()


@app.get("/lgc_params/")
async def lgc_params():
    return app.particle.lgc_params
