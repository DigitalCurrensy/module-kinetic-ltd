# Bayline — OCPP 2.1 event streams

## Two planes

| Plane | Message | RPC | Use |
|-------|---------|-----|-----|
| Diagnosis / availability | NotifyEvent | CALL, empty {} result | Receipts, Faulted, Alerting |
| High-rate telemetry | NotifyPeriodicEventStream | SEND (type 6), no result | Loadclear watts / Hz |

OCPP 1.6 StatusNotification is telemetry on a dead protocol. It is not a Bayline receipt.

## NotifyEvent (N07 / N08 / availability)

Envelope: generatedAt, seqNo, tbc, eventData[].
Each eventData row: eventId, timestamp, trigger in {Alerting, Delta, Periodic}, actualValue, component, variable, plus techCode, techInfo, cleared, severity, variableMonitoringId, eventNotificationType.

- trigger=Alerting → start a receipt (threshold / fault).
- trigger=Delta and variable=AvailabilityState and actualValue=Faulted → start a receipt.
- trigger=Delta AvailabilityState in {Available, Occupied, Reserved, Unavailable} → site state only, no work order.
- trigger=Periodic on NotifyEvent → slow monitor, not a receipt unless severity demands it.

## Periodic event streams (N11–N15)

1. SetVariableMonitoring with periodicEventStream {interval, values}.
2. CS OpenPeriodicEventStream {id, variableMonitoringId, params}.
3. CSMS stores constant metadata (component, variable, severity).
4. CS NotifyPeriodicEventStream SEND {id, basetime, pending, data[{t,v}]}.
5. Reconstruct timestamp = basetime + t, actualValue = v, attach stored metadata.
6. AdjustPeriodicEventStream if pending climbs. ClosePeriodicEventStream when the monitor dies.

SEND does not consume the single outstanding CALL slot. That is why streams exist.

Bayline receipt.py must refuse to open a work order from a stream sample.
