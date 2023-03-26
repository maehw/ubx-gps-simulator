# README

There's a bunch of scripts and tools that allow to communicate with u-blox GPS receivers. However, I was unable to find scripts or tools that simulate the GPS receiver side. This Python script simulates the GPS receiver serial communication using UBX message protocol over Universal Asynchronous Receiver/Transmitter (UART). The idea is to replace the GPS receiver hardware by running this script - e.g. for testing code indoors before using it with real hardware.

The simulator is planned to implement the proprietary (but with an accessible specification document) u-blox 6 GPS receiver UBX message protocol. It may also apply for other u-blox GPS receivers - if you know more, let us know.

Its functionality is currently limited to:
* receiving all messages and evaluating their checksums,
* recognizing `CFG` class messages (`0x06`) and replying with an `ACK-ACK`.
* assuming to run on and performing baudrate changes on I/O configuration port #1 (UART)

**Disclaimer**: The code has a lot of hacks, feel free to improve it and make a pull request! Please also understand that this software will never cover all functions of the real GPS receiver hardware - and there are likely some bugs in the code (search for `FIXME` and `TODO`)!


# Usage

```
usage: ubx_gps_simulator.py [-h] [-b SERIAL_BAUDRATE] serial_port_name

ubx_gps_simulator.py Run simulated UBX GPX receiver.

positional arguments:
  serial_port_name      Serial port name

optional arguments:
  -h, --help            show this help message and exit
  -b SERIAL_BAUDRATE, --serial-baudrate SERIAL_BAUDRATE
                        Serial baudrate with which the simulator is accessed
                        initially (default: 9600, possible: 4800, 9600, 19200,
                        38400, 57600, 115200)
```

## Usage examples for OpenBikeSensor (OBS)

See [OpenBikeSensor Usage](./OpenBikeSensor_Usage.md).
