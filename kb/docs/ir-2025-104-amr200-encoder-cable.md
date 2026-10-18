---
doc_id: IR-2025-104
doc_type: incident_report
robot_model: AMR-200
firmware: 2.0
error_code: E-42
last_updated: 2025-11-12
---

# Incident Report IR-2025-104: E-42 on an AMR-200 Fixed by Reseating the Encoder Cable

## Summary

On 4 November 2025, AMR-200 robot 3 stopped with E-42 in aisle 5. The technician on duty planned to replace the wheel motor, as is done on the AMR-100. The real cause was a loose wheel encoder cable, and reseating the cable fixed the fault in 20 minutes.

## What happened

1. 4 Nov, 14:05: robot 3 reported E-42 and stopped. Its position stayed the same across readings.
2. 14:15: the technician followed the AMR-100 practice, checked the ERP and found an AMR-200 wheel motor assembly (SP-1002) in stock. A maintenance notification for a motor replacement was drafted.
3. 14:30: before approving it, the maintenance supervisor asked for the AMR-200 error code reference to be checked. It lists the encoder cable as the first thing to check.
4. 14:40: the encoder connector on the left drive module was found half unplugged. It was pushed in and locked.
5. 14:50: the motor controller was reset from the dashboard. Robot 3 drove normally and E-42 did not return.
6. The draft notification was rejected, and a new notification was created for a routine check of all encoder connectors.

## Root cause

A loose wheel encoder connector, most likely shaken loose by a damaged floor joint in aisle 5. Firmware 2.0 reports the lost encoder signal as E-42.

## What fixed it

Reseating the wheel encoder cable connector. No parts were used.

## Lessons learned

1. The same code does not mean the same fix. E42 on the AMR-100 usually needs a new motor, while E-42 on the AMR-200 usually needs only the encoder cable to be reseated.
2. Always use the error code reference for the robot's own model.
3. The approval step caught an expensive mistake. Keep a human approval on every maintenance notification.
4. The damaged floor joint in aisle 5 was reported to facilities.
