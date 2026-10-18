---
doc_id: MS-200
doc_type: maintenance_schedule
robot_model: AMR-200
firmware: 2.0
last_updated: 2025-10-30
---

# AMR-200 Maintenance Schedule (Firmware 2.0)

This schedule lists the preventive maintenance for AMR-200 robots running firmware 2.0.

## Daily checks

1. Wipe the lidar window with a dry microfibre cloth.
2. Check both emergency stop buttons.
3. Check the dashboard for robots with error codes from the previous shift.

## Weekly checks

1. Clean the charging contacts on the robot and on the charging station.
2. Check that auto-dock completes without retries. Repeated retries point to dirty or bent contact plates (SP-1014).
3. Remove debris from the wheels.

## Monthly checks

1. Check the wheel encoder cable connectors on both drive modules, and push each connector in until it clicks. A loose encoder connector is the most common cause of E-42 on the AMR-200.
2. Check the lidar cable connector on the sensor mast.
3. Check the map version on the dashboard. It must be a converted firmware 2.0 map, with a version starting with v2.

## Every 6 months

1. Replace the drive wheel tyres (SP-1012) if the tread is below 3 mm.
2. Run the battery health test from the dashboard.
3. Inspect the motor controller board for dust and clean it with dry air.

## Yearly

1. Replace the wheel encoder cables (SP-1004) as a precaution.
2. Replace the lidar cable harness (SP-1006).
3. Have the vendor inspect the wheel motors (SP-1002). The AMR-200 uses brushless motors, so there are no brushes to check.

## After a firmware update

1. Convert the site map with the map conversion tool before releasing the robot.
2. Relocalize the robot at the charger.
3. Watch the first 50 readings for position jumps (E-57).

## Notes

- Battery packs (SP-1010) are replaced when the health test shows less than 70% capacity.
- Check part stock in the ERP two weeks before planned work.
