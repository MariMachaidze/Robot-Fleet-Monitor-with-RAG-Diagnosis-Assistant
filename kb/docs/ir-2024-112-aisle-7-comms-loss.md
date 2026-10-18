---
doc_id: IR-2024-112
doc_type: incident_report
robot_model: AMR-100
firmware: 1.4
error_code: E60
last_updated: 2024-12-09
---

# Incident Report IR-2024-112: Robots Stopping in Aisle 7

## Summary

Between 18 and 29 November 2024, AMR-100 robot 2 stopped six times in aisle 7. Each time it sent no telemetry for a while and then reported E60. The average downtime was 25 minutes per event.

## Timeline

1. 18 Nov: first event. The dashboard showed robot 2 as moving for 20 minutes while it was actually standing still in aisle 7. The operator noticed only when a pallet delivery was late.
2. 19 to 27 Nov: five more events, all in aisle 7.
3. 28 Nov: IT ran a Wi-Fi survey and found a dead zone near aisle 7. The new high racking installed in October blocks the signal from acess point AP-07.
4. 29 Nov: aisle 7 was marked as a no-go zone for robots.

## Root cause

A Wi-Fi dead zone near aisle 7, caused by the new racking. The robot itself was healthy. Firmware 1.4 stops a robot when it loses the connection, which is the correct and safe behavior.

## What fixed it

1. Short term: aisle 7 was closed to robots, and pallets for aisle 7 are now moved by forklift.
2. Long term: IT will install an additional access point at the end of aisle 7, planned for the first quarter of 2025.

## Lessons learned

1. The dashboard showed a stale status. Operators must check the timestamp of the latest reading, not only the status.
2. While a robot is silent, its position and battery are unknown. Do not report the last values as if they were current.
3. Repeated E60 events in one place point to the site network, not to the robot. Do not replace the Wi-Fi antenna module before checking where the robot stopped.
4. Robots that stop in a dead zone must be moved out by hand with manual recovery (OP-03), because they cannot receive commands.
