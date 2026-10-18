---
doc_id: RN-FW14
doc_type: release_notes
robot_model: all
firmware: 1.4
last_updated: 2024-05-20
---

# Firmware 1.4 Release Notes

Firmware 1.4 is available for AMR-100 and AMR-200 robots. It replaces firmware 1.2.

## New features

### Auto-dock and Send to charger

1. Robots can now be sent to the charger from the fleet dashboard: select the robot and press **Send to charger**.
2. The robot drives to the nearest free charging station and docks by itself. Auto-dock works down to 5% battery.
3. **This replaces the manual pendant docking procedure in "Operating Procedure: Return to Charger" (OP-02, March 2023).** That procedure is now outdated. Manual docking with the pendant caused misaligned contacts and burnt charging contact plates (SP-1013, SP-1014), so it should no longer be used.
4. Below 5% battery, use manual recovery (OP-03) to move the robot to the charger.

### Faster wheel stall detection

1. The motor controller now detects a wheel motor stall within 2 seconds and reports E42.
2. A stalled motor keeps drawing current until the emergency stop is pressed, so the battery falls about 3x faster during a stall.

### Communication watchdog

1. A robot now stops by itself when it loses the connection to the fleet manager for more than 2 seconds.
2. When the connection returns, the robot reports E60 and waits for an operator.

## Fixed issues

1. The battery percentage jumped by up to 5% after charging. This is fixed.
2. Robots sometimes reported E21 when a person walked past without stopping. The safety field timing was adjusted.

## Known issues

1. The dashboard keeps showing the last known status of a robot that has lost its connection. Check the timestamp of the last reading.
2. Firmware 1.4 does not support the new localization engine. It is planned for firmware 2.0, which will be available for the AMR-200 only.

## Upgrade notes

1. Upgrade one robot at a time and keep the others running.
2. After the upgrade, run the self-test from the dashboard.
