---
doc_id: IR-2025-047
doc_type: incident_report
robot_model: AMR-100
firmware: 1.4
error_code: E10
last_updated: 2025-05-21
---

# Incident Report IR-2025-047: Two Robots Stopped with Empty Batteries

## Summary

On 6 May 2025, AMR-100 robots 1 and 2 both stopped with E10 during the early shift, 40 minutes apart. Both batteries were healthy. The cause was a skipped charge cycle: the charging stations had been switched off overnight.

## What happened

1. 5 May, 22:00: during cleaning, the night crew switched off the power strip that feeds the charging stations in aisle 1 and did not switch it back on.
2. 6 May, 06:00: the robots started the early shift with 30 to 40% battery instead of 100%.
3. 07:10: robot 2 stopped in aisle 4 with E10 at 9% battery. The telemetry showed a slow, steady drop of about 0.5% per reading, which is normal consumption.
4. 07:50: robot 1 stopped with E10 in aisle 2. By the time staff reached it, its battery was at 4%.
5. 08:05: the power strip was switched back on. Robot 2 was sent to the charger with Send to charger. Robot 1 was below the 5% auto-dock limit and was towed to the charger with manual recovery.
6. 10:30: both robots were back in service.

## Root cause

A skipped charge cycle. The battery packs were not degraded: the battery health test showed 92% and 94% capacity.

## How to tell the two E10 causes apart

1. A slow, steady drop (about 0.5% per reading) before the stop means a skipped charge cycle. Check the chargers.
2. A fast drop (5% or more per reading) means a degraded cell. Replace the battery pack.

## What fixed it

Switching the chargers back on and recharging the robots. No parts were replaced.

## Lessons learned

1. The charger power strip now has a cover and a "Do not switch off" label.
2. The dashboard now alerts the shift lead if a robot starts a shift below 80% battery.
3. Do not order a new battery pack for E10 before checking how fast the battery fell.
