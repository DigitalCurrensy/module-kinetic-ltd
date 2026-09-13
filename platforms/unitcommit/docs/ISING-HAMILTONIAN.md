# Module Kinetic Ltd — Unitcommit Hamiltonian construction

Not a recap. This is the construction the solver implements.

## 0. What is allowed on the quantum device

Only clustered binaries.

- `u[k,t] ∈ {0,1}` cluster `k` committed in interval `t`
- `v[k,t] ∈ {0,1}` cluster `k` starts in interval `t`
- spin `σ[k,t] = 2 u[k,t] − 1`
- QUBO bit `x = (1 − σ) / 2`

Continuous `p, q, V` stay on ADMM + AC-OPF. Raw DER inverters are members of `vpp_clusters`, never individual spins.

## 1. Indexing

```
T = horizon_minutes / interval_minutes
K = len(vpp_clusters)
n_u = K * T
n_v = K * T
n   = n_u + n_v

u_index(k, t) = k*T + t
v_index(k, t) = n_u + k*T + t
```

Store this on `ising_jobs.index_spec` jsonb:
`{T, K, n_u, n_v, n}`

After anneal, persist one `spin_assignments` row per spin:
`(spin_index, cluster_id, time_step, sigma, committed)`.
Count must equal `ising_jobs.spin_count`.

## 2. Classical cost that becomes linear QUBO

```
min Σ_{k,t}  C_nl[k] * u[k,t]  +  C_su[k] * v[k,t]
```

Marginal energy cost is applied in the dispatch slave, not here.

## 3. Hard logic as quadratic penalties

Startup definition (`λ_logic`, default 5000).
`t = 0` uses `u[k,-1] = initial_on[k]`.

```
v[k,t] >= u[k,t] − u[k,t-1]
v[k,t] <= u[k,t]
v[k,t] <= 1 − u[k,t-1]
```

QUBO:

```
v (1 − u)              # v <= u
v * u_prev             # v <= 1 − u_prev
(u − u_prev − v)^2     # v >= Δu
```

Minimum up (`λ_mut`, default 4000):

```
for k' in 1 .. MUT[k]-1:
    v[k,t] * (1 − u[k, t+k'])
```

Reserve (`λ_R`, default 20):

```
(Σ_k (Pmax[k]−Pmin[k]) u[k,t]  −  R[t])^2
```

Minimum online capacity hint (`λ_D`, default 8, `α = 0.4`):

```
(Σ_k Pmin[k] u[k,t]  −  α D[t])^2
```

True power balance is the OPF slave.
Corridor gates (`λ_line`) are optional PTDF squares on critical branches.

## 4. QUBO → Ising

```
E(x) = x^T Q x + q^T x          x ∈ {0,1}^n
x_i = (1 − σ_i) / 2
H(σ) = const + Σ_i h_i σ_i + Σ_{i<j} J_ij σ_i σ_j
```

Conversion used in code:

```
h_i  += −0.5 q_i
for each Qs_ij:
    h_i  += −0.25 Qs_ij
    h_j  += −0.25 Qs_ij
    J_ij +=  0.25 Qs_ij     (i ≠ j)
```

`Qs = (Q + Q^T)/2`. Constant term dropped (does not change argmin).

Storage: `h_json` + `j_coo_json` if `n < 2000`, else object keys under `r2://module-kinetic/{tenant}/unitcommit/ising/`.

## 5. Worked example — 2 clusters × 2 intervals

| cluster | Pmin | Pmax | Cnl | Csu | MUT | initial_on |
|---------|------|------|-----|-----|-----|------------|
| 0 thermal-like | 20 | 80 | 400 | 1200 | 2 | 1 |
| 1 BESS aggregate | 0 | 25 | 10 | 5 | 1 | 0 |

Demand `[60, 70]` MW. Reserve `[5, 5]` MW.
`λ_logic=5000`, `λ_mut=4000`, `λ_R=20`, `λ_D=8`, `α=0.4`.

Index map:

```
u[0,0]=0  u[0,1]=1  u[1,0]=2  u[1,1]=3
v[0,0]=4  v[0,1]=5  v[1,0]=6  v[1,1]=7
n = 8
```

A feasible bitstring (stay on cluster 0, start cluster 1 at t=1):

```
x = [1, 1, 0, 1, 0, 0, 0, 1]
```

Clearance after anneal still requires an `opf_solutions` row whose `residual_mw` is inside `commitment_runs.tolerance_mw`, and `count(spin_assignments) == ising_jobs.spin_count`. Without both, status cannot become `cleared`.

## 6. Handoff

```
build_ising(zone_snapshot) → IsingProblem
solve_commitment(...)      → CommitmentVector
admm_dispatch(...)         → Setpoints
publish_setpoints          → OutboxEvent
```

`<500 ms` is the budget for the clustered problem, not millions of raw DERs.
