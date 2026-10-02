# Micronova Agua IOT (hubcasale fork)

> **Fork of [vincentwolsink/home_assistant_micronova_agua_iot](https://github.com/vincentwolsink/home_assistant_micronova_agua_iot)**
> with support for the Nobis Polygon boiler (boiler/puffer registers, weekly chrono programs, Italian translation).
> It installs as a **separate integration** (domain `aguaiot_hubcasale`) so it can live next to the original one.
> Remove the original *Micronova Agua IOT* entry before adding this one, otherwise entity ids get a `_2` suffix.

[![GitHub Release][releases-shield]][releases]
[![Maintainer][maintainer-shield]][maintainer]
[![HACS Custom][hacs-shield]][hacs-url]

Home Assistant integration for controlling heating devices (pellet stoves) connected via the Agua IOT platform of Micronova.

Supports the following vendors (mobile apps):
* Alfaplam
* APP-O BIOEN
* Boreal Home
* Bronpi Home
* Darwin Evolution
* Easy Connect
* Easy Connect Plus
* Easy Connect Poêle
* Elcofire Pellet Home
* Elfire Wifi
* EOSS WIFI
* EvaCalòr - PuntoFuoco
* Fontana Forni
* Fonte Flamme contrôle 1
* Globe-fire
* GO HEAT
* Jolly Mec Wi Fi
* Karmek Wifi
* Klover Home
* LAMINOX Remote Control (2.0)
* Lorflam Home
* Moretti design
* My Corisit
* MyPiazzetta
* MySuperior
* Nina
* Nobis-Fi
* Nordic Fire 2.0
* Ravelli Wi-Fi
* Stufe a pellet Italia
* Thermoflux
* Total Control 3.0 (Extraflame)
* TS Smart
* Wi-Phire

Vendor apps **NOT** compatible (using a different platform or abstraction layer):
* Ravelli Smart Wi-Fi
* Total Control 2.0/1.x

## Screenshots
<img width="671" alt="micronova_screenshot1" src="https://github.com/vincentwolsink/home_assistant_micronova_agua_iot/assets/1639734/4c646550-637d-4e20-bc64-a6977bfee3af">
<img width="330" alt="micronova_screenshot3" src="https://github.com/vincentwolsink/home_assistant_micronova_agua_iot/assets/1639734/3a06b135-eaee-4ff2-94e4-c3da268fb7a9">

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=hubcasale&repository=home_assistant_micronova_agua_iot_hubcasale&category=integration)

Or folow these steps:
1. Install [HACS](https://hacs.xyz/) if you haven't already
2. Install the plugin via HACS (Micronova Agua IOT)
3. Add the integration through the home assistant configuration flow

## Nobis Polygon and boilers with puffer / DHW tank
Extra registers exposed by water boilers (boiler and puffer temperatures, set points, three-way valve,
external thermostat contacts, flow switch, sleep mode) and the **weekly chrono programs** are supported.
See [docs/CHRONO.md](docs/CHRONO.md) for the chrono entities and the `aguaiot_hubcasale.set_chrono_program` service.

## Local Bluetooth mode

This integration now includes an experimental `Bluetooth` connection mode for Micronova stoves equipped with a local BLE module (for example the Micronova / Navel `T009_*` module seen by Home Assistant).

You can enable this mode via the integration options after setup.

For more information see [BLUETOOTH](docs/BLUETOOTH.md).

## Credits

Some parts of the code are based on [py-agua-iot](https://github.com/fredericvl/py-agua-iot)

## Related

For local stove control with custom hardware on the stove bus, take a look at one of these projects.
* https://esphome.io/components/micronova.html
* https://github.com/eni23/micronova-controller
* https://github.com/fabrizioromanelli/Pellet-Stove-Control
* https://github.com/philibertc/micronova_controller
* https://github.com/Shad107/OpenXtraflame

[releases-shield]: https://img.shields.io/github/v/release/hubcasale/home_assistant_micronova_agua_iot_hubcasale.svg?style=for-the-badge
[releases]: https://github.com/hubcasale/home_assistant_micronova_agua_iot_hubcasale/releases
[maintainer-shield]: https://img.shields.io/badge/maintainer-vincentwolsink-blue.svg?style=for-the-badge
[maintainer]: https://github.com/vincentwolsink
[hacs-shield]: https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge
[hacs-url]: https://github.com/hubcasale/home_assistant_micronova_agua_iot_hubcasale
