---
doc_id: OP-03
doc_type: operating_procedure
robot_model: all
firmware: all
last_updated: 2024-11-05
---

# Operating Procedure: Manual Recovery

## Purpose

How to move a robot that cannot drive by itself, for example after a wheel stall, an empty battery or a communication loss. This procedure applies to all models.

## Before you start

1. Press the emergency stop on the robot (OP-01).
2. Check the error code on the dashboard and note it for the maintenance notification.
3. Make sure the route to the destination, usually the maintenance bay or the charger, is clear.

## Releasing the brakes

1. Open the small service flap on the rear of the robot.
2. Hold the yellow brake release switch for 3 seconds. A beep confirms that the brakes are released.
3. The brakes engage again automatically after 5 minutes, or when you press the switch again.

## Moving an AMR-100

1. One person can push an AMR-100 on a flat floor. Push from the rear handle only.
2. Walk slowly and stop before ramps or floor joints.

## Moving an AMR-200

1. The AMR-200 is much heavier. Use tow mode: connect the tow bar to the front hook and pull with a pallet jack, or have two people push.
2. Never push an AMR-200 alone.

## Driving with the pendant

If the drive motors still work, for example after a communication loss, you can connect the handheld pendant and drive the robot slowly instead of pushing it. Do not use the pendant on a robot with a wheel motor stall (E42), because the stalled motor must not be powered.

## After the move

1. Engage the brakes again with the brake release switch.
2. If you moved the robot to a charger, press **Send to charger** on the dashboard so it docks the last few centimetres by itself. On a seperate charger without auto-dock, connect the charging cable by hand.
3. Create a maintenance notification (OP-04) with the robot id, the error code and the place where the robot stopped.
