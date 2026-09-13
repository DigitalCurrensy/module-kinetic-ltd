# Unitcommit Hamiltonian construction

Code law. Live builder: `platforms/unitcommit/src/application/build_ising.py`.

## 0. What is allowed on the quantum device

Only clustered binaries.

- `u[k,t] ∈ {0,1}` cluster `k` committed in interval `t`
- `v[k,t] ∈ {0,1}` cluster `k` starts in interval `t`
- `σ = 2u − 1` so `σ = +1` means ON
- `x = u = (σ + 1) / 2`

Continuous `p, q, V` stay on ADMM + AC-OPF. Raw DER inverters are members of a cluster, never individual spins.

## 1. Indexing (live)

```
T = len(demand_mw)
K = len(clusters)
n_u = K * T
n_v = K * T
n   = n_u + n_v

u_index(k, t) = k*T + t
v_index(k, t) = n_u + k*T + t
```

Clearance requires `assignment_count == n` and `opf.spin_count == n`.

## 2. Classical cost — linear QUBO, not scaled by derate `f`

```
q[u_{k,t}] += C_nl[k]
q[v_{k,t}] += C_su[k]
```

## 3. Hard logic as quadratic penalties (live defaults)

`λ_logic = 50`, `λ_mut = 40`, `λ_R = 20`, `λ_D = 8`, `α = 0.4`, `normalize = per_unit`.

Startup identity, `t = 0` uses `u[k,-1] = initial_on[k]`:

```
(u − u_prev − v)^2     plus v(1 − u) and the complementary bound
```

Minimum up:

```
for τ in 1 .. MUT[k]-1:
    λ_mut * v[k,t] * (1 − u[k, t+τ])
```

Reserve and demand hint after per-unit scale `s = max Pmax` (recomputed AFTER Cabinetfield shrink):

```
ĉ_k = Pmax_k / s
p̂_k = Pmin_k / s
R̂_t = R_t / s
D̂_t = α D_t / s

q[u_{k,t}] += λ_R (ĉ_k² − 2 ĉ_k R̂_t) + λ_D (p̂_k² − 2 p̂_k D̂_t)
Q[u_i,t ; u_j,t] += 2 λ_R ĉ_i ĉ_j + 2 λ_D p̂_i p̂_j
```

True power balance is the OPF slave. Corridor gates are not in the live builder.

## 4. QUBO → Ising (live `build_ising`)

```
E(x) = q·x + Σ_{i<j} Q_ij x_i x_j
x = (σ + 1) / 2

h_i  += q_i / 2
for each Q_ij:
    h_i += Q_ij / 4
    h_j += Q_ij / 4
    J_ij = Q_ij / 4
```

Do not use `x = (1 − σ)/2` or negative half-q increments. Those signs are retired.

## 5. Worked example — 2 clusters × 2 intervals

| cluster | Pmin | Pmax | Cnl | Csu | MUT | initial_on |
|---------|------|------|-----|-----|-----|------------|
| 0 | 20 | 80 | 400 | 1200 | 2 | 1 |
| 1 | 0 | 25 | 10 | 5 | 1 | 0 |

Demand `[60, 70]` MW. Reserve `[5, 5]` MW. Live λ, not 5000/4000.

```
u[0,0]=0  u[0,1]=1  u[1,0]=2  u[1,1]=3
v[0,0]=4  v[0,1]=5  v[1,0]=6  v[1,1]=7
n = 8
```

Clearance after anneal still requires `residual_mw ≤ tolerance_mw` and spin width `n`.

## 6. Handoff

```
clusters_from_flex(flex, derates) → tuple[Cluster]
build_ising(zone_snapshot)        → IsingProblem
build_and_clear(...)              → CommitmentRun {cleared|refused}
```
