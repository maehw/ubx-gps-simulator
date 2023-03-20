# README

There's a bunch of scripts and tools that allow to communicate with u-blox GPS receivers. However, I was unable to find scripts or tools that simulate the GPS receiver side. This Python script simulates the GPS receiver serial communication and can be used to replace the receiver hardware by running this script.

Its functionality is currently limited to:
* receiving all messages and evaluating their checksums,
* recognizing `CFG` class messages (`0x06`) and replying with an `ACK-ACK`.

# Usage

```
usage: ubx_gps_simulator.py [-h] [-b BAUDRATE] serial_port_name

ubx_gps_simulator.py Run simulated UBX GPX receiver.

positional arguments:
  serial_port_name      Serial port name

optional arguments:
  -h, --help            show this help message and exit
  -b BAUDRATE, --baudrate BAUDRATE
                        Serial baudrate (default: 115200)
```

## Usage example OBS

Example: Debugging the [OpenBikeSensor](https://www.openbikesensor.org/) [firmware](https://github.com/openbikesensor/OpenBikeSensorFirmware) v0.16.765 on an ESP32 development board without any attached hardware.

```
> python3 ubx_gps_simulator.py /dev/tty.usbserial-DEADBEEF

>>> Received VALID message: class 0x06, ID 0x34 w/o payload.
    CFG-RINV (remote inventory). Poll request.
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x064Bk'

>>> Received VALID message: class 0x06, ID 0x04 w/ payload b'\x00\x00\x02\x00' (length: 4).
    CFG-RST (reset receiver/ clear backup data structure command).
      navBbrMask: b'\x00\x00' (hotstart)
      resetMode:  2
      reserved1:  0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x04\x12;'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x0b2\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x0B, ID 0x32 (AID-ALPSRV).
      Rates for 6 I/O targets: b'\x00\x00\x00\x00\x00\x00'
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x0B, ID 0x50 w/o payload.
    AID-ALP (ALP file data transfer to the receiver)
      ALP file data: b''
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x0bPc\x91'

>>> Received VALID message: class 0x0A, ID 0x04 w/o payload.
    MON-VER

>>> Received VALID message: class 0x0A, ID 0x09 w/o payload.
    MON-HW

>>> Received VALID message: class 0x01, ID 0x03 w/o payload.
    NAV-STATUS

>>> Received VALID message: class 0x06, ID 0x24 w/o payload.
    CFG-NAV5
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06$2['

>>> Received VALID message: class 0x06, ID 0x34 w/o payload.
    CFG-RINV (remote inventory). Poll request.
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x064Bk'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01 \x00\x01\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x20 (NAV-TIMEGPS).
      Rates for 6 I/O targets: b'\x00\x01\x00\x00\x00\x00'
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01\x03\x00\x02\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x03 (NAV-STATUS).
      Rates for 6 I/O targets: b'\x00\x02\x00\x00\x00\x00'
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\n\t\x00\x02\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x0A, ID 0x09 (MON-HW).
      Rates for 6 I/O targets: b'\x00\x02\x00\x00\x00\x00'
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
```

From the logging console of the OBS firmware (running on the ESP32), without having any peripheral connected:

```
[I][gps.cpp:278] setBaud(): GPS startup already 115200
[I][gps.cpp:177] softResetGps(): Soft-RESET GPS!
...
[W][gps.cpp:214] enableAlpIfDataIsAvailable(): Disable ALP - no data!
...
```
