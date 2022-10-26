from fastapi import FastAPI


class Particle(object):
    def __init__(self, x: int = 0, y: int = 0, t: int = 0):
        self.x = x
        self.y = y
        self.t = t

    def query_rng(self):
        pass

    def step(self):
        self.x += 1

    def position(self):
        return (self.x, self.y, self.t)


app = FastAPI()
app.p = Particle()


@app.get("/pos/")
async def pos():
    """Get current particle position."""
    return app.p.position()


@app.get("/step/")
async def step():
    """Move current particle position."""
    return app.p.step()
