import requests
import redis
import uuid
import time


class Particle(object):
    def __init__(self, x: int = 0, y: int = 0, t: int = 0):
        self.x = x
        self.y = y
        self.t = t
        self.main_maxiter = 1_000
        self.lgc_params = requests.get(
            "http://rng_loadbalancer:4000/lgc_params/"
        ).json()
        self.redis_setup()
        self.main_loop()

    def main_loop(self):
        self.main_niter = 0
        while self.main_maxiter > self.main_niter:
            self.main_niter += 1
            time.sleep(0.5)  # sleep before checking for work again
            target_step = self.redis_store.hget("config", "target_step")
            if target_step is None:
                continue
            self.target_step = int(target_step)
            while self.t < self.target_step:
                self.step()

    def redis_setup(self):
        self.particle_id = str(uuid.uuid4())
        self.redis_store = redis.Redis(host="data_agg_redis", port=6379)
        self.redis_store.sadd("particle_ids", self.particle_id)

    def query_rng(self, x: int = None):
        resp = requests.get("http://rng_loadbalancer:4000/lgc/", params={"x": x})
        return int(resp.json())

    def normal_rand(self, num_summed: int = 11):
        random_ints = (self.query_rng() for n in range(num_summed))
        normal = (sum(random_ints) / self.lgc_params["m"] - num_summed / 2) / (
            num_summed / 12
        ) ** 0.5
        return normal

    def step(self):
        self.x += 2 * self.query_rng() / self.lgc_params["m"] - 1.0
        self.y += 2 * self.query_rng() / self.lgc_params["m"] - 1.0
        self.t += 1
        self.position_store()

    def position_store(self):
        self.redis_store.rpush(
            f"{self.particle_id}:x", self.x,
        )
        self.redis_store.rpush(
            f"{self.particle_id}:y", self.y,
        )
        self.redis_store.rpush(
            f"{self.particle_id}:t", self.t,
        )

    def position(self):
        return (self.x, self.y, self.t)
