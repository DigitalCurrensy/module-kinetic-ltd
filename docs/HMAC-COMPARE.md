# hmac.compare_digest vs Photonseal

Live `verify_interval`:

```
expected = seal_interval(... same fields ..., signing_key)
return hmac.compare_digest(interval.signature, expected.signature)
```

Both sides are 64-char hex from HMAC-SHA256. `compare_digest` is a
constant-time equality test for equal-length strings. It is not a
signature algorithm.

`==` on hex would also be correct for honest callers. It is not
constant-time and can leak how far two tags match. Use compare_digest
anyway.

Empty key: `seal_interval` raises `SealRefused` before compare.
Wrong key: compare returns False. Forged tag of the same length:
compare returns False unless the attacker has K.

`grade`, `wrapped`, `status` are gates on `seal_from_run`. They are
not in the MAC material. compare_digest cannot see them.
