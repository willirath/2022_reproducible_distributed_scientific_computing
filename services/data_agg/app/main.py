from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

import pandas as pd
import numpy as np
import asciichartpy

import requests
import redis

app = FastAPI()


class DataAgg(object):
    def __init__(self, num_particles: int = 5):
        """Initialize with number of particles."""
        self.num_particles = num_particles
        self.diags_init()
        self.timestep = 0
        self.redis_store = redis.Redis(host="data_agg_redis", port=6379)

    def diags_init(self):
        self.diags = pd.DataFrame()

    def diags_run(self):
        positions = self.query_particle_positions()
        x = np.array([p[0] for p in positions])
        y = np.array([p[1] for p in positions])
        com_x = x.mean()
        com_y = y.mean()
        moi = x.var() + y.var()
        self.diags = pd.concat(
            [
                self.diags,
                pd.DataFrame({"com_x": [com_x,], "com_y": [com_y], "moi": [moi,]}),
            ],
            ignore_index=True,
        )
        self.diags = self.diags.tail(25).reset_index(drop=True)

    def diags_show(self):
        self.diags_run()
        com_x_chart = "center of mass X:\n" + asciichartpy.plot(
            self.diags["com_x"], {"height": 5}
        )
        com_y_chart = "center of mass Y:\n" + asciichartpy.plot(
            self.diags["com_y"], {"height": 5}
        )
        moi_chart = "moment of inertia:\n" + asciichartpy.plot(
            self.diags["moi"], {"height": 5}
        )
        return "\n\n".join(
            ["== Random Walk Stats ==", com_x_chart, com_y_chart, moi_chart]
        )

    def move_particles(self):
        self.timestep += 1
        self.redis_store.set("timestep", self.timestep)

    def query_particle_positions(self):
        positions = []
        for n in range(self.num_particles):
            resp = requests.get(f"http://services_particles_{n+1:d}:80/pos/")
            positions.append(resp.json())
        return positions


app.dataagg = DataAgg()


@app.get("/diags_show/", response_class=PlainTextResponse)
async def diags_show():
    """Show diags"""
    return app.dataagg.diags_show()
