---
doc_id: RN-FW20
doc_type: release_notes
robot_model: AMR-200
firmware: 2.0
last_updated: 2025-09-15
---

# Firmware 2.0 Release Notes (AMR-200)

Firmware 2.0 is available for AMR-200 robots only. AMR-100 hardware cannot run firmware 2.0 and stays on firmware 1.4.

## Localization changes

1. Firmware 2.0 replaces the localization engine. The new engine matches lidar scans against a higher-resolution map and is more accurate in long aisles.
2. **The map format has changed.** Maps created under firmware 1.4 must be converted with the map conversion tool shipped with firmware 2.0 before a robot uses them.
3. A robot that runs on an unconverted or partly converted map can lose track of its position. Its position estimate jumps by more than 3 cells, and it reports the new error code E57. See the troubleshooting guide for E57.
4. After converting the map, relocalize every robot at the charger.

## New error code

- **E57, Localization drift.** Raised when the position estimate jumps by more than 3 cells. The robot keeps moving, so stop it from the dashboard.

## Other changes

1. The motor controller now also reports E-42 when the wheel encoder signal is lost, not only when the motor stalls. On the AMR-200 a loose encoder cable is therefore a common cause of E-42.
2. Auto-dock, introduced in firmware 1.4, is unchanged.
3. Error codes are shown with a hyphen on the robot display (E-42). Telemetry still uses the format without a hyphen (E42).

## Known issues

1. Robots in the Wi-Fi dead zone near aisle 7 still stop with E60. This is a site network issue, not a firmware issue.

## Upgrade steps

1. Convert the site map with the map conversion tool.
2. Upgrade one AMR-200 at a time.
3. Load the converted map, relocalize the robot at the charger and run the self-test.
4. Watch the first 50 readings for position jumps before releasing the robot to production.
5. Keep a copy of the old map. It is needed if the robot has to be rolled back to firmware 1.4.
