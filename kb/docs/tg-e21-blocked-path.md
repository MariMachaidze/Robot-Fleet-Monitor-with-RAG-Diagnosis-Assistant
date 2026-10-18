---
doc_id: TG-E21
doc_type: troubleshooting_guide
robot_model: all
firmware: all
error_code: E21
last_updated: 2024-09-15
---

# Troubleshooting Guide: Blocked Path (E21)

## Symptoms

- The robot's position does not change for 5 or more telemetry readings.
- During the first readings the status still says moving, because the robot is waiting for the path to clear. After about 5 readings it changes to stopped with error code E21.
- The battery drains at the normal rate. This separates E21 from a wheel motor stall (E42), where the battery drains about 3x faster.

## Likely cause

An obstacle in the aisle: a pallet left in the driving lane, fallen shrink wrap, or a person standing in the robot's safety field.

## Steps to clear the path

1. Check the robot's last position on the dashboard and identify the aisle.
2. Walk to the robot. Do not reach into its path while the status is still moving. Press the emergency stop first if you need to get close (OP-01).
3. Remove the obstacle. Move large pallets with a pallet jack instead of pushing them by hand.
4. Release the emergency stop if you pressed it.
5. Press **Resume** on the dashboard. The robot plans a new route and continues.
6. Watch the next few readings. The position should start changing again.

## If the robot does not resume

1. Check that the bumper safety strip is not pressed in or damaged.
2. Check that the lidar window is clean. Dirt on the window can look like an obstacle to the robot.
3. If the robot still reports E21 with a clear aisle, use manual recovery (OP-03) to move it to the maintenance bay, and create a maintenance notification (OP-04).

## Prevention

- Keep driving lanes marked and free of pallets.
- If E21 repeats in the same aisle, report the location to the shift lead so the aisle layout can be reviewed.
- Remind staff that standing in front of a waiting robot keeps it blocked.
