### Heltec HT-CT62 hardware configuration

from machine import Pin, ADC
import time

class DeviceConfig:
    config = {}

    def power_up(freakwan):
        return

    def get_battery_microvolts():
        return 4200000

    # Pin configuration for the SX1262.
    config['sx1262'] = {
        'busy': 4,
        'miso': 6,
        'mosi': 7,
        'clock': 10,
        'chipselect': 8,
        'reset': 5,
        'dio': 3,
    }
