---
doc_id: ECR-200
doc_type: error_code_reference
robot_model: AMR-200
firmware: 2.0
last_updated: 2025-10-20
---

# AMR-200 Error Code Reference (Firmware 2.0)

The AMR-200 display and this manual write error codes with a hyphen. E-42 here is the same code as E42 in telemetry. This reference covers firmware 2.0.

## E-10 Battery critically low

Symptoms: battery under 10% and status stopped. Fast drops of 5% or more per reading mean a degraded cell. A slow drop to 10% usually means a skipped charge cycle.

Fix:
1. Send the robot to the charger from the dashboard.
2. If the pack drains fast, replace the battery pack (SP-1010).

## E-21 Path blocked

Symptoms: position unchanged for 5 or more readings, status stopped.

Fix:
1. Clear the obstacle from the aisle.
2. Resume the robot from the dashboard.

## E-33 Lidar signal lost

Symptoms: status error, position jumping 2 to 3 cells between readings.

Fix:
1. Press the emergency stop.
2. Reseat the lidar cable connector. Replace the lidar cable harness (SP-1006) if the pins are bent.

## E-42 Wheel drive fault

Symptoms: robot stopped, position unchanged, battery draining about 3x faster. Firmware 2.0 also raises E-42 when the wheel encoder signal is lost.

Fix:
1. Press the emergency stop.
2. Reseat the wheel encoder cable at the drive module. This fixes most E-42 events on the AMR-200.
3. If E-42 returns, replace the encoder cable (SP-1004), then the motor controller board (SP-1003).
4. Replace the wheel motor assembly (SP-1002) only if the steps above fail. Do not follow the AMR-100 practice of replacing the motor first.

## E-57 Localization drift

Symptoms: the position jumps by more than 3 cells in one reading while the robot keeps moving.

Fix:
1. Stop the robot from the dashboard.
2. Follow the E-57 troubleshooting guide: relocalize the robot and check that the map was converted for firmware 2.0.

## E-60 Communication lost

Symptoms: no telemetry for about 10 readings, then E-60 with status stopped.

Fix:
1. Check the Wi-Fi dead zone near aisle 7.
2. If E-60 happens elsewhere, check the Wi-Fi antenna module (SP-1016).
