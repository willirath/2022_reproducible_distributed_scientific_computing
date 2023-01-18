from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

import pandas as pd
import json
import numpy as np
import asciichartpy

import redis

app = FastAPI()


class DataAgg(object):
    def __init__(self, target_step: int = 10):
        """Initialize with number of particles."""
        self.target_step = 10
        self.redis_store = redis.Redis(host="redis_store", port=6379)
        self.set_target_step(target_step)

    def set_target_step(self, target_step):
        self.redis_store.hset("config", "target_step", target_step)

    def diags_run(self):
        df = self.get_particle_positions()

        com_x = df.groupby("t")["x"].mean()
        com_y = df.groupby("t")["y"].mean()
        moi = df.groupby("t")["x"].var() + df.groupby("t")["y"].var()
        count = df.groupby("t")["x"].count()

        return com_x, com_y, moi, count

    def data_str(self):
        """Get (shortened) string representation of the data."""
        return str(self.get_particle_positions())

    def data_json(self):
        """Get JSON version of all data."""
        return json.loads(self.get_particle_positions().to_json())

    def charts(self, rolling_length: int = None):
        """Produce ASCII charts of center of mass and of moment of inertia."""
        com_x, com_y, moi, count = self.diags_run()
        if rolling_length is not None:
            com_x = com_x.tail(rolling_length)
            com_y = com_y.tail(rolling_length)
            moi = moi.tail(rolling_length)

        com_x_chart = "center of mass X:\n" + asciichartpy.plot(
            list(com_x), {"height": 5}
        )
        com_y_chart = "center of mass Y:\n" + asciichartpy.plot(
            list(com_y), {"height": 5}
        )
        moi_chart = "moment of inertia:\n" + asciichartpy.plot(list(moi), {"height": 5})

        count_chart = "number of data points:\n" + asciichartpy.plot(
            list(count), {"height": 3}
        )

        return "\n\n".join(
            [
                "== Random Walk Stats ==",
                com_x_chart,
                com_y_chart,
                moi_chart,
                count_chart,
            ]
        )

    def get_particle_positions(self):
        """Build particle position DataFrame from REDIS contents."""
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


@app.get("/data/str", response_class=PlainTextResponse)
async def data_str():
    """Get data as STR."""
    return app.dataagg.data_str()


@app.get("/data/json")
async def data_str():
    """Get data as JSON."""
    return app.dataagg.data_json()


@app.get("/charts/", response_class=PlainTextResponse)
async def charts(rolling_length: int = 100):
    """Show charts."""
    return app.dataagg.charts(rolling_length=rolling_length)


@app.get("/set_target_step/", response_class=PlainTextResponse)
async def set_target_step(target_step: int = 10):
    app.dataagg.set_target_step(target_step)
    return f"Set target step to {target_step}."
