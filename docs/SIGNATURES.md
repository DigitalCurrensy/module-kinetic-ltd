# Photonseal — MAC vs signature

Live tag is HMAC-SHA256. Anyone with `signing_key` can mint the same
64-char hex. That is a symmetric MAC. It is not non-repudiation.

| Object | Who can mint | Who can check | Live? |
|--------|--------------|---------------|-------|
| HMAC-SHA256 | holder of K | holder of K | yes |
| Ed25519 | holder of sk | holder of pk | no |
| ECDSA P-256 | holder of sk | holder of pk | no |
| ML-DSA (Dilithium) | holder of sk | holder of pk | no |

Ed25519 is the next honest public-key slice if called. ML-DSA is the
PQ slice after that. Neither is a token, a ledger write, or entangled
photon proof.

`kind = signed_meter` means attested interval, not a digital signature
class. Do not rename the house.
