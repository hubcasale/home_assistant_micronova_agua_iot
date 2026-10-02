import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .aguaiot import AguaIOTError
from .const import DOMAIN, SWITCHES, translation_key

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = config_entry.runtime_data
    agua = coordinator.agua

    switches = []
    for device in agua.devices:
        for switch in SWITCHES:
            if switch.key in device.registers and device.get_register_enabled(
                switch.key
            ):
                switches.append(AguaIOTHeatingSwitch(coordinator, device, switch))

    async_add_entities(switches, True)


class AguaIOTHeatingSwitch(CoordinatorEntity, SwitchEntity):
    """Switch entity"""

    _attr_has_entity_name = True

    def __init__(self, coordinator, device, description):
        """Initialize the thermostat."""
        super().__init__(coordinator)
        self._device = device
        self.entity_description = description
        self._attr_translation_key = translation_key(description)

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._device.id_device}_{self.entity_description.key}"

    @property
    def device_info(self):
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device.id_device)},
            name=self._device.name,
            manufacturer="Micronova",
            model=self._device.name_product,
        )

    @property
    def is_on(self):
        """Return the state of the sensor."""
        value = self._device.get_register_value(self.entity_description.key)
        value_on = getattr(self.entity_description, "value_on", 1)
        if value_on == 1:
            return bool(value)
        return value == value_on

    async def async_turn_off(self):
        """Turn device off."""
        try:
            await self._device.set_register_value(
                self.entity_description.key,
                getattr(self.entity_description, "value_off", 0),
            )
            await self.coordinator.async_request_refresh()
        except AguaIOTError as err:
            _LOGGER.error(
                "Failed to turn off '%s', error: %s",
                f"{self._device.name} {self.entity_description.name}",
                err,
            )

    async def async_turn_on(self):
        """Turn device on."""
        try:
            await self._device.set_register_value(
                self.entity_description.key,
                getattr(self.entity_description, "value_on", 1),
            )
            await self.coordinator.async_request_refresh()
        except AguaIOTError as err:
            _LOGGER.error(
                "Failed to turn on '%s', error: %s",
                f"{self._device.name} {self.entity_description.name}",
                err,
            )
