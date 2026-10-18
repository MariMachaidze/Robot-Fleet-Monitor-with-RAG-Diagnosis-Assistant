---
doc_id: TG-E60
doc_type: troubleshooting_guide
robot_model: all
firmware: all
error_code: E60
last_updated: 2025-01-22
---

# Troubleshooting Guide: Communication Loss (E60)

## Symptoms

- No telemetry from the robot for about 10 readings (20 seconds or more).
- The fleet dashboard keeps showing the last known status, often moving, even though the robot has stopped. Always check the timestamp of the latest reading.
- When the link returns, the robot reports status stopped with error code E60.

## Known cause on this site

There is a Wi-Fi dead zone near aisle 7, behind the racking added in 2024. Robots that drive into aisle 7 lose the connection and stop, because a robot halts automatically when it loses the link to the fleet manager.

## Steps

1. Check the last reported position. If the robot was in or near aisle 7, assume that the dead zone is the cause.
2. Walk to the robot. It is stopped and safe to approach, but press the emergency stop before you move it (OP-01).
3. Move the robot out of aisle 7 with manual recovery (OP-03).
4. Release the emergency stop. The robot reconnects and sends telemetry again.
5. Ask the shift lead to keep aisle 7 marked as a no-go zone for robots until the Wi-Fi coverage is fixed.

## If E60 happens outside aisle 7

1. Check that the Wi-Fi antenna on top of the robot is not damaged.
2. Replace the Wi-Fi antenna module if needed (SP-1015 for AMR-100, SP-1016 for AMR-200) and create a maintenance notification (OP-04).
3. If several robots lose the connection at the same time, the problem is the site network, not the robots. Contact IT.

## Do not guess missing data

While a robot is silent, its position, battery and status are unknown. Report them as unknown instead of repeating the last values as if they were current.
