import requests


class Particle(object):
    def __init__(self, x: int = 0, y: int = 0, t: int = 0):
        self.x = x
        self.y = y
        self.t = t
        self.lgc_params = requests.get(
            "http://rng_loadbalancer:4000/lgc_params/"
        ).json()

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

    def position(self):
        return (self.x, self.y, self.t)
