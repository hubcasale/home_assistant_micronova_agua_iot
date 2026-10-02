"""Time entities: start/stop of the weekly chrono programs."""

import logging

from homeassistant.components.time import TimeEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .aguaiot import AguaIOTError
from .chrono import CHRONO_UNSET, raw_to_time, time_to_raw
from .const import DOMAIN, TIMES, translation_key

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = config_entry.runtime_data
    agua = coordinator.agua

    times = []
    for device in agua.devices:
        for description in TIMES:
            if description.key in device.registers and device.get_register_enabled(
                description.key
            ):
                times.append(AguaIOTHeatingTime(coordinator, device, description))

    async_add_entities(times, True)


class AguaIOTHeatingTime(CoordinatorEntity, TimeEntity):
    """Start or stop time of a chrono program.

    The device stores the time in steps of 10 minutes; a time that is not set
    is shown as unknown. Use the ``set_chrono_program`` service to change
    several values of a program at once.
    """

    _attr_has_entity_name = True

    def __init__(self, coordinator, device, description):
        super().__init__(coordinator)
        self._device = device
        self.entity_description = description
        self._attr_translation_key = translation_key(description)

    @property
    def unique_id(self):
        return f"{self._device.id_device}_{self.entity_description.key}"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._device.id_device)},
            name=self._device.name,
            manufacturer="Micronova",
            model=self._device.name_product,
        )

    @property
    def native_value(self):
        return raw_to_time(self._device.get_register_value(self.entity_description.key))

    @property
    def extra_state_attributes(self):
        return {
            "raw_value": self._device.get_register_value(self.entity_description.key),
            "unset_raw_value": CHRONO_UNSET,
        }

    async def async_set_value(self, value):
        try:
            await self._device.set_register_value(
                self.entity_description.key, time_to_raw(value)
            )
            await self.coordinator.async_request_refresh()
        except (ValueError, AguaIOTError) as err:
            _LOGGER.error("Failed to set time, error: %s", err)
