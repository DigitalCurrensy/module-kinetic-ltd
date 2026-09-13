# hmac.compare_digest vs Photonseal

Live `verify_interval` computes HMAC-SHA256 via `_mac` then
`hmac.compare_digest`. It does **not** call `seal_interval`.

Empty key → False. Wrong key → False. Good key → True.
Seal still refuses empty key and gps_peer. Verify never raises for a bad key.

`compare_digest` is constant-time equality for equal-length strings.
It is not a signature algorithm.

`grade`, `wrapped`, `status` are gates on `seal_from_run`. They are not
in the MAC material. compare_digest cannot see them.
