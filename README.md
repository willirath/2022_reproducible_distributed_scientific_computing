# Reproducible Distributed Scientific Computing

## Problem

Random Walk application with different distributed components:

- Random Number Generation
- Particle Movement
- External Fields
- Data Aggregation

```mermaid
graph LR;
    RNG1-->PM1;
    RNG1-->PM2;
    RNG1-->PM3;
    RNG2-->PM1;
    RNG2-->PM2;
    RNG2-->PM3;
    EF-->PM1;
    EF-->PM2;
    EF-->PM3;
    PM1-->DA;
    PM2-->DA;
    PM3-->DA;
```

