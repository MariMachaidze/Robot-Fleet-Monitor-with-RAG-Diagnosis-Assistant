---
doc_id: IR-2025-031
doc_type: incident_report
robot_model: AMR-100
firmware: 1.4
error_code: E42
last_updated: 2025-04-02
---

# Incident Report IR-2025-031: Wheel Motor Stall and 12-Day Downtime

## Summary

On 10 March 2025, AMR-100 robot 1 stopped with error 42 (wheel motor stall) in aisle 3. The wheel motor had to be replaced, but no replacement motor was in stock. The robot was out of service for 12 days.

## What happened

1. 10 Mar, 09:12: robot 1 reported E42. The telemetry showed a frozen position and a battery falling about three times faster than normal.
2. 09:20: the operator reset the motor controller twice. The robot moved a few centimetres and stalled again. Resetting a stalled brushed motor is not a fix and risks burning the windings.
3. 09:45: maintenance pressed the emergency stop, moved the robot to the maintenance bay with manual recovery, and found worn motor brushes.
4. 10 Mar, afternoon: the ERP showed stock 0 for the AMR-100 wheel motor assembly (SP-1001). The lead time at that time was 10 days.
5. 12 Mar: the maintenance notification was created and approved, two days late.
6. 22 Mar: the motor arrived and was installed the same day. Robot 1 returned to service.

## Root cause

Worn brushes in the brushed wheel motor. The 6-month brush inspection from the maintenance schedule had been skipped.

## What fixed it

Replacing the wheel motor assembly (SP-1001).

## Lessons learned

1. On the AMR-100, error 42 means a motor replacement. Do not reset and restart the motor.
2. Check spare-part stock in the ERP as soon as the fault is diagnosed, and create the maintenance notification the same day. The two-day delay added two days of downtime.
3. Keep at least one AMR-100 wheel motor in stock. A reorder point was requested from purchasing.
4. Lead times change. Always read the current lead time in the ERP instead of relying on this report.
5. Do the 6-month brush inspection on time.
