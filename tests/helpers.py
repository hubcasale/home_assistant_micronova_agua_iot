import importlib.util
import os
import sys

# Load aguaiot.py directly to avoid __init__.py import cascade
_AGUAIOT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "custom_components", "aguaiot_hubcasale", "aguaiot.py"
)
_spec = importlib.util.spec_from_file_location("aguaiot_module", _AGUAIOT_PATH)
_aguaiot_module = importlib.util.module_from_spec(_spec)
sys.modules["aguaiot_module"] = _aguaiot_module
_spec.loader.exec_module(_aguaiot_module)

Device = _aguaiot_module.Device
aguaiot = _aguaiot_module.aguaiot
AguaIOTError = _aguaiot_module.AguaIOTError
AguaIOTUnauthorized = _aguaiot_module.AguaIOTUnauthorized


def compute_information_dict(register_map):
    """Build information dict from fixture register map.

    Registers may share an offset using different masks (bit packing).
    Value_raw values are already masked - so we need to combine them
    bitwise into the full word value.
    """
    info = {}
    for reg in register_map.values():
        offset = reg.get("offset")
        value_raw = reg.get("value_raw", "0")
        mask = reg.get("mask", 65535)
        if offset is not None:
            raw_int = int(value_raw)
            existing = info.get(offset)
            # The raw value already has mask applied, so place it
            # back into the word at the mask's bit positions.
            # We need to find a value where existing_mask bits = existing_value
            # and new_mask bits = raw_int.
            if existing is not None:
                # Check if they can coexist (non-overlapping masks or consistent values)
                if existing & mask == raw_int:
                    # Already consistent
                    continue
                # Bitwise OR them - each value should occupy non-overlapping mask bits
                info[offset] = existing | raw_int
            else:
                info[offset] = raw_int
    return info


def build_device_from_fixture(aguaiot_instance, fixture_name, register_map):
    raw_data = compute_information_dict(register_map)
    device = Device(
        id=1,
        id_device=fixture_name,
        id_product=1,
        product_serial=f"SERIAL-{fixture_name}",
        name=fixture_name,
        is_online=True,
        name_product=fixture_name,
        id_registers_map=1,
        aguaiot=aguaiot_instance,
        device_info={},
        register_map=register_map,
    )
    device._Device__register_dict = device._Device__build_register_dict(raw_data)
    return device
