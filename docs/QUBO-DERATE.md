# QUBO coefficients after Cabinetfield derate

Code law: σ = 2u − 1, x = (σ+1)/2, σ = +1 means ON.
Live penalties: λ_logic=50, λ_mut=40, λ_R=20, λ_D=8, α=0.4, normalize=per_unit.

## Shrink

Pmax'_k = f_k Pmax_k
Pmin'_k = f_k Pmin_k
C_nl, C_su unchanged. f=0 forces initial_on=0.

s = max_k Pmax'_k
ĉ_k = Pmax'_k / s
p̂_k = Pmin'_k / s
R̂_t = R_t / s
D̂_t = α D_t / s

## Linear q on u_{k,t}

q[u_kt] = C_nl
        + λ_logic · (startup identity diagonal)
        + λ_R (ĉ_k² − 2 ĉ_k R̂_t)
        + λ_D (p̂_k² − 2 p̂_k D̂_t)

## Off-diagonal Q between u_{i,t} and u_{j,t}

Q_ij(t) = 2 λ_R ĉ_i ĉ_j + 2 λ_D p̂_i p̂_j

## Ising

J_ij = Q_ij / 4 = (λ_R / 2) ĉ_i ĉ_j + (λ_D / 2) p̂_i p̂_j
h_i  = q_i / 2 + Σ_{j≠i} Q_ij / 4

Startup / min-up terms do not carry f except via initial_on=0 when f=0.
