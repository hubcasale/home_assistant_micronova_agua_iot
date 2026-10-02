# Weekly chrono programs (Nobis Polygon and similar)

Some devices expose up to four weekly timer programs (`chrono_p1` … `chrono_p4`).
Each program has a start and a stop time, one flag per weekday, optional water and
boiler set temperatures and a DHW (ACS) flag. The integration creates entities for
every register the device reports as enabled, so you only see what your model supports.

## Entities

| Entity | What it does |
|---|---|
| `switch.<device>_weekly_chrono` | Turns the whole weekly chrono on or off |
| `time.<device>_chrono_p<N>_start` / `_stop` | Start and stop time of program N (steps of 10 minutes) |
| `switch.<device>_chrono_p<N>_<weekday>` | Enables program N on that weekday |
| `number.<device>_chrono_p<N>_water_setpoint` / `_boiler_setpoint` | Set temperatures used by program N |
| `switch.<device>_chrono_p<N>_acs` | DHW production during program N (if the device enables it) |

They are in the *Configuration* section of the device page. A time that is not set is
shown as `unknown` (the device stores `144`, shown as `--:--` in the vendor app).

## Service `aguaiot_hubcasale.set_chrono_program`

Programs one chrono program in a **single request** (much faster and safer than writing
the 10+ entities one by one). Only the fields you provide are changed; if you provide
`days`, the listed days are enabled and all the others are disabled.

```yaml
# Run the boiler from 05:00 to 00:30, every day: it will not start between 00:30 and 05:00
action: aguaiot_hubcasale.set_chrono_program
target:
  entity_id: climate.casale_water
data:
  program: 1
  start: "05:00:00"
  stop: "00:30:00"
  days: [monday, tuesday, wednesday, thursday, friday, saturday, sunday]
  weekly_enabled: true
```

## Notes

* **Check the time unit once.** The code assumes one step = 10 minutes (so the raw value
  `30` is 05:00). Set a program time in the vendor app and confirm Home Assistant shows
  the same time before relying on it.
* The chrono registers are stored in the device EEPROM. Write them when you really change
  the schedule, not every few minutes from an automation.
* A program that crosses midnight (start later than stop, like the example) is accepted
  by the vendor app; confirm the behaviour on your model before trusting it overnight.
