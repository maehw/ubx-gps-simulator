# Usage examples for OpenBikeSensor (OBS)

Example: Debugging the [OpenBikeSensor](https://www.openbikesensor.org/) [firmware](https://github.com/openbikesensor/OpenBikeSensorFirmware) v0.16.765 on an ESP32 development board without any attached hardware.

```
> python3 ubx_gps_simulator.py /dev/tty.usbserial-DEADBEEF

... Startup time: now=1679927703.867 s (used as reference 0.0 s)
>>> Received VALID message: class 0x06, ID 0x00 w/ payload b'\x01\x00\x00\x00\xd0\x08\x00\x00\x00\xc2\x01\x00\x03\x00\x01\x00\x00\x00\x00\x00' (length: 20).
      Port ID:        #1(*)
      TX ready:       b'\x00\x00'
      Mode:           b'\xd0\x08\x00\x00'
      Baudrate:       115200 [Bits/s]
      In proto mask:  b'\x03\x00'
      Out proto mask: b'\x01\x00'
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x00\x0e7'

!!! Reconfiguring serial's baudrate to 115200

>>> Received VALID message: class 0x06, ID 0x34 w/o payload.
    CFG-RINV (remote inventory)
    Poll request.
    Queued message. Queue length: 1 replies
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x064Bk'

... Preparing to send queued replies.
... Sending queued reply #0 (CFG-RINV): {'class': b'\x06', 'id': b'4', 'payload': b'\x00Notice: no data saved!'}
<<< Sending CFG-RINV message: b'\xb5b\x064\x17\x00\x00Notice: no data saved!\xf8\xbe'

>>> Received VALID message: class 0x06, ID 0x34 w/o payload.
    CFG-RINV (remote inventory)
    Poll request.
    Queued message. Queue length: 1 replies
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x064Bk'

... Preparing to send queued replies.
... Sending queued reply #0 (CFG-RINV): {'class': b'\x06', 'id': b'4', 'payload': b'\x00Notice: no data saved!'}
<<< Sending CFG-RINV message: b'\xb5b\x064\x17\x00\x00Notice: no data saved!\xf8\xbe'

>>> Received VALID message: class 0x06, ID 0x09 w/ payload b'\xff\xff\x00\x00\x00\x00\x00\x00\xfe\xff\x00\x00\x03' (length: 13).
    CFG-CFG (Clear, Save and Load configurations) with optional device mask: 0x03.
      Clear mask: b'\xff\xff\x00\x00'
      Save mask:  b'\x00\x00\x00\x00'
      Load mask:  b'\xfe\xff\x00\x00'
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
      Requested rate change: class=0xF0, ID=0x00, rate=0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\xf0\x04\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0xF0, ID 0x04 (NMEA-RMC).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0xF0, ID=0x04, rate=0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\xf0\x01\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0xF0, ID 0x01 (NMEA-GLL).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0xF0, ID=0x01, rate=0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\xf0\x02\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0xF0, ID 0x02 (NMEA-GSA).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0xF0, ID=0x02, rate=0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\xf0\x03\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0xF0, ID 0x03 (NMEA-GSA).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0xF0, ID=0x03, rate=0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\xf0\x05\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0xF0, ID 0x05 (NMEA-VTG).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0xF0, ID=0x05, rate=0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01\x03\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x03 (NAV-STATUS).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x03, rate=0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\n\t\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x0A, ID 0x09 (MON-HW).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0x0A, ID=0x09, rate=0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x0b2\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x0B, ID 0x32 (AID-ALPSRV).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0x0B, ID=0x32, rate=0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x16 w/ payload b'\x01\x03\x02\x00\x08\x00\x01\x00' (length: 8).
    CFG-SBAS (SBAS Configuration)
      Mode:      0x01
      Usage:     0x03
      Max. SBAS: 2
      scanmode2: 0
      scanmode1: b'\x08\x00\x01\x00'
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x16$M'

>>> Received VALID message: class 0x06, ID 0x16 w/o payload.
    CFG-SBAS (SBAS Configuration)
      Poll SBAS configuration.
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x16$M'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x012\x00;\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x32 (NAV-SBAS).
      Rates for 6 I/O targets: 0, 59(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x32, rate=59
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01\x02\x00\x01\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x02 (NAV-POSLLH).
      Rates for 6 I/O targets: 0, 1(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x02, rate=1
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

... Going to send message with class=0x01, ID=0x02; last=-1679927704.867 s, now=94.936 s
<<< Sending NAV-POSLLH message: b'\xb5b\x01\x02\x1c\x00\x13u\x90\x03\xb8\x1e\xe6\x06\xe4\x89\xb1\x1cX\xeb\x07\x00\x07\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x89\x8a'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01\x04\x00\x01\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x04 (NAV-DOP).
      Rates for 6 I/O targets: 0, 1(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x04, rate=1
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01\x06\x00\x01\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x06 (NAV-SOL).
      Rates for 6 I/O targets: 0, 1(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x06, rate=1
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01\x12\x00\x01\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x12 (NAV-VELNED).
      Rates for 6 I/O targets: 0, 1(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x12, rate=1
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

... Going to send message with class=0x01, ID=0x12; last=-1679927704.867 s, now=94.984 s
<<< Sending NAV-VELNED message: b'\xb5b\x01\x12$\x00Cu\x90\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x82,'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01 \x00\x01\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x20 (NAV-TIMEGPS).
      Rates for 6 I/O targets: 0, 1(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x20, rate=1
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
      Requested rate change: class=0x0B, ID=0x01, rate=185
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x09 w/ payload b'\x00\x00\x00\x00\xff\xff\x00\x00\x00\x00\x00\x00\x17' (length: 13).
    CFG-CFG (Clear, Save and Load configurations) with optional device mask: 0x17.
      Clear mask: b'\x00\x00\x00\x00'
      Save mask:  b'\xff\xff\x00\x00'
      Load mask:  b'\x00\x00\x00\x00'
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\t\x17@'

>>> Received VALID message: class 0x06, ID 0x34 w/o payload.
    CFG-RINV (remote inventory)
    Poll request.
    Queued message. Queue length: 1 replies
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x064Bk'

... Preparing to send queued replies.
... Sending queued reply #0 (CFG-RINV): {'class': b'\x06', 'id': b'4', 'payload': b'\x00Notice: no data saved!'}
<<< Sending CFG-RINV message: b'\xb5b\x064\x17\x00\x00Notice: no data saved!\xf8\xbe'

>>> Received VALID message: class 0x06, ID 0x04 w/ payload b'\x00\x00\x02\x00' (length: 4).
    CFG-RST (reset receiver/ clear backup data structure command).
      navBbrMask: b'\x00\x00' (hotstart)
      resetMode:  2
      reserved1:  0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x04\x12;'

>>> Received VALID message: class 0x06, ID 0x09 w/ payload b'\xff\xff\x00\x00\x00\x00\x00\x00\xfe\xff\x00\x00\x03' (length: 13).
    CFG-CFG (Clear, Save and Load configurations) with optional device mask: 0x03.
      Clear mask: b'\xff\xff\x00\x00'
      Save mask:  b'\x00\x00\x00\x00'
      Load mask:  b'\xfe\xff\x00\x00'
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
      Requested rate change: class=0xF0, ID=0x00, rate=0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\xf0\x04\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0xF0, ID 0x04 (NMEA-RMC).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0xF0, ID=0x04, rate=0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\xf0\x01\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0xF0, ID 0x01 (NMEA-GLL).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0xF0, ID=0x01, rate=0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\xf0\x02\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0xF0, ID 0x02 (NMEA-GSA).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0xF0, ID=0x02, rate=0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\xf0\x03\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0xF0, ID 0x03 (NMEA-GSA).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0xF0, ID=0x03, rate=0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\xf0\x05\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0xF0, ID 0x05 (NMEA-VTG).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0xF0, ID=0x05, rate=0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01\x03\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x03 (NAV-STATUS).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x03, rate=0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\n\t\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x0A, ID 0x09 (MON-HW).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0x0A, ID=0x09, rate=0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x0b2\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x0B, ID 0x32 (AID-ALPSRV).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0x0B, ID=0x32, rate=0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x16 w/ payload b'\x01\x03\x02\x00\x08\x00\x01\x00' (length: 8).
    CFG-SBAS (SBAS Configuration)
      Mode:      0x01
      Usage:     0x03
      Max. SBAS: 2
      scanmode2: 0
      scanmode1: b'\x08\x00\x01\x00'
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x16$M'

>>> Received VALID message: class 0x06, ID 0x16 w/o payload.
    CFG-SBAS (SBAS Configuration)
      Poll SBAS configuration.
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x16$M'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x012\x00;\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x32 (NAV-SBAS).
      Rates for 6 I/O targets: 0, 59(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x32, rate=59
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01\x02\x00\x01\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x02 (NAV-POSLLH).
      Rates for 6 I/O targets: 0, 1(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x02, rate=1
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01\x04\x00\x01\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x04 (NAV-DOP).
      Rates for 6 I/O targets: 0, 1(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x04, rate=1
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

... Going to send message with class=0x01, ID=0x02; last=94.936 s, now=95.938 s
<<< Sending NAV-POSLLH message: b'\xb5b\x01\x02\x1c\x00\xfdx\x90\x03\xb8\x1e\xe6\x06\xe4\x89\xb1\x1cX\xeb\x07\x00\x07\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00vs'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01\x06\x00\x01\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x06 (NAV-SOL).
      Rates for 6 I/O targets: 0, 1(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x06, rate=1
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01\x12\x00\x01\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x12 (NAV-VELNED).
      Rates for 6 I/O targets: 0, 1(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x12, rate=1
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01 \x00\x01\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x20 (NAV-TIMEGPS).
      Rates for 6 I/O targets: 0, 1(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x20, rate=1
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

... Going to send message with class=0x01, ID=0x12; last=94.984 s, now=95.986 s
<<< Sending NAV-VELNED message: b'\xb5b\x01\x12$\x00-y\x90\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00p\xa0'

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
      Requested rate change: class=0x0B, ID=0x01, rate=185
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x09 w/ payload b'\x00\x00\x00\x00\xff\xff\x00\x00\x00\x00\x00\x00\x17' (length: 13).
    CFG-CFG (Clear, Save and Load configurations) with optional device mask: 0x17.
      Clear mask: b'\x00\x00\x00\x00'
      Save mask:  b'\xff\xff\x00\x00'
      Load mask:  b'\x00\x00\x00\x00'
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\t\x17@'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x0b2\x00\x00\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x0B, ID 0x32 (AID-ALPSRV).
      Rates for 6 I/O targets: 0, 0(*),  0,  0, 0, 0
      Requested rate change: class=0x0B, ID=0x32, rate=0
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x0B, ID 0x50 w/o payload.
    AID-ALP (ALP file data transfer to the receiver)
      ALP file data: b''
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
    Queued message. Queue length: 1 replies
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x064Bk'

... Preparing to send queued replies.
... Sending queued reply #0 (CFG-RINV): {'class': b'\x06', 'id': b'4', 'payload': b'\x00Notice: no data saved!'}
<<< Sending CFG-RINV message: b'\xb5b\x064\x17\x00\x00Notice: no data saved!\xf8\xbe'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01 \x00\x01\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x20 (NAV-TIMEGPS).
      Rates for 6 I/O targets: 0, 1(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x20, rate=1
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\x01\x03\x00\x02\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x01, ID 0x03 (NAV-STATUS).
      Rates for 6 I/O targets: 0, 2(*),  0,  0, 0, 0
      Requested rate change: class=0x01, ID=0x03, rate=2
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

>>> Received VALID message: class 0x06, ID 0x01 w/ payload b'\n\t\x00\x02\x00\x00\x00\x00' (length: 8).
    CFG-MSG for class 0x0A, ID 0x09 (MON-HW).
      Rates for 6 I/O targets: 0, 2(*),  0,  0, 0, 0
      Requested rate change: class=0x0A, ID=0x09, rate=2
<<< Sending ACK-ACK response: b'\xb5b\x05\x01\x02\x00\x06\x01\x0f8'

... Going to send message with class=0x01, ID=0x02; last=95.938 s, now=96.954 s
<<< Sending NAV-POSLLH message: b'\xb5b\x01\x02\x1c\x00\xf5|\x90\x03\xb8\x1e\xe6\x06\xe4\x89\xb1\x1cX\xeb\x07\x00\x07\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00r\xff'

... Going to send message with class=0x01, ID=0x12; last=95.986 s, now=96.987 s
<<< Sending NAV-VELNED message: b'\xb5b\x01\x12$\x00\x16}\x90\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00]\xf0'

... Going to send message with class=0x01, ID=0x02; last=96.954 s, now=97.970 s
<<< Sending NAV-POSLLH message: b'\xb5b\x01\x02\x1c\x00\xed\x80\x90\x03\xb8\x1e\xe6\x06\xe4\x89\xb1\x1cX\xeb\x07\x00\x07\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00n\x8b'

... Going to send message with class=0x01, ID=0x12; last=96.987 s, now=98.004 s
<<< Sending NAV-VELNED message: b'\xb5b\x01\x12$\x00\x0f\x81\x90\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00Z\x80'
```

From the logging console of the OBS firmware (running on the ESP32), without having any peripheral connected:

```
...
[E][gps.cpp:349] sendAndWaitForAck(): Retry to send 0x3406
[E][gps.cpp:349] sendAndWaitForAck(): Retry to send 0x3406
[E][gps.cpp:349] sendAndWaitForAck(): Retry to send 0x3406
[E][gps.cpp:354] sendAndWaitForAck(): Failed to send cfg. 0x3406 NAK: 0 
[W][gps.cpp:639] encode(): Unexpected GPS char in state null: ...
...
[E][gps.cpp:349] sendAndWaitForAck(): Retry to send 0x3406
[I][gps.cpp:426] addStatisticsMessage(): New: RINV: Notice: no data saved!
[I][gps.cpp:834] parseUbxMessage(): GPS config from Notice: no data saved! outdated - will trigger update.
[I][gps.cpp:834] parseUbxMessage(): GPS config from Notice: no data saved! outdated - will trigger update.
[W][gps.cpp:1192] prepareGpsData(): Had to switch incomplete record tow: 59798803 pos: 1, info: 0, hdop: 0, vel: 0
[I][gps.cpp:426] addStatisticsMessage(): New: OBS: Did update GPS settings.
[I][gps.cpp:173] configureGpsModule(): Config GPS done!
[I][gps.cpp:177] softResetGps(): Soft-RESET GPS!
[I][gps.cpp:834] parseUbxMessage(): GPS config from Notice: no data saved! outdated - will trigger update.
[W][gps.cpp:1192] prepareGpsData(): Had to switch incomplete record tow: 59798851 pos: 0, info: 0, hdop: 0, vel: 1
[W][gps.cpp:1192] prepareGpsData(): Had to switch incomplete record tow: 59799805 pos: 1, info: 0, hdop: 0, vel: 0
[I][gps.cpp:173] configureGpsModule(): Config GPS done!
...
[W][gps.cpp:214] enableAlpIfDataIsAvailable(): Disable ALP - no data!
[I][gps.cpp:834] parseUbxMessage(): GPS config from Notice: no data saved! outdated - will trigger update.
...
[W][gps.cpp:1192] prepareGpsData(): Had to switch incomplete record tow: 59799853 pos: 0, info: 0, hdop: 0, vel: 1
[W][gps.cpp:1192] prepareGpsData(): Had to switch incomplete record tow: 59800821 pos: 1, info: 0, hdop: 0, vel: 0
[W][gps.cpp:1192] prepareGpsData(): Had to switch incomplete record tow: 59800854 pos: 0, info: 0, hdop: 0, vel: 1
[W][gps.cpp:1192] prepareGpsData(): Had to switch incomplete record tow: 59801837 pos: 1, info: 0, hdop: 0, vel: 0
...
```
