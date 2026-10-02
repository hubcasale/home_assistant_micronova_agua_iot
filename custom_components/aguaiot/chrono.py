"""Weekly chrono (timer) programs of Micronova devices.

Some devices (for example the Nobis Polygon) expose up to four weekly programs
``chrono_p1 .. chrono_p4``. Each program has a start and stop time, one enable
flag per weekday, optional water/boiler set temperatures and an ACS flag.

Times are stored as a number of ``CHRONO_STEP_MINUTES`` minutes since midnight;
``CHRONO_UNSET`` means "no time set" (the app shows ``--:--``).

This module has no Home Assistant dependency so it can be unit tested alone.
"""

from __future__ import annotations

from datetime import time

CHRONO_PROGRAMS = (1, 2, 3, 4)
CHRONO_DAYS = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)
CHRONO_STEP_MINUTES = 10
CHRONO_UNSET = 24 * 60 // CHRONO_STEP_MINUTES  # 144

CHRONO_WEEK_ENABLE_KEY = "chrono_week_enable_set"

# Raw value of the "ACS" register of a program
CHRONO_ACS_OFF = 1
CHRONO_ACS_ON = 2


def start_key(program: int) -> str:
    return f"chrono_p{program}_start_set"


def stop_key(program: int) -> str:
    return f"chrono_p{program}_stop_set"


def day_key(program: int, day: str) -> str:
    return f"chrono_p{program}_day_{day}_set"


def water_temp_key(program: int) -> str:
    return f"chrono_p{program}_t_water_set"


def boiler_temp_key(program: int) -> str:
    return f"chrono_p{program}_t_boiler_set"


def acs_key(program: int) -> str:
    return f"chrono_p{program}_acs_set"


def raw_to_time(raw) -> time | None:
    """Convert a raw register value to a time of day (None if not set)."""
    if raw is None:
        return None
    try:
        raw = int(raw)
    except (TypeError, ValueError):
        return None
    if raw < 0 or raw >= CHRONO_UNSET:
        return None
    minutes = raw * CHRONO_STEP_MINUTES
    return time(minutes // 60, minutes % 60)


def time_to_raw(value: time) -> int:
    """Convert a time of day to a raw register value (rounded down to the step)."""
    minutes = value.hour * 60 + value.minute
    return minutes // CHRONO_STEP_MINUTES


def build_program_items(
    program: int,
    *,
    start: time | None = None,
    stop: time | None = None,
    days=None,
    water_temperature: float | None = None,
    boiler_temperature: float | None = None,
    acs: bool | None = None,
) -> dict[str, int | float]:
    """Return the register values needed to (re)program one chrono program.

    Only the parameters that are not None are included, so a program can be
    changed partially. ``days`` is an iterable of weekday names: the listed
    days are enabled and all the others are disabled.
    """
    if program not in CHRONO_PROGRAMS:
        raise ValueError(f"Program must be one of {CHRONO_PROGRAMS}: {program}")

    items: dict[str, int | float] = {}

    if start is not None:
        items[start_key(program)] = time_to_raw(start)
    if stop is not None:
        items[stop_key(program)] = time_to_raw(stop)

    if days is not None:
        selected = {d.lower() for d in days}
        unknown = selected - set(CHRONO_DAYS)
        if unknown:
            raise ValueError(f"Unknown days: {sorted(unknown)}")
        for day in CHRONO_DAYS:
            items[day_key(program, day)] = 1 if day in selected else 0

    if water_temperature is not None:
        items[water_temp_key(program)] = water_temperature
    if boiler_temperature is not None:
        items[boiler_temp_key(program)] = boiler_temperature
    if acs is not None:
        items[acs_key(program)] = CHRONO_ACS_ON if acs else CHRONO_ACS_OFF

    return items
