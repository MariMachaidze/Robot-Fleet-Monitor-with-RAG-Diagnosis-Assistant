---
doc_id: TG-E33
doc_type: troubleshooting_guide
robot_model: all
firmware: all
error_code: E33
last_updated: 2025-02-11
---

# Troubleshooting Guide: Lidar Dropout (E33)

## Symptoms

- Status error with error code E33.
- The reported position jumps by 2 to 3 cells between readings, although the robot is not driving.
- The robot halts because it can no longer see its surroundings.

## Cause

In almost all cases the lidar cable has worked loose at the connector on the sensor mast. Vibration from uneven floors loosens the connector over time, especially on AMR-100 robots.

## Safety first

1. Press the emergency stop on the robot before you touch the sensor mast (OP-01).
2. Wait until the dashboard shows the robot as stopped.

## Fix

1. Open the sensor mast cover. It has two thumb screws, so no tools are needed.
2. Check the lidar cabel connector. If it is loose, push it in until it clicks and tighten the locking ring by hand.
3. Inspect the cable for kinks, cuts or bent pins.
4. If the cable is damaged, replace the lidar cable harness: SP-1005 for AMR-100, SP-1006 for AMR-200. Check the stock in the ERP first.
5. Close the cover, release the emergency stop and restart the robot from the dashboard.
6. Watch the next readings. The position should be stable again and the error code should clear.

## If E33 comes back

1. If the robot does not recieve a lidar signal even with a new cable, the lidar sensor unit itself may be faulty (SP-1007 for AMR-100, SP-1008 for AMR-200).
2. Lidar sensor units have long lead times. Create a maintenance notification right away (OP-04) and keep the robot out of service.

## Do not confuse with E57

Localization drift (E57, firmware 2.0 only) also shows position jumps. In that case the robot keeps moving, the jump is larger than 3 cells, and the status is not error. See the troubleshooting guide for E57.
