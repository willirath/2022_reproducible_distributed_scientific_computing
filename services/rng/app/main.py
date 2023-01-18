from fastapi import FastAPI

from time import sleep

app = FastAPI()


class Lgc(object):
    """LCG RNG.
    
    See <https://en.wikipedia.org/wiki/Linear_congruential_generator>

    Uses mapping

    x_next = (a * x + c) mod m
    
    with
    
    a = 1664525
    c = 1013904223
    m = 2 ** 32
    
    """

    a = 1664525
    c = 1013904223
    m = 2 ** 32

    def __init__(self, seed: int = 0):
        """Initialize with an integer seed value."""
        self.x = seed

    def next_rand(self, x: int = None, delay: float = 0.0):
        """For a given x, return the next random x."""
        if x is not None:
            self.x = x

        sleep(delay)
        self.x = (self.a * self.x + self.c) % self.m
        return self.x

    def lcg_params(self):
        """Return dict of own config."""
        return {"a": self.a, "c": self.c, "m": self.m}


app.lcg = Lgc()


@app.get("/lcg/")
async def get_lcg(x: int = None, delay: float = 0.5):
    """Query the LCG RNG for a random integer."""
    return app.lcg.next_rand(x, delay)


@app.get("/lcg_params/")
async def get_lcg():
    """Query the LCG RNG for a random integer."""
    return app.lcg.lcg_params()
