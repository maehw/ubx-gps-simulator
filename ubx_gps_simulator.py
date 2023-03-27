import argparse
import serial
import pendulum
from enum import Enum


# TODO
# - class DynamicPlatformModel(Enum):
#   portable (default), stationary etc.
# - class NavigationInputFilter(Enum):
#   fixMode (default), fixAlt etc.
# - class NavigationOutputFilter(...)
# - current configuration (volatile) vs
#   default configuration (non-volatile) vs
#   permanent configuration (non-volatile)
#   (e.g. by using an external configuration file to load and save)
# - class StartupMode(Enum):
#   cold start, warm start, hot start (depending on ephemeris data)
# - remote inventory (binary or ASCII data)

messages = {
    b'\x01': {
        'class_name': 'NAV',
        b'\x01': {'code': 'POSECEF'},
        b'\x02': {'code': 'POSLLH'},  # Geodetic Position Solution
        b'\x03': {'code': 'STATUS'},  # Receiver Navigation Status
        b'\x04': {'code': 'DOP'},
        b'\x06': {'code': 'SOL'},  # Navigation Solution Information
        b'\x11': {'code': 'VELECEF'},
        b'\x12': {'code': 'VELNED'},  # Velocity Solution in NED
        b'\x20': {'code': 'TIMEGPS'},  # GPS Time Solution
        b'\x21': {'code': 'TIMEUTC'},  # UTC Time Solution
        b'\x22': {'code': 'NAVCLOCK'},
        b'\x30': {'code': 'SVINFO'},
        b'\x31': {'code': 'DGPS'},
        b'\x32': {'code': 'SBAS'},
        b'\x40': {'code': 'EFKSTATUS'},
        b'\x60': {'code': 'AOPSTATUS'},
    },
    b'\x02': {
        'class_name': 'RXM',
        b'\x10': {'code': 'RAW'},
        b'\x11': {'code': 'SFRB'},
        b'\x20': {'code': 'SVSI'},
        b'\x30': {'code': 'ALM'},
        b'\x31': {'code': 'EPH'},
        b'\x41': {'code': 'PMREQ'},
    },
    b'\x04': {
        'class_name': 'INF',
        b'\x00': {'code': 'ERROR'},
        b'\x01': {'code': 'WARNING'},
        b'\x02': {'code': 'NOTICE'},
        b'\x03': {'code': 'TEST'},
        b'\x04': {'code': 'DEBUG'},
    },
    b'\x05': {
        'class_name': 'ACK',
        b'\x00': {'code': 'NAK'},
        b'\x01': {'code': 'ACK'},
    },
    b'\x06': {
        'class_name': 'CFG',
        b'\x00': {'code': 'PRT'},  # port settings
        b'\x01': {'code': 'MSG'},  # message settings (enable/disable, update rate)
        b'\x02': {'code': 'INF'},  # information output settings (errors, warnings, notice, test etc.)
        b'\x04': {'code': 'RST'},
        b'\x06': {'code': 'DAT'},
        b'\x07': {'code': 'TP'},  # TimePulse Parameters
        b'\x08': {'code': 'RATE'},
        b'\x09': {'code': 'CFG'},
        b'\x0E': {'code': 'FXN'},
        b'\x11': {'code': 'RXM'},
        b'\x12': {'code': 'EKF'},
        b'\x13': {'code': 'ANT'},
        b'\x16': {'code': 'SBAS'},
        b'\x17': {'code': 'NMEA'},
        b'\x1B': {'code': 'USB'},  # USB settings
        b'\x1D': {'code': 'TMODE'},
        b'\x22': {'code': 'NVS'},
        b'\x23': {'code': 'NAVX5'},
        b'\x24': {'code': 'NAV5'},  # Navigation Engine Settings
        b'\x29': {'code': 'ESFGWT'},
        b'\x31': {'code': 'TP5'},
        b'\x32': {'code': 'PM'},
        b'\x34': {'code': 'RINV'},
        b'\x39': {'code': 'ITFM'},
        b'\x3B': {'code': 'PM2'},
        b'\x3D': {'code': 'TMODE2'},
    },
    b'\x0A': {
        'class_name': 'MON',
        b'\x02': {'code': 'IO'},
        b'\x04': {'code': 'VER'},  # Receiver/Software/ROM Version
        b'\x06': {'code': 'MSGPP'},
        b'\x07': {'code': 'RXBUF'},
        b'\x08': {'code': 'TXBUF'},
        b'\x09': {'code': 'HW'},  # Hardware Status
        b'\x0B': {'code': 'HW2'},  # Extended Hardware Status
        b'\x21': {'code': 'RXR'},
    },
    b'\x0B': {
        'class_name': 'AID',  # AssistNow Aiding Messages
        b'\x00': {'code': 'REQ'},  # poll (AID-DATA) for all GPS Aiding Data
        b'\x01': {'code': 'INI'},  # GPS Initial Aiding Data
        b'\x02': {'code': 'HUI'},  # GPS Health, UTC and ionosphere parameters
        b'\x10': {'code': 'DATA'},  # GPS Initial Aiding Data (poll)
        b'\x30': {'code': 'ALM'},  # GPS Aiding Almanac
        b'\x31': {'code': 'EPH'},  # GPS Aiding Ephemeris Data
        b'\x32': {'code': 'ALPSRV'},  # ALP client AlmanacPlus data
        b'\x33': {'code': 'AOP'},  # AssistNow Autonomous data
        b'\x50': {'code': 'ALP'},  # ALP file data transfer
    },
    b'\x0D': {
        'class_name': 'TIM',
        b'\x01': {'code': 'TP'},
        b'\x03': {'code': 'TM2'},
        b'\x04': {'code': 'SVIN'},
        b'\x06': {'code': 'VRFY'},
    },
    b'\x10': {
        'class_name': 'ESF',
        b'\x02': {'code': 'MEAS'},
        b'\x10': {'code': 'STATUS'},
    },
    b'\xF0': {
        'class_name': 'NMEA',
        b'\x00': {'code': 'GGA'},  # Global positioning system fix data
        b'\x01': {'code': 'GLL'},  # Latitude and longitude, with time of position fix and status
        b'\x02': {'code': 'GSA'},  # GNSS DOP and Active Satellites
        b'\x03': {'code': 'GSA'},  # GNSS Satellites in View
        b'\x04': {'code': 'RMC'},  # Recommended Minimum data
        b'\x05': {'code': 'VTG'},  # Course over ground and Ground speed
    },
}


