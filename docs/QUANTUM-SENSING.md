# Quantum sensing applications — Module Kinetic Ltd

Sensing is not one product. Do not build a generic sensing platform.
QAOA / VQE / QPE are compute. CV-QKD is a key wrap. Signed meters are attestation.

## Cabinetfield — NV-center magnetometry (ship first)

Measures vector B and temperature outside a live tank.
Physics: NV S=1, D ≈ 2.87 GHz, f± = D ± γ B∥, γ ≈ 28.024 GHz/T.
Classes: winding_hotspot, bushing_leak, core_sat, pd_burst, oil_pump, healthy.
Derate shrinks Unitcommit cluster Cap[k] before build_ising.
Illegal: severity=critical without calibration_run covering observed_at.

## Phasepin — chip-scale atomic clocks

Measures proper time. CSAC + IEEE 1588. GPS is a peer sensor, never source of truth.
Stamps Unitcommit windows and Photonseal intervals with time_source.

## Densitywell — cold-atom gravimetry

Measures δg. Fuses density voxels onto a Wellpath cube. No closed-loop bit steering in v1.

## Fiberlock — not a plant sensor

CV-QKD. Operator object is a key session and a QBER tape. File under control-plane wrap.

## Photonseal — not a sensor

Signed meter interval first. BQC adapter later and labeled.

## Start order

1. Cabinetfield ODMR + baseline + derate.
2. Phasepin offset_ns + holdover on sites Unitcommit clears.
3. Fiberlock QBER on spans that carry those setpoints.
4. Densitywell only when a Wellpath cube exists.
