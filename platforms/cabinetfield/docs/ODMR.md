# Cabinetfield — ODMR derate

NV S=1. Zero-field splitting D ≈ 2.87 GHz.

```
f± = D ± γ B∥
γ ≈ 28.024 GHz/T = 28.024 MHz/mT
B∥ = (f+ − f−) / (2γ)
```

`issue_derate` returns a factor in [0, 1] that multiplies Unitcommit cluster Pmax.
`severity=critical` without a `calibration_run` covering `observed_at` on that cabinet is illegal.
