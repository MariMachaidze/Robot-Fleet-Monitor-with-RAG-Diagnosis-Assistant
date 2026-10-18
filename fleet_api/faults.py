"""Catalog of injectable faults: the error code each one produces and its true cause.

fleet_api uses it to validate POST /faults/inject and fill in the true cause. The
simulator (Stage 2) will use the same catalog to know how each fault behaves, so the
fault names, codes and causes are defined in exactly one place.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class FaultSpec:
    error_code: str
    true_cause: str
    firmware_only: str | None = None  # the fault can only occur on this firmware version


FAULTS: dict[str, FaultSpec] = {
    "battery_drain": FaultSpec("E10", "degraded cell or skipped charge cycle"),
    "blocked_path": FaultSpec("E21", "obstacle in the aisle"),
    "lidar_dropout": FaultSpec("E33", "loose lidar cable"),
    "wheel_stall": FaultSpec("E42", "wheel motor stalled"),
    "localization_drift": FaultSpec(
        "E57", "map mismatch after the firmware 2.0 update", firmware_only="2.0"
    ),
    "comms_loss": FaultSpec("E60", "Wi-Fi dead zone near aisle 7"),
}
