---
doc_id: OP-01
doc_type: operating_procedure
robot_model: all
firmware: all
last_updated: 2025-04-07
---

# Operating Procedure: Emergency Stop

## Purpose

How to stop a robot immediately and how to restart it safely afterwards. This procedure applies to all robot models.

## When to use the emergency stop

- A person or a vehicle is in danger.
- You need to touch the robot, its wheels or its sensor mast.
- A troubleshooting guide tells you to cut motor power.

## Stopping the robot

1. Press the red emergency stop button on either side of the robot. It locks in the pressed position.
2. The drive motors lose power at once and the brakes engage.
3. The dashboard shows the robot as stopped within a few seconds. If the robot is in the Wi-Fi dead zone near aisle 7, the dashboard may not update.

## Before restarting

1. Make sure the cause of the stop has been removed and that no one is in the robot's path.
2. Make sure all covers on the robot are closed.

## Restarting the robot

1. Twist the emergency stop button clockwise until it pops out.
2. On the dashboard, select the robot and press **Reset**. The robot runs a short self-test of about 10 seconds.
3. Press **Resume**. The robot continues its last task.
4. If the robot reports an error code after the self-test, look up the code in the error code reference for its model.

## Things you must not do

1. Do not switch the robot off and on while the emergency stop is pressed. Power-cycling clears the error history that technicians need.
2. Do not push a robot while its brakes are engaged. Use manual recovery (OP-03) to release the brakes first.
3. Do not cover or tape over the emergency stop button.

## Reporting

Every emergency stop caused by a fault, rather than by a person stepping into the robot's path, should be followed by a maintenance notification (OP-04). Include the error code and the time of the stop.