class UbxGpsSimulator:
    class RxState(Enum):
        # states for receiver state machine to parse UBX packet structure
        WAIT_SYNC_1 = 1  # Wait 1st Sync Byte Rx'ed (0xB5)
        WAIT_SYNC_2 = 2  # Wait 2nd Sync Byte Rx'ed (0x62)
        WAIT_MSG_CLASS = 3  # Wait Message Class Byte Rx'ed
        WAIT_MSG_ID = 4  # Wait Message ID Byte Rx'ed
        WAIT_LENGTH_1 = 5  # Wait 1st Length Byte Rx'ed
        WAIT_LENGTH_2 = 6  # Wait 2nd Length Byte Rx'ed
        WAIT_PAYLOAD_CPLT = 7  # Wait Payload Completely Rx'ed
        WAIT_CHECKSUM_START = 8  # Wait 1st Checksum Byte Rx'ed
        WAIT_MSG_CPLT = 9  # Wait 2nd Checksum Byte Rx'ed

    def __init__(self,
                 serial_port_name,
                 serial_baudrate,
                 serial_baudrates_accepted,
                 serial_blocking_read_timeout,
                 io_target):
        self.startup_time_millis = 0
        self.message_rates = dict()  # start with an empty dict
        self.queued_replies = []
        self.io_target = io_target
        self.baudrates_accepted = serial_baudrates_accepted

        # From the specification, section about "UART Ports":
        # "The serial ports consist of an RX and a TX line.
        #  Neither handshaking signals nor hardware flow control signals are available."
        # Configuration must be 8N1, but different baud rates are possible.
        self.ser = serial.Serial(port=serial_port_name,
                                 baudrate=serial_baudrate,
                                 timeout=serial_blocking_read_timeout)
        print(f"Opened serial port '{self.ser.name}' with a baudrate of {self.ser.baudrate} and "
              f"serial blocking read timeout of {serial_blocking_read_timeout} seconds. "
              f"Simulating I/O target #{self.io_target}.")

    @staticmethod
    def print_protocol_id(identifier):
        print("        Protocol ID: ", end="")
        if identifier == 0:
            print("UBX Protocol")
        elif identifier == 1:
            print("NMEA Protocol")
        else:
            print("Reserved")

    @staticmethod
    def calc_fletcher_checksum(block):
        # calculate checksum using 8 bit Fletcher algorithm
        ck_a = 0
        ck_b = 0
        for b in block:
            ck_a += b
            ck_a = ck_a & 0xFF
            ck_b += ck_a
            ck_b = ck_b & 0xFF
        return ck_a.to_bytes(1, 'little') + ck_b.to_bytes(1, 'little')

    @staticmethod
    def get_time_of_week(timestamp=None):
        # calculate "GPS Millisecond Time of Week" ('itow')
        # from timestamp or for just now
        if timestamp is None:
            timestamp = pendulum.now()
        time_of_week = int(timestamp.format('x')) - int(timestamp.start_of('week').format('x'))
        return time_of_week

    @staticmethod
    def get_msg_code(msg):
        if msg['class'] in messages:
            code = messages[msg['class']]['class_name']
            if msg['id'] in messages[msg['class']]:
                code += "-" + messages[msg['class']][msg['id']]['code']
            else:
                code += "???"
        else:
            code = "???-???"
        return code

    @staticmethod
    def now():
        timestamp = pendulum.now()
        millis = int(timestamp.format('x'))  # cannot just use the attribute 'microseconds' due to wrap-around
        return timestamp, millis

    def run(self):
        _, self.startup_time_millis = self.now()
        print(f"... Startup time: now={self.startup_time_millis/1000:.3f} s (used as reference 0.0 s)")

        # run the state machine, receiving and processing byte by byte;
        # please note that this script runs single-threaded and does both RX and TX
        rx_state = self.RxState.WAIT_SYNC_1
        msg = {}

        # enter endless loop and process one received byte at a time
        while True:
            rx_byte = self.ser.read()
            # check if timeout has occurred or if a byte has been received
            # TODO: move this into a less complex part of code (state machine driver)
            if rx_byte:
                # a byte has been received
                if rx_state == self.RxState.WAIT_SYNC_1:
                    if rx_byte == b'\xb5':
                        rx_state = self.RxState.WAIT_SYNC_2
                    else:
                        rx_state = self.RxState.WAIT_SYNC_1
                elif rx_state == self.RxState.WAIT_SYNC_2:
                    if rx_byte == b'\x62':
                        # print("Found sync bytes (start of message).")
                        rx_state = self.RxState.WAIT_MSG_CLASS
                    else:
                        rx_state = self.RxState.WAIT_SYNC_1
                elif rx_state == self.RxState.WAIT_MSG_CLASS:
                    msg = {
                        'class': rx_byte,
                        'id': None,
                        'len_raw': None,
                        'remaining_len': 0,
                        'payload': b'',
                        'checksum': None
                    }
                    rx_state = self.RxState.WAIT_MSG_ID
                elif rx_state == self.RxState.WAIT_MSG_ID:
                    msg['id'] = rx_byte
                    rx_state = self.RxState.WAIT_LENGTH_1
                elif rx_state == self.RxState.WAIT_LENGTH_1:
                    msg['len_raw'] = rx_byte
                    rx_state = self.RxState.WAIT_LENGTH_2
                elif rx_state == self.RxState.WAIT_LENGTH_2:
                    msg['len_raw'] += rx_byte
                    # recalculate length from the two bytes
                    remaining_len = int.from_bytes(msg['len_raw'], 'little', signed=False)
                    msg['remaining_len'] = remaining_len
                    if remaining_len > 0:
                        rx_state = self.RxState.WAIT_PAYLOAD_CPLT
                    else:
                        # skipping payload
                        rx_state = self.RxState.WAIT_CHECKSUM_START
                elif rx_state == self.RxState.WAIT_PAYLOAD_CPLT:
                    msg['remaining_len'] -= 1
                    msg['payload'] += rx_byte
                    if msg['remaining_len'] <= 0:
                        rx_state = self.RxState.WAIT_CHECKSUM_START
                elif rx_state == self.RxState.WAIT_CHECKSUM_START:
                    # here comes the first byte of the checksum
                    msg['checksum'] = rx_byte
                    rx_state = self.RxState.WAIT_MSG_CPLT
                elif rx_state == self.RxState.WAIT_MSG_CPLT:
                    msg['checksum'] += rx_byte
                    if self.has_valid_checksum(msg):
                        print(f">>> Received VALID message: class 0x{ord(msg['class']):02X}, "
                              f"ID 0x{ord(msg['id']):02X} ", end="")
                        if msg['payload'] == b'':
                            print(f"w/o payload.")
                        else:
                            print(f"w/ payload {msg['payload']} (length: {len(msg['payload'])}).")
                        self.process_message(msg)
                    else:
                        print(f"!!! Received INVALID message: {msg}.")
                    rx_state = self.RxState.WAIT_SYNC_1

            # make sure to transmit *after* having processed the received message as
            # this can have triggered some direct transmissions
            # (ACK-ACK, ACK-NAK, replies to poll requests)

            # process queued transmissions
            self.send_queued_replies()

            # handle cyclic transmissions
            current_time, current_time_millis = self.now()

            if self.check_cyclic_tx(millis=current_time_millis, msg_class=b'\x01', msg_id=b'\x02'):
                self.send_nav_posllh(self.get_time_of_week(current_time),
                                     lon=11.574444, lat=48.139722,
                                     height=519.0, hmsl=519.0,
                                     hacc=0, vacc=0)
            if self.check_cyclic_tx(millis=current_time_millis, msg_class=b'\x01', msg_id=b'\x12'):
                self.send_nav_velned(self.get_time_of_week(current_time))

            # TODO:
            # - send_nav_dop(ser)
            # - send_nav_status(ser)
            # - send_nav_sol(ser)  # FIXME: not implemented yet
            # - self.send_nav_timegps(current_time_of_week,
            #                 frac_time_of_week=0,
            #                 week=current_time.week_of_year)
            # - send_nav_timeutc(ser)  # FIXME: not implemented yet
            # - send_mon_hw(ser)  # FIXME: not implemented yet

            last_tx_time_millis = current_time_millis  # just "now"

    def process_message(self, msg):
        # process message, i.e.
        # - decode class and ID to a human-readable code
        # - decode single messages in more detail
        # - reply with ACK-ACK messages to CFG-* messages

        # handle specific messages
        if msg['class'] == b'\x06':
            send_ack = None  # initialize return value (None: do not send ACK or NAK, True: send ACK, False: send NAK)

            # "Configuration Input Messages: Set Dynamic Model, Set DOP Mask,
            #  Set Baud Rate, etc."
            # "The CFG Class can be used to configure the receiver and read out
            #  current configuration values. Any messages in Class CFG sent to the
            #  receiver are acknowledged (with Message ACK-ACK) if processed
            #  successfully, and rejected (with Message ACK-NAK) if processing the
            #  message failed."
            if msg['id'] == b'\x00':
                send_ack = self.process_cfg_prt(msg)
            elif msg['id'] == b'\x01':
                send_ack = self.process_cfg_msg(msg)
            elif msg['id'] == b'\x02':
                send_ack = self.process_cfg_inf(msg)
            elif msg['id'] == b'\x04':
                send_ack = self.process_cfg_rst(msg)
            elif msg['id'] == b'\x07':
                send_ack = self.process_cfg_tp(msg)
            elif msg['id'] == b'\x09':
                send_ack = self.process_cfg_cfg(msg)
            elif msg['id'] == b'\x16':
                send_ack = self.process_cfg_sbas(msg)
            elif msg['id'] == b'\x24':
                send_ack = self.process_cfg_nav5(msg)
            elif msg['id'] == b'\x34':
                send_ack = self.process_cfg_rinv(msg)
            else:
                print(f"!!! Received {self.get_msg_code(msg)} - processing not implemented yet (TODO)")

            if send_ack in [True, False]:
                # send ACK-ACK or ACK-NAK
                self.send_ack_or_nak(msg['class'], msg['id'], send_ack)

        elif msg['class'] == b'\x0a' and msg['id'] == b'\x04':
            self.process_mon_ver(msg)
        # elif msg['class'] == b'\x0b' and msg['id'] == b'\x01':
        #    process_aid_ini(msg)
        # elif msg['class'] == b'\x0b' and msg['id'] == b'\x32':
        #    process_aid_alpsrv(msg)
        elif msg['class'] == b'\x0b' and msg['id'] == b'\x50':
            self.process_aid_alp(msg)
            # self.send_ack_ack(msg['class'], msg['id'])  # allow to send next chunk directly
            # TODO: investigate; at least OBS firmware gives an ACK overrun! may have been wrong in the firmware or here
        else:
            print(f"    {self.get_msg_code(msg)} (unhandled)")
            print()  # Improve readability of log by adding an empty line

    def queue_reply(self, msg):
        assert 'class' in msg, "Missing message class"
        assert 'id' in msg, "Missing message ID"
        assert 'payload' in msg, "Missing message payload"
        self.queued_replies.append(msg)
        print(f"    Queued message. Queue length: {len(self.queued_replies)} replies")

    def send_queued_replies(self):
        # send replies that have been queued by calling queue_reply()
        if self.queued_replies:
            print("... Preparing to send queued replies.")
            i = 0
            for msg in self.queued_replies:
                print(f"... Sending queued reply #{i} ({self.get_msg_code(msg)}): {msg}")

                sync = b'\xb5\x62'
                length = len(msg['payload']).to_bytes(2, 'little')
                body = msg['class'] + msg['id'] + length
                body += msg['payload']
                cs = self.calc_fletcher_checksum(body)
                msg['payload'] = sync + body + cs
                print(f"<<< Sending {self.get_msg_code(msg)} message: {msg['payload']}")
                print()  # Improve readability of log by adding an empty line
                self.ser.write(msg['payload'])

                i += 1
            self.queued_replies = []  # OK to empty list here as there's no concurrency

    def process_cfg_prt(self, msg):
        assert msg['class'] == b'\x06' and msg['id'] == b'\x00', "Unexpected call."
        payload_len = len(msg['payload'])
        assert payload_len in [0, 1, 20], f"Unexpected {self.get_msg_code(msg)} " \
                                          f"payload length (expecting 0, 1 or 20 bytes)."
        # FIXME: possibly also multiple of 20 bytes (i.e. multiple 'configuration units')

        if payload_len == 0:
            print("      Poll the configuration of the used I/O Port.")
            # TODO: should queue reply with message configuration (ACK comes first)
            # self.queue_reply()
        elif payload_len == 1:
            print("      Poll the configuration of one I/O Port.")
            # TODO: should queue reply with message configuration (ACK comes first)
            # self.queue_reply()
        else:
            port_id = msg['payload'][0]  # single element is interpreted as integer in the range 0..255 by default
            if port_id in [1, 2]:
                # decoding fields continued for UART ports:
                # byte #1 is reserved
                tx_ready = msg['payload'][2:4]
                mode = msg['payload'][4:8]
                baudrate = int.from_bytes(msg['payload'][8:12], 'little', signed=False)
                in_proto_mask = msg['payload'][12:14]
                out_proto_mask = msg['payload'][14:16]
                # bytes #16..#20 are reserved
                print(f"      Port ID:        #{port_id}", end="")
                if port_id == self.io_target:
                    print("(*)")  # relevant for us
                else:
                    print()
                print(f"      TX ready:       {tx_ready}")
                print(f"      Mode:           {mode}")
                print(f"      Baudrate:       {baudrate} [Bits/s]")
                print(f"      In proto mask:  {in_proto_mask}")
                print(f"      Out proto mask: {out_proto_mask}")
                if port_id == self.io_target:
                    # send ACK-ACK here
                    if baudrate in self.baudrates_accepted:
                        self.send_ack_ack(msg['class'], msg['id'])
                        self.reconfig_baudrate(baudrate)
                        return None  # do not allow caller to send ACK-ACK again!
                    else:
                        return False  # caller shall send ACK-NAK due to unsupported baudrate
            else:
                # FIXME: "also" add support for other configuration units
                print(f"      Not decoding details for non-UART ports.")
        return True    # allow caller to send ACK-ACK

    def reconfig_baudrate(self, baudrate):
        self.ser.flush()
        print(f"!!! Reconfiguring serial's baudrate to {baudrate}")
        print()
        self.ser.baudrate = baudrate
        self.ser.reset_output_buffer()
        self.ser.reset_input_buffer()

    def has_valid_checksum(self, msg):
        # calculate checksum and verify (i.e. compare with received one)
        # print(f"  Checking message {msg} for valid checksum")
        calculated_checksum = self.calc_fletcher_checksum(msg['class'] + msg['id'] + msg['len_raw'] + msg['payload'])
        if calculated_checksum != msg['checksum']:
            # print("  Checksum mismatch!")
            # print(f"  Calculated checksum: {calculated_checksum}")
            # print(f"  Received checksum: {msg['checksum']}")
            return False
        else:
            return True

    def send_ack_ack(self, cls_id, msg_id):
        # create ACK-ACK packet with message-specific class and ID
        # (as reply to CFG input message)
        self.send_ack_or_nak(cls_id, msg_id, ack=True)

    def send_ack_nak(self, cls_id, msg_id):
        # create ACK-NAK packet with message-specific class and ID
        # (as reply to CFG input message)
        self.send_ack_or_nak(cls_id, msg_id, ack=False)

    def send_ack_or_nak(self, cls_id, msg_id, ack):
        # create ACK-ACK or ACK-NAK packet with message-specific class and ID
        # (as reply to CFG input message)
        sync = b'\xb5\x62'
        body = b'\x05'
        # use different IDs for ACK-ACK and ACK-NAK
        if ack:
            body += b'\x01'
        else:
            body += b'\x00'
        body += b'\x02\x00' + cls_id + msg_id
        cs = self.calc_fletcher_checksum(body)
        msg = sync + body + cs
        print(f"<<< Sending ACK-{'ACK' if ack else 'NAK'} response: {msg}")
        print()  # Improve readability of log by adding an empty line
        self.ser.write(msg)

    def send_nav_posllh(self,
                        time_of_week=None,
                        lon=0.0, lat=0.0,
                        height=0.0, hmsl=0.0,
                        hacc=0.0, vacc=0.0):
        # create NAV-POSLLH Geodetic Position Solution message
        # lon and lat are inputs in degrees, but as floats
        sync = b'\xb5\x62'
        msg = {'class': b'\x01', 'id': b'\x02'}
        body = msg['class'] + msg['id'] + b'\x1C\x00'  # length of inner payload is 28 bytes
        lon = int(lon * 1e7).to_bytes(4, 'little')
        lat = int(lat * 1e7).to_bytes(4, 'little')
        height = int(height * 1e3).to_bytes(4, 'little')  # from meters to cm
        hmsl = int(hmsl).to_bytes(4, 'little')  # from meters to cm
        hacc = int(hacc).to_bytes(4, 'little')
        vacc = int(vacc).to_bytes(4, 'little')
        if time_of_week is None:
            time_of_week = self.get_time_of_week()
        itow = time_of_week.to_bytes(4, 'little')
        body += itow + lon + lat + height + hmsl + hacc + vacc  # FIXME: not all fields are SIGNED integers!
        assert len(body) == (4+28), "Unexpected message body length."
        cs = self.calc_fletcher_checksum(body)
        msg['payload'] = sync + body + cs
        print(f"<<< Sending {self.get_msg_code(msg)} message: {msg['payload']}")
        print()  # Improve readability of log by adding an empty line
        self.ser.write(msg['payload'])

    def send_nav_dop(self,
                     time_of_week=None,
                     gdop=0,
                     pdop=0,
                     tdop=0,
                     vdop=0,
                     hdop=0,
                     ndop=0,
                     edop=0):
        sync = b'\xb5\x62'
        body = b'\x01\x04\x12\x00'  # length is 18 bytes
        gdop = int(gdop * 100).to_bytes(4, 'little')
        pdop = int(pdop * 100).to_bytes(4, 'little')
        tdop = int(tdop * 100).to_bytes(4, 'little')
        vdop = int(vdop * 100).to_bytes(4, 'little')
        hdop = int(hdop * 100).to_bytes(4, 'little')
        ndop = int(ndop * 100).to_bytes(4, 'little')
        edop = int(edop * 100).to_bytes(4, 'little')
        if time_of_week is None:
            time_of_week = self.get_time_of_week()
        itow = time_of_week.to_bytes(4, 'little')
        body += itow + gdop + pdop + tdop + vdop + hdop + edop  # FIXME: all fields are actually UNSIGNED integers!
        assert len(body) == 18, "Unexpected message body length."
        cs = self.calc_fletcher_checksum(body)
        msg = sync + body + cs
        print(f"<<< Sending {self.get_msg_code(msg)} message: {msg}")
        print()  # Improve readability of log by adding an empty line
        self.ser.write(msg)

    def send_nav_status(self,
                        time_of_week=None,
                        gps_fix=0,  # default: no fix
                        nav_status_flags=0,
                        fix_stat=0,
                        nav_status_flags2=0,
                        time_to_first_fix=0,
                        startup_time=0):
        sync = b'\xb5\x62'
        body = b'\x01\x03\x10\x00'  # message body length is 16 bytes
        gps_fix = int(gps_fix).to_bytes(4, 'little')
        nav_status_flags = int(nav_status_flags).to_bytes(1, 'little')
        fix_stat = int(fix_stat).to_bytes(1, 'little')
        nav_status_flags2 = int(nav_status_flags2).to_bytes(1, 'little')
        ttff = int(time_to_first_fix).to_bytes(4, 'little')
        msss = int(startup_time).to_bytes(4, 'little')
        if time_of_week is None:
            time_of_week = self.get_time_of_week()
        itow = time_of_week.to_bytes(4, 'little')
        body += itow + gps_fix + nav_status_flags + fix_stat + nav_status_flags2 + ttff + msss
        assert len(body) == 16, "Unexpected message body length."
        cs = self.calc_fletcher_checksum(body)
        msg = sync + body + cs
        print(f"<<< Sending {self.get_msg_code(msg)} message: {msg}")
        print()  # Improve readability of log by adding an empty line
        self.ser.write(msg)

    def send_nav_velned(self,
                        time_of_week=None,
                        vel_n=0,  # cm/s
                        vel_e=0,  # cm/s
                        vel_d=0,  # cm/s
                        speed=0,  # cm/s
                        ground_speed=0,  # cm/s
                        heading=0,  # deg
                        speed_acc_est=0,  # cm/s
                        heading_acc_est=0):  # deg
        sync = b'\xb5\x62'
        msg = {'class': b'\x01', 'id': b'\x12'}
        body = msg['class'] + msg['id'] + b'\x24\x00'  # length of inner payload is 36 bytes
        vel_n = int(vel_n).to_bytes(4, 'little')
        vel_e = int(vel_e).to_bytes(4, 'little')
        vel_d = int(vel_d).to_bytes(4, 'little')
        speed = int(speed).to_bytes(4, 'little')
        ground_speed = int(ground_speed).to_bytes(4, 'little')
        heading = int(heading * 1e5).to_bytes(4, 'little')
        speed_acc_est = int(speed_acc_est).to_bytes(4, 'little')
        heading_acc_est = int(heading_acc_est * 1e5).to_bytes(4, 'little')
        if time_of_week is None:
            time_of_week = self.get_time_of_week()
        itow = time_of_week.to_bytes(4, 'little')
        body += itow + vel_n + vel_e + vel_d + speed + ground_speed + heading
        body += speed_acc_est + heading_acc_est
        assert len(body) == (4+36), "Unexpected message body length."
        cs = self.calc_fletcher_checksum(body)
        msg['payload'] = sync + body + cs
        print(f"<<< Sending {self.get_msg_code(msg)} message: {msg['payload']}")
        print()  # Improve readability of log by adding an empty line
        self.ser.write(msg['payload'])

    def send_nav_timegps(self,
                         time_of_week=None,
                         frac_time_of_week=0,
                         week=0,
                         leap_secs=0,
                         valid=b'\x07',  # set time of week, week number and leap seconds to valid by default
                         time_acc_est=0):
        sync = b'\xb5\x62'
        msg = {'class': b'\x01', 'id': b'\x20'}
        body = msg['class'] + msg['id'] + b'\x10\x00'  # length of inner payload is 16 bytes
        if time_of_week is None:
            time_of_week = self.get_time_of_week()
        frac_time_of_week = int(frac_time_of_week).to_bytes(4, 'little')
        week = int(week).to_bytes(2, 'little')
        leap_secs = int(leap_secs).to_bytes(1, 'little')
        time_acc_est = int(time_acc_est).to_bytes(4, 'little')
        itow = time_of_week.to_bytes(4, 'little')
        body += itow + frac_time_of_week + week + leap_secs + valid + time_acc_est
        assert len(body) == (4+16), "Unexpected message body length."
        cs = self.calc_fletcher_checksum(body)
        msg['payload'] = sync + body + cs
        print(f"<<< Sending {self.get_msg_code(msg)} message: {msg['payload']}")
        print()  # Improve readability of log by adding an empty line
        self.ser.write(msg['payload'])

    def process_cfg_msg(self, msg):
        assert msg['class'] == b'\x06' and msg['id'] == b'\x01', "Unexpected call."
        payload_len = len(msg['payload'])
        assert payload_len in [2, 3, 8], f"Unexpected {self.get_msg_code(msg)} " \
                                         f"payload length (expecting 2, 3 or 8 bytes)."

        pl_msg_class = msg['payload'][0]
        pl_msg_id = msg['payload'][1]
        pl_rate = msg['payload'][2:]  # Send rate is relative to the event a message is registered on
        pl_msg = {'class': pl_msg_class.to_bytes(1, 'little'), 'id': pl_msg_id.to_bytes(1, 'little')}
        pl_msg_code = self.get_msg_code(pl_msg)
        print(f"    {self.get_msg_code(msg)} for class 0x{pl_msg_class:02X}, ID 0x{pl_msg_id:02X} ({pl_msg_code}).")
        if payload_len == 2:
            print("      Poll message configuration. (TODO)")
            # TODO: should queue reply with message configuration (ACK comes first)
            # self.queue_reply(msg)
        elif payload_len == 3:
            print(f"      Rate for current target: {pl_rate}")
            self.set_msg_rate(pl_msg_class, pl_msg_id, pl_rate)
        elif payload_len == 8:
            print(f"      Rates for 6 I/O targets: "
                  f"{pl_rate[0]}, "
                  f"{pl_rate[1]}{'(*)' if self.io_target == 1 else ''}, ",
                  f"{pl_rate[2]}{'(*)' if self.io_target == 2 else ''}, ",
                  f"{pl_rate[4]}, "
                  f"{pl_rate[4]}, "
                  f"{pl_rate[5]}")
            # (where #0=DDC/I2C, #1=UART1, #2=UART2, #3=USB, #4=SPI, #5=reserved for future use)

            # contains info for us for sure
            self.set_msg_rate(pl_msg_class, pl_msg_id, pl_rate[self.io_target])
        return True  # allow caller to send ACK-ACK

    def set_msg_rate(self, msg_class, msg_id, rate):
        # add or overwrite message rate for specific class and ID
        base_rate_millis = 1000  # assume a base rate of 1 Hz; actually store a "base period" of 1000 ms
        print(f"      Requested rate change: class=0x{msg_class:02X}, ID=0x{msg_id:02X}, rate={rate}")

        # check if message class is in dict, otherwise add it
        if msg_class not in self.message_rates:
            self.message_rates[msg_class] = dict()
        if msg_id not in self.message_rates[msg_class]:
            self.message_rates[msg_class][msg_id] = dict()
        self.message_rates[msg_class][msg_id]['rate'] = rate * base_rate_millis  # store "rate" (actually period in ms)
        # print(f"      Updated message rates to: {self.message_rates}")

    def check_cyclic_tx(self, millis, msg_class, msg_id):
        # message class and ID come in as 'bytes'
        msg_class = int.from_bytes(msg_class, 'little')
        msg_id = int.from_bytes(msg_id, 'little')

        if msg_class not in self.message_rates:
            return False
        if msg_id not in self.message_rates[msg_class]:
            return False
        if 'rate' not in self.message_rates[msg_class][msg_id]:
            return False
        if self.message_rates[msg_class][msg_id]['rate'] == 0:
            return False

        if 'last_cyclic_tx' not in self.message_rates[msg_class][msg_id]:
            # first transmission; make sure that the next check is true
            self.message_rates[msg_class][msg_id]['last_cyclic_tx'] = -self.message_rates[msg_class][msg_id]['rate']

        last = self.message_rates[msg_class][msg_id]['last_cyclic_tx']
        if millis >= last + self.message_rates[msg_class][msg_id]['rate']:
            print(f"... Going to send message with class=0x{msg_class:02X}, ID=0x{msg_id:02X}; "
                  f"last={(last-self.startup_time_millis)/1000:.3f} s, "
                  f"now={(millis-self.startup_time_millis)/1000:.3f} s")
            self.message_rates[msg_class][msg_id]['last_cyclic_tx'] = millis  # assume we directly send it
            return True  # ready to send
        else:
            return False

    def process_cfg_cfg(self, msg):
        assert msg['class'] == b'\x06' and msg['id'] == b'\x09', "Unexpected call."
        payload_len = len(msg['payload'])
        assert payload_len in [12, 13], f"Unexpected {self.get_msg_code(msg)} " \
                                        f"payload length (expecting 12 or 13 bytes)."

        pl_clear_mask = msg['payload'][0:4]
        pl_save_mask = msg['payload'][4:8]
        pl_load_mask = msg['payload'][8:12]
        pl_device_mask = None
        if payload_len == 13:
            pl_device_mask = msg['payload'][12]

        print(f"    {self.get_msg_code(msg)} (Clear, Save and Load configurations) ", end="")
        if pl_device_mask:
            print(f"with optional device mask: 0x{pl_device_mask:02X}.")
        else:
            print(f"w/o optional device mask.")
        print(f"      Clear mask: {pl_clear_mask}")
        print(f"      Save mask:  {pl_save_mask}")
        print(f"      Load mask:  {pl_load_mask}")
        return True  # allow caller to send ACK-ACK

    def process_cfg_sbas(self, msg):
        assert msg['class'] == b'\x06' and msg['id'] == b'\x16', "Unexpected call."
        payload_len = len(msg['payload'])
        assert payload_len in [0, 8], f"Unexpected {self.get_msg_code(msg)} payload length (expecting 0 or 8 bytes)."

        print(f"    {self.get_msg_code(msg)} (SBAS Configuration)")
        if payload_len == 0:
            print("      Poll SBAS configuration.")
            # TODO: should queue reply with SBAS configuration (ACK comes first)
            # self.queue_reply(msg)
        else:
            mode = msg['payload'][0]
            usage = msg['payload'][1]
            max_sbas = msg['payload'][2]
            scan_mode2 = msg['payload'][3]
            scan_mode1 = msg['payload'][4:8]
            print(f"      Mode:      0x{mode:02X}")
            print(f"      Usage:     0x{usage:02X}")
            print(f"      Max. SBAS: {max_sbas}")
            print(f"      scanmode2: {scan_mode2}")
            print(f"      scanmode1: {scan_mode1}")
        return True  # allow caller to send ACK-ACK

    def process_cfg_tp(self, msg):
        assert msg['class'] == b'\x06' and msg['id'] == b'\x07', "Unexpected call."
        payload_len = len(msg['payload'])
        assert payload_len in [0, 20], f"Unexpected {self.get_msg_code(msg)} payload length (expecting 12 or 13 bytes)."

        print(f"    {self.get_msg_code(msg)} (TimePulse Parameters)")
        if payload_len == 0:
            print("      Poll message configuration.")
            # TODO: should queue reply with message configuration (ACK comes first)
        else:
            interval = int.from_bytes(msg['payload'][0:4], 'little', signed=False)
            length = int.from_bytes(msg['payload'][4:8], 'little', signed=False)
            status = msg['payload'][8]  # FIXME: should be signed integer
            time_ref = msg['payload'][9]
            flags = msg['payload'][10]  # bitmask
            # byte #11 is reserved
            ant_cable_delay = int.from_bytes(msg['payload'][12:14], 'little', signed=True)
            rf_group_delay = int.from_bytes(msg['payload'][14:16], 'little', signed=True)
            user_delay = int.from_bytes(msg['payload'][16:20], 'little', signed=True)
            print(f"      Interval:          {interval} [us]")
            print(f"      Length:            {length} [us]")
            print(f"      Status:            {status}")
            print(f"      Time reference:    {time_ref}")
            print(f"      Flags:             0x{flags:02X}")
            print(f"        Sync mode:       {flags & 0x01}")
            print(f"      Ant. cable delay:  {ant_cable_delay} [ns]")
            print(f"      RX RF group delay: {rf_group_delay} [ns]")
            print(f"      User delay:        {user_delay} [ns]")
        return True  # allow caller to send ACK-ACK

    def process_cfg_nav5(self, msg):
        assert msg['class'] == b'\x06' and msg['id'] == b'\x24', "Unexpected call."
        payload_len = len(msg['payload'])
        assert payload_len in [0, 36], f"Unexpected {self.get_msg_code(msg)} payload length (expecting 0 or 36 bytes)."

        print(f"    {self.get_msg_code(msg)} (Navigation Engine Settings)")
        if payload_len == 0:
            print("      Poll message configuration.")
            # TODO: should queue reply with message configuration (ACK comes first)
        else:
            mask = msg['payload'][0:2]
            dyn_model = msg['payload'][2]
            fix_mode = msg['payload'][3]
            fixed_alt = msg['payload'][4:8]
            fixed_alt_var = msg['payload'][8:12]
            min_elev = msg['payload'][12]
            dr_limit = msg['payload'][13]
            pdop = msg['payload'][14:16]
            tdop = msg['payload'][16:18]
            pacc = msg['payload'][18:20]
            tacc = msg['payload'][20:22]
            static_hold_thres = msg['payload'][22]
            dgps_timeout = msg['payload'][23]
            # the remaining 12 bytes are currently marked reserved ("always set to zero")
            print(f"      Mask: {mask}")
            # TODO: continue...
        return True  # allow caller to send ACK-ACK

    def process_cfg_inf(self, msg):
        assert msg['class'] == b'\x06' and msg['id'] == b'\x02', "Unexpected call."
        payload_len = len(msg['payload'])
        assert payload_len in [1, 10, 20, 30, 40, 50, 60], \
            f"Unexpected {self.get_msg_code(msg)} payload length (expecting 1 or " \
            f"multiple of 10 bytes)."

        print(f"    {self.get_msg_code(msg)}")
        num_targets = payload_len // 10
        if payload_len == 1:
            protocol_id = msg['payload'][0]
            self.print_protocol_id(protocol_id)
            # TODO: this is a poll request, i.e. excepts an answer
            # self.queue_reply(msg)
        else:
            for target_id in range(0, num_targets):  # blocks for "I/O target" aka "configuration unit"
                print(f"      Target ID: #{target_id}", end="")
                if target_id == self.io_target:
                    print("      (*)")  # print marker that info is relevant for us; FIXME: do make use of it
                else:
                    print()
                protocol_id = msg['payload'][target_id*10 + 0]
                self.print_protocol_id(protocol_id)
                # inf_msg_msk = msg['payload'][target_id*10 + 4:(target_id+1)*10]  # 6 bytes
                inf_msg_msk = msg['payload'][target_id * 10 + 5]  # only 1 byte contains information
                enabled_info_msg = []
                disabled_info_msg = []
                if inf_msg_msk & 0x01 == 0x01:
                    enabled_info_msg.append('ERROR')
                else:
                    disabled_info_msg.append('ERROR')
                if inf_msg_msk & 0x02 == 0x02:
                    enabled_info_msg.append('WARNING')
                else:
                    disabled_info_msg.append('WARNING')
                if inf_msg_msk & 0x04 == 0x04:
                    enabled_info_msg.append('NOTICE')
                else:
                    disabled_info_msg.append('NOTICE')
                if inf_msg_msk & 0x08 == 0x08:
                    enabled_info_msg.append('DEBUG')
                else:
                    disabled_info_msg.append('DEBUG')
                if inf_msg_msk & 0x10 == 0x10:
                    enabled_info_msg.append('TEST')
                else:
                    disabled_info_msg.append('TEST')
                print(f"      Enabled messages:  {', '.join(enabled_info_msg) if enabled_info_msg else '(none)'}")
                print(f"      Disabled messages: {', '.join(disabled_info_msg) if disabled_info_msg else '(none)'}")
        return True  # allow caller to send ACK-ACK

    def process_cfg_rinv(self, msg):
        assert msg['class'] == b'\x06' and msg['id'] == b'\x34', "Unexpected call."
        payload_len = len(msg['payload'])
        assert payload_len == 0 or payload_len >= 2, "Unexpected payload length"

        print(f"    {self.get_msg_code(msg)} (remote inventory)")
        if payload_len == 0:
            print("    Poll request.")
            # TODO: should queue reply with message configuration (ACK comes first)
            # Note: the default is: flags=0x00, data="Notice: no data saved!"
            payload = b'\x00Notice: no data saved!'
            msg = {
                'class': msg['class'],
                'id': msg['id'],
                'payload': payload
            }
            self.queue_reply(msg)
        elif payload_len >= 2:
            flags = msg['payload'][0]
            data = msg['payload'][1:31]  # "If N is greater than 30, the excess bytes are discarded"
            is_binary = True if flags & 0x2 else False
            dump = True if flags & 0x1 else False  # dump data at startup (does not work if flag 'binary' is set)
            print(f"      Flags: binary={is_binary}, dump={dump}.")
            print(f"      Data: {data}")
            if not is_binary:
                print(f"      Data (textual): '{data.decode('ascii')}'")
        return True  # allow caller to send ACK-ACK

    def process_cfg_rst(self, msg):
        assert msg['class'] == b'\x06' and msg['id'] == b'\x04', "Unexpected call."
        payload_len = len(msg['payload'])
        assert payload_len == 4, "Unexpected payload length"

        print(f"    {self.get_msg_code(msg)} (reset receiver/ clear backup data structure command).")
        nav_bbr_mask = msg['payload'][0:2]
        nav_bbr_mask_special = ''
        # check three special values to append textual representation
        if nav_bbr_mask == b'\x00\x00':
            nav_bbr_mask_special = ' (hotstart)'
        elif nav_bbr_mask == b'\x00\x01':
            nav_bbr_mask_special = ' (warmstart)'
        elif nav_bbr_mask == b'\xff\xff':
            nav_bbr_mask_special = ' (coldstart)'
        reset_mode = msg['payload'][2]
        reserved1 = msg['payload'][3]
        print(f"      navBbrMask: {nav_bbr_mask}{nav_bbr_mask_special}")
        print(f"      resetMode:  {reset_mode}")
        print(f"      reserved1:  {reserved1}")
        return True  # allow caller to send ACK-ACK

    def process_mon_ver(self, msg):
        assert msg['class'] == b'\x0A' and msg['id'] == b'\x04', "Unexpected call."
        payload_len = len(msg['payload'])
        assert payload_len == 0, "Unexpected payload length"
        # or payload_len >= 70 -- nope, does not make sense to support a setter

        print(f"    {self.get_msg_code(msg)} (Receiver/Software/ROM Version, poll request)")
        # TODO: should queue reply with message configuration (ACK comes first)
        # sw_version = ... # 30 characters, NULL-terminated
        # hw_version = ... # 10 characters, NULL-terminated
        # rom_version = ... # 30 characters, NULL-terminated
        # extension = ... # optional extension data

    def process_aid_alpsrv(self, msg):
        assert msg['class'] == b'\x0B' and msg['id'] == b'\x32', "Unexpected call."
        payload_len = len(msg['payload'])
        assert payload_len >= 8, "Unexpected payload length (must be >=8 bytes)"
        print(f"    {self.get_msg_code(msg)} (ALP server/client AlmanacPlus data; TODO)")
        # TODO/FIXME

    def process_aid_alp(self, msg):
        assert msg['class'] == b'\x0b' and msg['id'] == b'\x50', "Unexpected call."
        payload_len = len(msg['payload'])
        assert payload_len % 2 == 0 or payload_len == 1, "Unexpected payload length (must be even-sized or 1)"
        assert payload_len <= 700, "Payload too large"  # would exceed the receiver's internal buffering capabilities

        print(f"    {self.get_msg_code(msg)} (ALP file data transfer to the receiver)")
        if payload_len == 1:
            assert(msg['payload'][0] == b'\x00')
            print("      Marking end of transfer.")
        else:
            print(f"      ALP file data: {msg['payload']}")


