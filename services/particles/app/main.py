from fastapi import FastAPI

import requests


class Particle(object):
    def __init__(self, x: int = 0, y: int = 0, t: int = 0):
        self.x = x
        self.y = y
        self.t = t
        self.lgc_params = requests.get("http://rng/lgc_params/").json()

    def query_rng(self, x: int = None):
        resp = requests.get("http://rng/lgc/", params={"x": x})
        return int(resp.json())

    def step(self):
        self.x += self.query_rng(self.x)
        self.y += self.query_rng(self.x)
        self.t += 1

    def position(self):
        return (self.x, self.y, self.t)


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
