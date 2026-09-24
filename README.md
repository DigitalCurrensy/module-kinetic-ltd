# Module Kinetic Ltd

When a charger breaks, this software signs off on it, or it refuses it.

If the checks pass, it saves one signed record. If a check fails, it saves nothing and says why.

Copyright 2026 DIGITAL CURRENSY INC / Module Kinetic Ltd. Apache-2.0.

## Who it is for

People who run chargers, and people on the power grid who have to explain why a charger was allowed back on.

## What you do

1. A fault comes in from the charger.
2. Seven checks run, in order.
3. You get a signed record, or a refusal.

Sending the same fault twice does not create a second record.

## The seven checks

| Name | In plain words | It refuses when |
| --- | --- | --- |
| Bayline | Was this a real fault? | The message is the old charger protocol, or it is only a status update |
| Loadclear | Is this charger allowed back on? | There is no repair job, or someone tries to turn it on while it is locked |
| Cabinetfield | Was the cabinet measured? | The fault is serious and there is no calibration for that time |
| Unitcommit | Do the power numbers add up? | The power does not match |
| Phasepin | Is the clock good enough? | The only clock is GPS, or the clock error is too large |
| Fiberlock | Is the line clean enough? | The line has too many errors |
| Photonseal | Is the record signed? | There is no signing key |

The signing key is not saved in the record.

## What this is not

It does not run the charger. It does not sell carbon credits. It does not make a coin or a token.

## How to run the tests

GitHub will not open the operator screen. This repository is the checks.

```bash
python -m pip install pytest
PYTHONPATH=. python -m pytest tests
```

Do not put a database password or a signing key in the repository. If no database is set, a live save writes nothing.

## The seven parts

Each check lives in its own repository. They stay separate.

| Part | What it checks | Repository |
| --- | --- | --- |
| Bayline | The fault message | [bayline](https://github.com/DigitalCurrensy/bayline) |
| Loadclear | Whether the charger can be used | [loadclear](https://github.com/DigitalCurrensy/loadclear) |
| Cabinetfield | The cabinet measurement | [cabinetfield](https://github.com/DigitalCurrensy/cabinetfield) |
| Unitcommit | The power numbers | [unitcommit](https://github.com/DigitalCurrensy/unitcommit) |
| Phasepin | The clock | [phasepin](https://github.com/DigitalCurrensy/phasepin) |
| Fiberlock | The line | [fiberlock](https://github.com/DigitalCurrensy/fiberlock) |
| Photonseal | The signature | [photonseal](https://github.com/DigitalCurrensy/photonseal) |

## License

You can use this code, change it, and sell a product built with it. You have to keep the copyright line and the license with any copy. See [LICENSE](LICENSE). The names Digital Currensy and Module Kinetic are not part of that permission.
