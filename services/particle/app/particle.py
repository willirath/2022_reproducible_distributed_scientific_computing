import requests
import redis
import uuid
import time

import logging


class Particle(object):
    main_maxiter = 10_000
    stepsize = 1.0

    def __init__(self, x: int = 0, y: int = 0, t: int = 0):
        self.x, self.y, self.t = x, y, t
        self.redis_setup()
        self.lcg_params = requests.get(
            "http://rng_loadbalancer:4000/lcg_params/"
        ).json()
        self.run_main_loop()

    def redis_setup(self):
        """Draw unique particle ID and register it in REDIS store."""
        self.particle_id = str(uuid.uuid4())
        self.redis = redis.Redis(host="redis_store", port=6379)
        self.redis.sadd("particle_ids", self.particle_id)

        # added code
        length = self.redis.rpush("seeds", 0) # an easy approach to build distinct seeds                                                         
        self.seed = length - 1 # We assume rpush is atomic/synchronized
		#
		
        logging.info(f"Registered as {self.particle_id} on redis store.")
		

    def get_rand(self, x: int = None):
        """Get random number from RNG service and scale to [-1, 1)."""
        resp = requests.get("http://rng_loadbalancer:4000/lcg/", params={"x": x}) 
        N = int(resp.json())
        self.seed = N # added code
        return 2 * N / self.lcg_params["m"] - 1

    def step(self): 
        """Move by random step and increment time step."""
		# added code
        logging.info(f"[Seed used for x-value]: {self.seed}")
        self.x += self.get_rand(self.seed) * self.stepsize
        logging.info(f"[Seed used for y-value]: {self.seed}")
        self.y += self.get_rand(self.seed) * self.stepsize
		#
		
        self.t += 1
        logging.info(f"Stepped.")

    def store_position(self):
        """Save position to REDIS store."""
        self.redis.rpush(f"{self.particle_id}:x", self.x)
        self.redis.rpush(f"{self.particle_id}:y", self.y)
        self.redis.rpush(f"{self.particle_id}:t", self.t)
        logging.info(f"Stored.")

    def run_main_loop(self):
        """Poll for work (target_steps from REDIS store) an step / store pos."""
        self.main_niter = 0
        while self.main_maxiter > self.main_niter:
            self.main_niter += 1

            # get target num of time steps
            logging.info(f"Polling for more steps.")
            target_step = int(self.redis.hget("config", "target_step") or 0)
            # target_step = int(target_step)

            # add steps if necessary
            while self.t < target_step:
                self.step()
                self.store_position()

            time.sleep(0.5)  # wait before checking for more work


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    particle = Particle()
