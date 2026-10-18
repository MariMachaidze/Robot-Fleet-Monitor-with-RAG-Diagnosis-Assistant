---
doc_id: TG-E10
doc_type: troubleshooting_guide
robot_model: all
firmware: all
error_code: E10
last_updated: 2025-06-02
---

# Troubleshooting Guide: Battery Drain (E10)

## When to use this guide

Use this guide when a robot reports E10, or when its battery drops below 10% and it stops. It applies to AMR-100 and AMR-200 robots.

## Symptoms

- Status stopped with error code E10.
- Battery below 10% in the latest telemetry reading.
- In normal operation the battery falls about 0.5% per telemetry reading. If the readings before the stop show drops of 5% or more per reading, the pack is degrading.

## Likely causes

1. **Degraded battery cell.** The pack can no longer hold its charge, so the battery falls very quickly while the robot drives.
2. **Skipped charge cycle.** The robot missed its scheduled charge, for example because the chargers were switched off, and then ran down at the normal rate.

## Diagnosis steps

1. Open the robot's recent telemetry and look at how fast the battery fell.
2. Fast drop (5% or more per reading): treat it as a degraded cell.
3. Slow, steady drop (about 0.5% per reading): treat it as a skipped charge cycle and check the charging log for the last shift.

## Fix: return the robot to the charger

1. If the battery is above 5%, select the robot on the fleet dashboard and press **Send to charger**. The robot docks by itself (auto-dock, available since firmware 1.4).
2. If the battery is 5% or lower, the robot may not reach the charger. Use the manual recovery procedure (OP-03) and tow it to the charger.
3. Do not drive the robot onto the charger with the handheld pendant. The old pendant docking procedure (OP-02, 2023) is outdated, and misaligned docking damages the charging contact plates.

## Fix: degraded cell

1. Let the robot charge to 100% and watch the next shift. If it drains fast again, the pack must be replaced.
2. Replace the battery pack: SP-1009 for AMR-100, SP-1010 for AMR-200.
3. Check spare-part stock in the ERP and create a maintenance notification (OP-04). Battery packs are not always in stock, so check before you plan the repair.

## Escalation

If a new battery pack also drains quickly, escalate to the vendor. The charging electronics may be at fault.
