---
doc_id: ECR-100
doc_type: error_code_reference
robot_model: AMR-100
firmware: 1.4
last_updated: 2025-11-03
---

# AMR-100 Error Code Reference

This reference lists the error codes reported by AMR-100 robots running firmware 1.4. The code appears in the error_code field of every telemetry reading and on the fleet dashboard. For detailed help, open the troubleshooting guide for the code.

## E10 – Battery critically low

**Symptoms:** battery below 10% and status stopped. A healthy pack loses about 0.5% per telemetry reading. Drops of 5% or more per reading point to a degraded cell.

**Fix:**
1. Send the robot to the charger from the dashboard.
2. If the battery fell fast, replace the battery pack (SP-1009).

## E21 – Path blocked

**Symptoms:** position unchanged for 5 or more readings, then status stopped. The battery drains at the normal rate.

**Fix:**
1. Walk to the robot and remove the obstacle from the aisle.
2. Press Resume on the dashboard.

## E33 – Lidar signal lost

**Symptoms:** status error, and the reported position jumps by 2 to 3 cells between readings.

**Fix:**
1. Press the emergency stop.
2. Reseat the lidar cable at the sensor mast. Replace the lidar cable harness (SP-1005) if it is damaged.

## E42 – Wheel motor stall

**Symptoms:** position unchanged, status stopped, and the battery falling about 3x faster than normal because the stalled motor still draws current.

**Fix:**
1. Press the emergency stop to cut motor power.
2. Replace the wheel motor assembly (SP-1001). The AMR-100 uses a brushed motor that cannot be repaired on site, and resetting it is not a fix.
3. Check spare-part stock in the ERP before planning the repair.

## E57 – Localization drift

Not raised by firmware 1.4. If an AMR-100 ever reports E57, save the telemetry and escalate to the vendor.

## E60 – Communication lost

**Symptoms:** no telemetry for about 10 readings, then status stopped with E60 when the link returns. The dashboard keeps showing the last known status, so check the timestamp of the latest reading.

**Fix:**
1. Check whether the robot stopped near aisle 7, where there is a known Wi-Fi dead zone.
2. Move the robot with manual recovery (OP-03) and report the location.
