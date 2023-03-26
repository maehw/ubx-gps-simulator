# Usage examples for OpenBikeSensor (OBS)

Example: Debugging the [OpenBikeSensor](https://www.openbikesensor.org/) [firmware](https://github.com/openbikesensor/OpenBikeSensorFirmware) v0.16.765 on an ESP32 development board without any attached hardware.

```
> python3 ubx_gps_simulator.py /dev/tty.usbserial-DEADBEEF

>>> Received VALID message: class 0x06, ID 0x00 w/ payload b'\x01\x00\x00\x00\xd0\x08\x00\x00\x00\xc2\x01\x00\x03\x00\x01\x00\x00\x00\x00\x00' (length: 20).
      Port ID:        #1(*)
      TX ready:       b'\x00\x00'
      Mode:           b'\xd0\x08\x00\x00'
      Baudrate:       115200 [Bits/s]
      In proto mask:  b'\x03\x00'
      Out proto mask: b'\x01\x00'
!!! Reconfiguring serial's baudrate to 115200
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x00\x0e7'
>>> Received VALID message: class 0x06, ID 0x34 w/o payload.
    CFG-RINV (remote inventory)
    Poll request.
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x064Bk'
>>> Received VALID message: class 0x06, ID 0x09 w/ payload b'\xff\xff\x00\x00\x00\x00\x00\x00\xfe\xff\x00\x00\x03' (length: 13).
    CFG-CFG
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\t\x17@'
>>> Received VALID message: class 0x06, ID 0x02 w/ payload b'\x00\x00\x00\x00\x00\xff\x00\x00\x00\x00' (length: 10).
    CFG-INF
      Target ID: #0
        Protocol ID: UBX Protocol
      Enabled messages:  ERROR, WARNING, NOTICE, DEBUG, TEST
      Disabled messages: (none)
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x02\x109'
>>> Received VALID message: class 0x06, ID 0x02 w/ payload b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00' (length: 10).
    CFG-INF
      Target ID: #0
        Protocol ID: NMEA Protocol
      Enabled messages:  (none)
      Disabled messages: ERROR, WARNING, NOTICE, DEBUG, TEST
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x02\x109'
>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\xf0\x00\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0xF0, ID 0x00 (NMEA-GGA).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0xF0, ID=0x00, rate=0 (TODO)
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\xf0\x04\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0xF0, ID 0x04 (NMEA-RMC).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0xF0, ID=0x04, rate=0 (TODO)
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\xf0\x01\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0xF0, ID 0x01 (NMEA-GLL).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0xF0, ID=0x01, rate=0 (TODO)
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\xf0\x02\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0xF0, ID 0x02 (NMEA-GSA).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0xF0, ID=0x02, rate=0 (TODO)
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\xf0\x03\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0xF0, ID 0x03 (NMEA-GSA).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0xF0, ID=0x03, rate=0 (TODO)
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\xf0\x05\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0xF0, ID 0x05 (NMEA-VTG).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0xF0, ID=0x05, rate=0 (TODO)
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01\x03\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x03 (NAV-STATUS).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x03, rate=0 (TODO)
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\n\t\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x0A, ID 0x09 (MON-HW).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0x0A, ID=0x09, rate=0 (TODO)
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x0b2\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x0B, ID 0x32 (AID-ALPSRV).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0x0B, ID=0x32, rate=0 (TODO)
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message: class 0x06, ID 0x16 w/ payload b'\x01\x03\x02\x00\x08\x00\x01\x00' (length: 8).
    CFG-SBAS
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x16$M'
>>> Received VALID message: class 0x06, ID 0x16 w/o payload.
    CFG-SBAS
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x16$M'
>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x012\x00;\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x32 (NAV-SBAS).
      Rates for 6 I/O targets: 0, 59(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x32, rate=59 (TODO)
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01\x02\x00\x01\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x02 (NAV-POSLLH).
      Rates for 6 I/O targets: 0, 1(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x02, rate=1 (TODO)
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01\x04\x00\x01\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x04 (NAV-DOP).
      Rates for 6 I/O targets: 0, 1(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x04, rate=1 (TODO)
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01\x06\x00\x01\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x06 (NAV-SOL).
      Rates for 6 I/O targets: 0, 1(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x06, rate=1 (TODO)
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01\x12\x00\x01\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x12 (NAV-VELNED).
      Rates for 6 I/O targets: 0, 1(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x12, rate=1 (TODO)
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01 \x00\x01\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x20 (NAV-TIMEGPS).
      Rates for 6 I/O targets: 0, 1(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x20, rate=1 (TODO)
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message: class 0x06, ID 0x24 w/ payload b"\xff\xff\x03\x03\x00\x00\x00\x00\x10'\x00\x00\x05\x00\xfa\x00\xfa\x00d\x00,\x01P\x00\x00\x00\x00\x00\x14\x00\x00\x00\x00\x00\x00\x00" (length: 36).
    CFG-NAV5 (Navigation Engine Settings)
      Mask: b'\xff\xff'
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06$2['
>>> Received VALID message: class 0x06, ID 0x07 w/ payload b"\x80\x96\x98\x00\x10'\x00\x00\x01\x01\x00\x002\x00\x00\x00\x00\x00\x00\x00" (length: 20).
    CFG-TP (TimePulse Parameters)
      Interval:          10000000 [us]
      Length:            10000 [us]
      Status:            1
      Time reference:    1
      Flags:             0x00
        Sync mode:       0
      Ant. cable delay:  50 [ns]
      RX RF group delay: 0 [ns]
      User delay:        0 [ns]
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x07\x15>'
>>> Received VALID message: class 0x06, ID 0x34 w/ payload b'\x01openbikesensor.org/v0.16.765' (length: 29).
    CFG-RINV (remote inventory)
      Flags: binary=False, dump=True.
      Data: b'openbikesensor.org/v0.16.765'
      Data (textual): 'openbikesensor.org/v0.16.765'
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x064Bk'
>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x0b\x01\x00\xb9\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x0B, ID 0x01 (AID-INI).
      Rates for 6 I/O targets: 0, 185(*),  0,  0, 0, 0
      Requested rate change: class=0x0B, ID=0x01, rate=185 (TODO)
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message: class 0x06, ID 0x09 w/ payload b'\x00\x00\x00\x00\xff\xff\x00\x00\x00\x00\x00\x00\x17' (length: 13).
    CFG-CFG
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\t\x17@'
>>> Received VALID message: class 0x06, ID 0x34 w/o payload.
    CFG-RINV (remote inventory)
    Poll request.
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x064Bk'
>>> Received VALID message: class 0x06, ID 0x04 w/ payload b'\x00\x00\x02\x00' (length: 4).
    CFG-RST (reset receiver/ clear backup data structure command).
      navBbrMask: b'\x00\x00' (hotstart)
      resetMode:  2
      reserved1:  0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x04\x12;'
>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x0b2\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x0B, ID 0x32 (AID-ALPSRV).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0x0B, ID=0x32, rate=0 (TODO)
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message: class 0x0B, ID 0x50 w/o payload.
    AID-ALP (ALP file data transfer to the receiver)
      ALP file data: b''
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x0bPc\x91'
>>> Received VALID message: class 0x0A, ID 0x04 w/o payload.
    MON-VER (Receiver/Software/ROM Version, poll request)
>>> Received VALID message: class 0x0A, ID 0x09 w/o payload.
    MON-HW (unhandled)
>>> Received VALID message: class 0x01, ID 0x03 w/o payload.
    NAV-STATUS (unhandled)
>>> Received VALID message: class 0x06, ID 0x24 w/o payload.
    CFG-NAV5 (Navigation Engine Settings)
      Poll message configuration.
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06$2['
>>> Received VALID message: class 0x06, ID 0x34 w/o payload.
    CFG-RINV (remote inventory)
    Poll request.
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x064Bk'
>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01 \x00\x01\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x20 (NAV-TIMEGPS).
      Rates for 6 I/O targets: 0, 1(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x20, rate=1 (TODO)
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01\x03\x00\x02\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x03 (NAV-STATUS).
      Rates for 6 I/O targets: 0, 2(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x03, rate=2 (TODO)
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\n\t\x00\x02\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x0A, ID 0x09 (MON-HW).
      Rates for 6 I/O targets: 0, 2(*),  0,  0, 0, 0
      Requested rate change: class=0x0A, ID=0x09, rate=2 (TODO)
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'
```

From the logging console of the OBS firmware (running on the ESP32), without having any peripheral connected:

```
[E][gps.cpp:349] sendAndWaitForAck(): Retry to send 0x3406
[E][gps.cpp:349] sendAndWaitForAck(): Retry to send 0x3406
[E][gps.cpp:349] sendAndWaitForAck(): Retry to send 0x3406
[E][gps.cpp:354] sendAndWaitForAck(): Failed to send cfg. 0x3406 NAK: 0 
[I][gps.cpp:426] addStatisticsMessage(): New: OBS: Did update GPS settings.
[I][gps.cpp:173] configureGpsModule(): Config GPS done!
[I][gps.cpp:177] softResetGps(): Soft-RESET GPS!
...
[W][gps.cpp:214] enableAlpIfDataIsAvailable(): Disable ALP - no data!
[E][gps.cpp:805] parseUbxMessage(): ACK overrun had ack: 1 for 0x500b
...
```
