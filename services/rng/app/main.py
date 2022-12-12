from fastapi import FastAPI

from time import sleep

app = FastAPI()


class Lgc(object):
    """LGC RNG.
    
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

    def next_rand(self, delay: float = 0.0):
        """For a given x, return the next random x."""
        sleep(delay)
        self.x = (self.a * self.x + self.c) % self.m
        return self.x

    def lgc_params(self):
        """Return dict of own config."""
        return {"a": self.a, "c": self.c, "m": self.m}


app.lgc = Lgc()


@app.get("/lgc/")
async def get_lgc(x: int = None, delay: float = 0.1):
    """Query the LGC RNG for a random integer."""
    return app.lgc.next_rand(delay)


@app.get("/lgc_params/")
async def get_lgc():
    """Query the LGC RNG for a random integer."""
    return app.lgc.lgc_params()
