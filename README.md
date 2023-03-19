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
Opened serial port '/dev/tty.usbserial-DEADBEEF' with a baudrate of 115200.
>>> Received VALID message class 0x06, ID 0x34 w/o payload.
    CFG-RINV
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x064Bk'
>>> Received VALID message class 0x06, ID 0x04 w/ payload b'\x00\x00\x02\x00' (length: 4).
    CFG-RST
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x04\x12;'
>>> Received VALID message class 0x06, ID 0x01 w/ payload b'\x0b2\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message class 0x0B, ID 0x50 w/o payload.
>>> Received VALID message class 0x0A, ID 0x04 w/o payload.
>>> Received VALID message class 0x0A, ID 0x09 w/o payload.
>>> Received VALID message class 0x01, ID 0x03 w/o payload.
>>> Received VALID message class 0x06, ID 0x24 w/o payload.
    CFG-NAV5
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06$2['
>>> Received VALID message class 0x06, ID 0x34 w/o payload.
    CFG-RINV
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x064Bk'
>>> Received VALID message class 0x06, ID 0x01 w/ payload b'\x01 \x00\x01\x00\x00\x00\x00' (length: 8).
    CFG-MSG
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message class 0x06, ID 0x01 w/ payload b'\x01\x03\x00\x02\x00\x00\x00\x00' (length: 8).
    CFG-MSG
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message class 0x06, ID 0x01 w/ payload b'\n\t\x00\x02\x00\x00\x00\x00' (length: 8).
    CFG-MSG
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
```

From the logging console of the OBS (ESP32):

```
[E][gps.cpp:349] sendAndWaitForAck(): Retry to send 0x3406
[I][gps.cpp:278] setBaud(): GPS startup already 115200
[I][gps.cpp:177] softResetGps(): Soft-RESET GPS!
[E][vfs_api.cpp:72] exists(): File system is not mounted
[W][gps.cpp:214] enableAlpIfDataIsAvailable(): Disable ALP - no data!
```