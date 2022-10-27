# Reproducible Distributed Scientific Computing

## Problem

Random Walk application with different components:

- Random Number Generation
- Particle Set
- External Fields
- Data Aggregation

```mermaid
graph TD;
    RNG-->PS;
    EF-->PS;
    PS-->DA;
```

## Parallelisation

We can follow different strategies here

Either, we replicate all parts (and bring everything together in the data aggregation step):

```mermaid
graph TD;
    RNG1-->PS1;
    EF1-->PS1;
    RNG2-->PS2;
    EF2-->PS2;
    PS1-->DA;
    PS2-->DA;
```

Or, depending on where the actual cost is spent, we could go for more diverse patterns (where `EF` and `RNG` are load balancers):

```mermaid
graph TD;
    RNG1-->RNG;
    RNG2-->RNG;
    RNG3-->RNG;
    EF1-->EF;
    EF2-->EF;
    RNG-->PS1;
    RNG-->PS2;
    EF-->PS1;
    EF-->PS2;
    PS1-->DA;
    PS2-->DA;
```
