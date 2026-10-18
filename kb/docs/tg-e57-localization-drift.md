---
doc_id: TG-E57
doc_type: troubleshooting_guide
robot_model: AMR-200
firmware: 2.0
error_code: E57
last_updated: 2025-10-28
---

# Troubleshooting Guide: Localization Drift (E57)

## Applies to

AMR-200 robots running firmware 2.0. Firmware 1.4 does not raise E57.

## Symptoms

- The reported position jumps by more than 3 cells in a single reading.
- The robot keeps moving after the jump, and every reading carries E57.
- The status is usually moving, not error. This separates E57 from a lidar dropout (E33).

## Cause

Firmware 2.0 introduced a new localization engine with a new map format. A robot that runs on a map built under firmware 1.4, or on a map that was only partly converted, matches its lidar scans against the wrong map. Its position estimate jumps to a wrong place, and the robot continues driving on that wrong estimate.

## Steps

1. Stop the robot from the dashboard. A robot driving on a wrong position estimate can enter areas it should not.
2. Check which map version the robot uses (dashboard, robot details, Map). A version starting with v1. means the map was never converted.
3. Convert the site map with the map conversion tool shipped with firmware 2.0, then load the converted map on the robot.
4. Move the robot to the charger or another known marker with manual recovery (OP-03), and run **Relocalize** from the dashboard.
5. Release the robot and watch the next 20 readings. The position should change by at most one cell per reading.

## If E57 continues on a converted map

1. Re-map the aisle where the jumps happen. Racking changes since the last mapping can also cause a mismatch.
2. If the jumps continue after re-mapping, collect the telemetry and escalate to the vendor.

## Background

The localization change is described in the firmware 2.0 release notes (RN-FW20), in the section "Localization changes". Plan map conversion before every firmware 2.0 rollout, not after the first E57.
