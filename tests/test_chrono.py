"""Tests for the weekly chrono programs (Nobis Polygon and similar)."""

import asyncio
import importlib.util
import os
import sys
from datetime import time

import pytest

from tests.helpers import build_device_from_fixture

_CHRONO_PATH = os.path.join(
    os.path.dirname(__file__), "..", "custom_components", "aguaiot", "chrono.py"
)
_spec = importlib.util.spec_from_file_location("aguaiot_chrono", _CHRONO_PATH)
chrono = importlib.util.module_from_spec(_spec)
sys.modules["aguaiot_chrono"] = chrono
_spec.loader.exec_module(chrono)


@pytest.fixture
def polygon(aguaiot_mock, fixture_data):
    """The Polygon device plus the list of raw write requests it receives."""
    writes = []

    async def fake_request_writing(device, items):
        writes.append(dict(items))

    aguaiot_mock._request_writing = fake_request_writing
    device = build_device_from_fixture(
        aguaiot_mock, "nobis_polygon", fixture_data["nobis_polygon"]
    )
    return device, writes


class TestTimeConversion:
    def test_unset_value_is_none(self):
        assert chrono.raw_to_time(144) is None
        assert chrono.raw_to_time(None) is None
        assert chrono.raw_to_time("garbage") is None

    def test_raw_to_time(self):
        assert chrono.raw_to_time(0) == time(0, 0)
        assert chrono.raw_to_time(3) == time(0, 30)
        assert chrono.raw_to_time(30) == time(5, 0)
        assert chrono.raw_to_time(143) == time(23, 50)

    def test_time_to_raw_rounds_down_to_the_step(self):
        assert chrono.time_to_raw(time(5, 0)) == 30
        assert chrono.time_to_raw(time(0, 30)) == 3
        assert chrono.time_to_raw(time(0, 35)) == 3
        assert chrono.time_to_raw(time(23, 59)) == 143

    def test_round_trip(self):
        for raw in range(0, 144):
            assert chrono.time_to_raw(chrono.raw_to_time(raw)) == raw


class TestBuildProgramItems:
    def test_full_program(self):
        items = chrono.build_program_items(
            1,
            start=time(5, 0),
            stop=time(0, 30),
            days=["monday", "sunday"],
            water_temperature=65,
            boiler_temperature=50,
            acs=True,
        )
        assert items["chrono_p1_start_set"] == 30
        assert items["chrono_p1_stop_set"] == 3
        assert items["chrono_p1_day_monday_set"] == 1
        assert items["chrono_p1_day_sunday_set"] == 1
        assert items["chrono_p1_day_tuesday_set"] == 0
        assert items["chrono_p1_t_water_set"] == 65
        assert items["chrono_p1_t_boiler_set"] == 50
        assert items["chrono_p1_acs_set"] == chrono.CHRONO_ACS_ON
        assert len([k for k in items if "_day_" in k]) == 7

    def test_partial_program_only_touches_given_values(self):
        items = chrono.build_program_items(2, start=time(6, 10))
        assert items == {"chrono_p2_start_set": 37}

    def test_acs_off(self):
        items = chrono.build_program_items(3, acs=False)
        assert items == {"chrono_p3_acs_set": chrono.CHRONO_ACS_OFF}

    def test_invalid_program(self):
        with pytest.raises(ValueError):
            chrono.build_program_items(5, start=time(1, 0))

    def test_invalid_day(self):
        with pytest.raises(ValueError):
            chrono.build_program_items(1, days=["funday"])


class TestPolygonRegisters:
    def test_chrono_registers_exist(self, polygon):
        device, _ = polygon
        for program in chrono.CHRONO_PROGRAMS:
            assert chrono.start_key(program) in device.registers
            assert chrono.stop_key(program) in device.registers
            assert chrono.acs_key(program) in device.registers
            for day in chrono.CHRONO_DAYS:
                assert chrono.day_key(program, day) in device.registers
        assert chrono.CHRONO_WEEK_ENABLE_KEY in device.registers

    def test_unset_times_read_as_none(self, polygon):
        device, _ = polygon
        assert device.get_register_value("chrono_p1_start_set") == 144
        assert chrono.raw_to_time(device.get_register_value("chrono_p1_start_set")) is None

    def test_enable_flags_follow_the_device(self, polygon):
        device, _ = polygon
        # Boiler/puffer registers the integration did not know before
        assert device.get_register_enabled("temp_h2o_boiler2_get") is True
        assert device.get_register_enabled("temp_h2o_boiler_set") is True
        # Puffer probes are disabled while the boiler is set to scheme 01
        assert device.get_register_enabled("temp_h2o_puffer_h_get") is False
        assert device.get_register_enabled("ext_puffertherm_get") is False
        # Chrono temperatures are enabled, the per-program ACS flag is not
        assert device.get_register_enabled("chrono_p1_t_water_set") is True
        assert device.get_register_enabled("chrono_p1_acs_set") is False
        # Weekday flags have no enable register: always available
        assert device.get_register_enabled("chrono_p1_day_monday_set") is True

    def test_boiler_and_valve_values(self, polygon):
        device, _ = polygon
        assert device.get_register_value("temp_h2o_boiler2_get") == 64.0
        assert device.get_register_value("temp_h2o_boiler_set") == 45
        assert device.get_register_value_description("vie_3_get", language="ENG") == "RISC."


class TestWritingPrograms:
    def run(self, coro):
        return asyncio.run(coro)

    def test_program_is_written_in_a_single_request(self, polygon):
        device, writes = polygon
        items = chrono.build_program_items(
            1,
            start=time(5, 0),
            stop=time(0, 30),
            days=["monday", "tuesday"],
            water_temperature=65,
            boiler_temperature=50,
            acs=True,
        )
        self.run(device.set_register_values(items))

        assert len(writes) == 1
        assert writes[0]["chrono_p1_start_set"] == 30
        assert writes[0]["chrono_p1_stop_set"] == 3
        # Weekday flags are bits of one word: the written value is the bit mask
        assert writes[0]["chrono_p1_day_monday_set"] == 1
        assert writes[0]["chrono_p1_day_tuesday_set"] == 2
        assert writes[0]["chrono_p1_day_wednesday_set"] == 0
        assert writes[0]["chrono_p1_acs_set"] == 2

    def test_out_of_range_temperature_is_rejected(self, polygon):
        device, writes = polygon
        items = chrono.build_program_items(1, water_temperature=80)  # max is 75
        with pytest.raises(ValueError):
            self.run(device.set_register_values(items))
        assert writes == []

    def test_weekly_chrono_switch(self, polygon):
        device, writes = polygon
        self.run(device.set_register_value("chrono_week_enable_set", 1))
        assert writes == [{"chrono_week_enable_set": 1}]