def run():
    baudrates_accepted = [4800, 9600, 19200, 38400, 57600, 115200]
    baudrate_default = 9600

    io_targets_accepted = [1, 2]
    io_target_default = 1

    # blocking time (in seconds) for every blocking read; has influence of the jitter of the periodic transmits
    # (as this script is currently single-threaded and switches between receiving and transmitting)
    blocking_read_timeout = 0.03

    parser = argparse.ArgumentParser(description='%(prog)s '
                                                 'Run simulated UBX GPX receiver.')

    parser.add_argument(dest='serial_port_name',
                        help='Serial port name')

    parser.add_argument('-b', '--serial-baudrate',
                        type=int,
                        help='Serial baudrate with which the simulator is accessed initially '
                             f"(default: {baudrate_default}, "
                             f"possible: {', '.join(str(b) for b in baudrates_accepted)})",
                        default=baudrate_default)

    # "A target in the context of the I/O system is an I/O port."
    parser.add_argument('-t', '--io-target',
                        type=int,
                        help='I/O target ID '
                             f"(default: {io_target_default}, "
                             f"possible: {', '.join(str(t) for t in io_targets_accepted)})",
                        default=io_target_default)

    args = parser.parse_args()

    assert args.serial_baudrate in baudrates_accepted, "Invalid baudrate selected."
    assert args.io_target in io_targets_accepted, "Invalid I/O target selected."

    simulator = UbxGpsSimulator(serial_port_name=args.serial_port_name,
                                serial_baudrate=args.serial_baudrate,
                                serial_baudrates_accepted=baudrates_accepted,
                                serial_blocking_read_timeout=blocking_read_timeout,
                                io_target=args.io_target)
    simulator.run()


if __name__ == '__main__':
    run()
