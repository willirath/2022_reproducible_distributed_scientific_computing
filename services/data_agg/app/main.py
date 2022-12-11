from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

import pandas as pd
import numpy as np
import asciichartpy

import redis

app = FastAPI()


class DataAgg(object):
    def __init__(self, target_step=10):
        """Initialize with number of particles."""
        self.target_step = 10
        self.redis_store = redis.Redis(host="data_agg_redis", port=6379)
        self.redis_store.hset("config", "target_step", self.target_step)

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

    def data_show(self):
        df = self.get_particle_positions()
        return str(df)

    def diags_show(self):
        df = self.get_particle_positions()
        com_x = df.groupby("t")["x"].mean()
        com_x_chart = "center of mass X:\n" + asciichartpy.plot(
            list(com_x), {"height": 5}
        )
        com_y = df.groupby("t")["y"].mean()
        com_y_chart = "center of mass Y:\n" + asciichartpy.plot(
            list(com_y), {"height": 5}
        )
        moi = df.groupby("t")["x"].var() + df.groupby("t")["y"].var()
        print(moi)
        moi_chart = "moment of inertia:\n" + asciichartpy.plot(list(moi), {"height": 5})
        return "\n\n".join(
            ["== Random Walk Stats ==", com_x_chart, com_y_chart, moi_chart]
        )

    def get_particle_positions(self):
        particle_ids = list(
            map(lambda b: b.decode("utf-8"), self.redis_store.smembers("particle_ids"))
        )
        particle_positions = []
        for pid in particle_ids:
            _t = list(map(int, self.redis_store.lrange(f"{pid}:t", 0, -1)))
            _x = list(map(float, self.redis_store.lrange(f"{pid}:x", 0, len(_t))))
            _y = list(map(float, self.redis_store.lrange(f"{pid}:y", 0, len(_t))))
            _df = pd.DataFrame(dict(t=_t, x=_x, y=_y))
            _df["pid"] = pid
            particle_positions.append(_df)
        return pd.concat(particle_positions, ignore_index=True)


app.dataagg = DataAgg()


@app.get("/data_show/", response_class=PlainTextResponse)
async def data_show():
    """Show diags"""
    return app.dataagg.data_show()


@app.get("/diags_show/", response_class=PlainTextResponse)
async def diags_show():
    """Show diags"""
    return app.dataagg.diags_show()
