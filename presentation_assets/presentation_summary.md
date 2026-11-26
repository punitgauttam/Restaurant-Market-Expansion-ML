# Presentation summary: restaurant market expansion

## Finding

In the single 2018–2021 held-out evaluation, white-space captured 838 industry-wide net additions at K=5, compared with -8 for population and Ridge. At K=10 and K=20, white-space captured 1,081 and 1,359 additions. This is a historical proxy result, not a chain-level return estimate.

## Top-five selections

### Population — total observed net additions: -8
1. New York-Newark-Jersey City, NY-NJ-PA — -285
2. Los Angeles-Long Beach-Anaheim, CA — -185
3. Chicago-Naperville-Elgin, IL-IN-WI — -93
4. Dallas-Fort Worth-Arlington, TX — +312
5. Houston-The Woodlands-Sugar Land, TX — +243

### White-space — total observed net additions: +838
1. Miami-Fort Lauderdale-West Palm Beach, FL — +92
2. Tampa-St. Petersburg-Clearwater, FL — +138
3. Houston-The Woodlands-Sugar Land, TX — +243
4. Phoenix-Mesa-Scottsdale, AZ — +193
5. Riverside-San Bernardino-Ontario, CA — +172

### Ridge — total observed net additions: -8
1. New York-Newark-Jersey City, NY-NJ-PA — -285
2. Los Angeles-Long Beach-Anaheim, CA — -185
3. Chicago-Naperville-Elgin, IL-IN-WI — -93
4. Dallas-Fort Worth-Arlington, TX — +312
5. Houston-The Woodlands-Sugar Land, TX — +243

## Method and evaluation

The evaluation universe is the 100 largest eligible MSAs by 2016 PEP population. The training set contains 383 MSAs. The target is CBP 2021 MSA establishments minus CBP 2018 MSA establishments. Ridge uses alpha=1.0. Every method ranks the same evaluation candidates.

| Method | K | Selected additions | Regret | Overlap | Precision@K | NDCG@K |
|---|---:|---:|---:|---:|---:|---:|
| Population | 5 | -8 | 1,210 | 2/5 | 0.40 | 0.300 |
| Ridge | 5 | -8 | 1,210 | 2/5 | 0.40 | 0.300 |
| White-space | 5 | 838 | 364 | 3/5 | 0.60 | 0.592 |
| Population | 10 | 29 | 1,819 | 3/10 | 0.30 | 0.353 |
| Ridge | 10 | 29 | 1,819 | 3/10 | 0.30 | 0.353 |
| White-space | 10 | 1,081 | 767 | 5/10 | 0.50 | 0.554 |
| Population | 20 | 139 | 2,413 | 8/20 | 0.40 | 0.426 |
| Ridge | 20 | 53 | 2,499 | 8/20 | 0.40 | 0.424 |
| White-space | 20 | 1,359 | 1,193 | 10/20 | 0.50 | 0.548 |

## Boundaries

- Evaluation spans 2018–2021, includes COVID-19, and is the only evaluation window.
- OMB 2017 county assignments are applied retrospectively.
- The target is industry-wide net establishment additions, not chain revenue, profit, survival, or causal entry returns.
- Post-2017 suppressed small CBP cells are unknown, not zero.
- White-space score and observed outcome are different quantities.

Generated PNGs and the self-contained dashboard use the verified outputs under `outputs/tables/`.
