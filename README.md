# Reproducible Distributed Scientific Computing

## Problem and introduction

We'll work with a 2-dimensional [random walk](https://en.wikipedia.org/wiki/Random_walk) application with different components.

- *__(Pseudo) Random Number Generator:__* Generates pseudo-random numbers which are used to determine the steps each particle takes.  (We'll learn more about random number generation below.)
- *__Particles:__* Handles position and movement of multiple particles.
- *__Data Aggregation:__* Aggregates information about the particles (could be distance travelled by each particle, distribution of all particles in space, etc.)

The relationship can be visualised as follows:
```mermaid
erDiagram
    DataAgg ||--|| Particle : "configures"
    Particle ||--|| DataAgg : "sends positions"
    Particle ||--|| RNG : "requests random number"

    DataAgg {
        int target_step PK "target number of time steps"
    }

    Particle {
        string particle_id
        float x
        float y
        int step
        int target_step FK "configured by DataAgg"
    }

    RNG {
        int state
    }
```


### Discussion of the components

#### Particles

We'll handle `N` particles which are moving in small and random discrete steps. For a particle with index `n` which is at step `l`, the movement can be expressed as
$$x_{n,l+1} = x_{n,l} + \delta x$$
$$y_{n,l+1} = y_{n,l} + \delta y$$
$$\delta x, \delta y \in [-1, 1)$$
where $x_{n,l}$ and $y_{n,l}$ are positions of particle $n$ at step $l$, and $\delta x$ and $\delta y$ are drawn from a uniform random distribution between -1 and 1.

#### Data Aggregation

We'll calculate two quantities which describe the overall distribution of the particles at step $l$:

The _center of mass_
$$COM_l = (\overline{x_l}, \overline{y_l})$$
with
$$\overline{x_l} = \frac{1}{N}\sum_{n=1}^N x_{n,l}$$
$$\overline{y_l} = \frac{1}{N}\sum_{n=1}^N y_{n,l}$$

is the point in space where the mass-weighted sum of positions averages to zero. (Here, we assume that all particles have the same mass.)

The _moment of inertia_ (relative to the center of mass)
$$MOI_l = \sum_{n=1}^N ((x_{n,l}-\overline{x_l})^2 + (y_{n,l}-\overline{y_l})^2)$$

determines the torque one needs to apply in order to achieve an angular acceleration. _(More mass away from the center of mass means higher $MOI$.)_

#### (Pseudo)-Random Number Generators (pRNG)

Generating good pseudo-random numbers is an own research field. There are criteria for "good" random numbers which are along the lines of requiring convergence towards the desired distribution and independence (or lack of predictability) between subsequent numbers.

A pRNG has an internal state wich is changed everytime a random number is drawn. By choosing the initial state of the pRNG, we completely determine the  sequence of random numbers it will produce.

For different use cases, there's different ways of chosing the initial state of the pRNG: If you're building a game or create cryptographic keys, you want to avoid being able to reproduce the initial state.

In _scientific_ applications, however, we aim at reproducibility (or at least repeatability). Hence, we want to be able to control the initial state of the pRNG.

In our random-walk application, we use a very simple pRNG: The [linear congruential generator](https://en.wikipedia.org/wiki/Linear_congruential_generator) (LCG).  This generator is based on the mapping
$$
R' = (a \cdot R + c)\mod m
$$
where $a$, $c$, and $m$ are unsigned integers and where $m$ determines the maximum range of the possible (unsigned integer) random numbers $R$.

The LCG has many disadvantages, which render it un-usable for real scientific applications. Here, however, we'll take advantage of the very simple structure of the LCG and ignore these.

*__Note__ that for "good" pRNG's, the internal state can be quite large (e.g. 2.5kB for the standard generator used in Numpy and Matlab). For LGCs, hoever, the internal state is completely determined by the single unsigned integer $R$.*

## Parallelisation

To make use of concurrency or of other resources like main memory or IO bandwidth, we often need to parallelise scientific applications. For our simple random walk problem, can follow different strategies.

We could replicate all parts (and bring everything together in the data aggregation step):

```mermaid
erDiagram
    DataAgg ||--|| Particle_1 : "configures"
    Particle_1 ||--|| DataAgg : "sends positions"
    Particle_1 ||--|| RNG_1 : "requests random number"

    DataAgg ||--|| Particle_2 : "configures"
    Particle_2 ||--|| DataAgg : "sends positions"
    Particle_2 ||--|| RNG_2 : "requests random number"

    DataAgg ||--|| Particle_3 : "configures"
    Particle_3 ||--|| DataAgg : "sends positions"
    Particle_3 ||--|| RNG_3 : "requests random number"
```

Or we could go for more complex patterns (where `RNG_LB` is a load balancer for multiple instances of `RNG`s):

```mermaid
erDiagram
    DataAgg ||--|| Particle_1 : "configures"
    DataAgg ||--|| Particle_2 : "configures"
    DataAgg ||--|| Particle_3 : "configures"
    
    Particle_1 ||--|| DataAgg : "sends positions"
    Particle_2 ||--|| DataAgg : "sends positions"
    Particle_3 ||--|| DataAgg : "sends positions"

    Particle_1 ||--|| RNG_LB : "requests random number"
    Particle_2 ||--|| RNG_LB : "requests random number"
    Particle_3 ||--|| RNG_LB : "requests random number"

    RNG_LB ||--|{ RNG : "forward request"
```

Another possibility is the following:
```mermaid
erDiagram
    DataAgg ||--|| REDIS : "sets config"
    DataAgg ||--|| REDIS : "reads positions"

    Particle }o--|| REDIS : "reads config positions"
    Particle }o--|| REDIS : "sends positions"

    Particle }o--|| RNG_LB : "requests random number"

    RNG_LB ||--|{ RNG : "forward request"
```
Here, we added a REDIS store able to relay information between multiple instances of `Particle` and the `DataAgg` instance. _(Note that we've switched to a more concise notation indicating the number of instances of each entity on the link.)_

*__Note__ that we can easily parallelise into multiple instances of `Particles`, because in our simple problem, the individual particles don't interact with each other.*

## Reproducibility

To completely reproduce results with different parallel layouts, we'd need to control the following aspects:
- initial positions $(x^n_0, y^n_0)$ of all particles — _We'll solve this by starting all particles at $(0, 0)$._
- initial states of the pRNG — _We'll focus on these._

*__Note__ that we don't take into account effects from roundoff errors. If we cared for them, we'd also need to completely control the order of execution of all arithmetics in particle movement and in the data aggregation. If we'd simulate a chaotic physical system, we'd need to control roundoff errors as well.*

## Communication

For the last layout above, let's look at the sequence of interactions.

### Particle position update

Each particle instance will poll the REDIS store for configuration (the desired number of steps to be recorded), and query the necessary random numbers from the RNG.

```mermaid
sequenceDiagram
    participant RD as REDIS
    participant P as Particle
    participant R as RNG

    loop forever
        P->>RD: get target_step
        alt step < target_step
            P->>+R: Want random number
            R->>R: Update random state
            R-->>-P: Send random number
            P->>P: Update X
            P->>+R: Want random number
            R->>R: Update random state
            R-->>-P: Send random number
            P->>P: Update Y
            P->>P: Update step
            P-)RD: Store step, X, Y

        else step >= target_step
            P->>P: sleep delay
        end            
        
    end

```

### Multiple RNGs behind load balancer

With the `RNG` above actually forwarding the request for random numbers to one of multiple backend `RNG`s:
```mermaid
sequenceDiagram
    participant P as Particle
    participant RL as RNG_LB
    participant R1 as RNG_1
    participant R2 as RNG_2

    P->>+RL: "Want random number"
    RL->>R1: "Want random number"
    deactivate RL
    activate R1
    R1->>R1: Update internal state
    R1->>-P: "Send random number"
    P->>P: Update X

    P->>+RL: "Want random number"
    RL->>R2: "Want random number"
    deactivate RL
    activate R2
    R2->>R2: Update internal state
    R2->>-P: "Send random number"
    P->>P: Update Y

```

### User inspection / intervention

At the same time, one or more users can interact with the data aggregation:

```mermaid
sequenceDiagram
    actor A
    participant DA as DataAgg
    participant RD as REDIS

    par [check results]
        opt
            A->>+DA: Show charts!
            DA->>RD: Get positions
            DA->>-A: Send charts
        end
    and [reconfigure]
        opt
            A->>DA: Set new target_step
            DA->>RD: Set target_step
        end
    end
```

## Code

The parallel layout detailed above has been implemented using Docker compose. See the [services/](services/) directory for details.

## Exercises

1. Run the setup with multiple instances of the RNG service. Check the charts and compare to a run with only one RNG instance. What do you see?

2. ...