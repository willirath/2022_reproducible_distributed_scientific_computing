from fastapi import FastAPI

app = FastAPI()


class Lgc(object):
    """LGC RNG.
    
    See <https://en.wikipedia.org/wiki/Linear_congruential_generator>

    Uses mapping

    X = (a * X + c) mod m
    
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

    def next_rand(self, x: int = None):
        """For a given x, return the next random x."""
        return (self.a * x + self.c) % self.m

    def query(self, x: int = None):

        if x is None:
            self.x = self.next_rand(x=self.x)
            return self.x
        else:
            return self.next_rand(x=x)


lgc = Lgc()


@app.get("/lgc/")
async def get_lgc(x: int = 0):
    """Query the LGC RNG for a random integer."""
    return lgc.query(x)
