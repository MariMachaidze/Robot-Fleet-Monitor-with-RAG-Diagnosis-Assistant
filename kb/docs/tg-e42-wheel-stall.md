---
doc_id: TG-E42
doc_type: troubleshooting_guide
robot_model: all
firmware: all
error_code: E42
last_updated: 2025-12-01
---

# Troubleshooting Guide: Wheel Motor Stall (E42)

## Symptoms

- Status stopped with error code E42.
- The position stays the same across readings.
- The battery drops about 3x faster than normal (around 1.5% per reading instead of 0.5%), because the stalled motor keeps drawing current.

## First steps (both models)

1. Press the emergency stop to cut power to the drive motors (OP-01). This also stops the extra battery drain.
2. Check that nothing is jammed in the wheels, such as shrink wrap or a strap.
3. Note the robot model. **The fix for E42 is different on the AMR-100 and the AMR-200.**

## Fix for AMR-100

The AMR-100 uses a brushed wheel motor. Worn brushes are the usual cause of a stall, and the motor cannot be repaired on site.

1. Do not reset and restart the motor. Restarting a stalled brushed motor can burn the windings.
2. Replace the wheel motor assembly (SP-1001).
3. Check spare-part stock in the ERP before you plan the repair. If the motor is out of stock, write the lead time in the maintenance notification and set the priority to high (OP-04).
4. After the replacement, run the robot for 10 minutes and confirm that the battery drain is back to normal.

## Fix for AMR-200

On the AMR-200 most E42 events come from a loose wheel encoder cable, not from the motor itself.

1. Open the drive module cover and reseat the wheel encoder cable connector.
2. Release the emergency stop and reset the motor controller from the dashboard.
3. If E42 returns, replace the encoder cable (SP-1004).
4. If it still returns, replace the motor controller board (SP-1003).
5. Replace the wheel motor assembly (SP-1002) only when all of the steps above have failed.

## Lessons from past incidents

- AMR-100, March 2025: a robot was out of service for 12 days because no wheel motor was in stock (IR-2025-031).
- AMR-200, November 2025: a technician drafted a motor replacement, but reseating the encoder cable fixed the fault in 20 minutes (IR-2025-104).
