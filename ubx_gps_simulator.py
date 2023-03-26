import argparse
import serial
import pendulum
from enum import Enum

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


def calc_checksum(block):
    # calculate checksum using 8 bit Fletcher algorithm
    ck_a = 0
    ck_b = 0
    # print(f"  Calculating checksum for block {block}")
    for b in block:
        byte_val = b  # struct.unpack('B', b)[0]
        ck_a += byte_val
        ck_a = ck_a & 0xFF
        ck_b += ck_a
        ck_b = ck_b & 0xFF
        # print(f"  Byte value: {byte_val} (0x{byte_val:02X}), CK_A: {ck_a}
        # (0x{ck_a:02X}), CK_B: {ck_b} (0x{ck_b:02X})")
    return ck_a.to_bytes(1, 'little') + ck_b.to_bytes(1, 'little')


def has_valid_checksum(msg):
    # calculate checksum and verify (i.e. compare with received one)
    # print(f"  Checking message {msg} for valid checksum")
    calculated_checksum = calc_checksum(msg['class'] + msg['id'] + msg['len_raw'] + msg['payload'])
    if calculated_checksum != msg['checksum']:
        # print("  Checksum mismatch!")
        # print(f"  Calculated checksum: {calculated_checksum}")
        # print(f"  Received checksum: {msg['checksum']}")
        return False
    else:
        return True


def send_ack_ack(ser, cls_id, msg_id):
    # create ACK-ACK packet with message-specific class and ID
    # (as reply to CFG input message)
    send_ack_or_nak(ser, cls_id, msg_id, ack=True)


def send_ack_nak(ser, cls_id, msg_id):
    # create ACK-NAK packet with message-specific class and ID
    # (as reply to CFG input message)
    send_ack_or_nak(ser, cls_id, msg_id, ack=False)


def send_ack_or_nak(ser, cls_id, msg_id, ack):
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
    cs = calc_checksum(body)
    msg = sync + body + cs
    print(f"<<< Sending ACK-{'ACK' if ack else 'NAK'} response: {msg}")
    print()  # Improve readability of log by adding an empty line
    ser.write(msg)


def get_time_of_week(timestamp=None):
    # calculate "GPS Millisecond Time of Week" ('itow')
    # from timestamp or for just now
    if timestamp is None:
        timestamp = pendulum.now()
    time_of_week = int(timestamp.format('x')) - int(timestamp.start_of('week').format('x'))
    return time_of_week


def send_nav_posllh(ser,
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
        time_of_week = get_time_of_week()
    itow = time_of_week.to_bytes(4, 'little')
    body += itow + lon + lat + height + hmsl + hacc + vacc  # FIXME: not all fields are SIGNED integers!
    assert len(body) == (4+28), "Unexpected message body length."
    cs = calc_checksum(body)
    msg['payload'] = sync + body + cs
    print(f"<<< Sending {get_msg_code(msg)} message: {msg['payload']}")
    print()  # Improve readability of log by adding an empty line
    ser.write(msg['payload'])


def send_nav_dop(ser,
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
        time_of_week = get_time_of_week()
    itow = time_of_week.to_bytes(4, 'little')
    body += itow + gdop + pdop + tdop + vdop + hdop + edop  # FIXME: all fields are actually UNSIGNED integers!
    assert len(body) == 18, "Unexpected message body length."
    cs = calc_checksum(body)
    msg = sync + body + cs
    print(f"<<< Sending {get_msg_code(msg)} message: {msg}")
    print()  # Improve readability of log by adding an empty line
    ser.write(msg)


def send_nav_status(ser,
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
        time_of_week = get_time_of_week()
    itow = time_of_week.to_bytes(4, 'little')
    body += itow + gps_fix + nav_status_flags + fix_stat + nav_status_flags2 + ttff + msss
    assert len(body) == 16, "Unexpected message body length."
    cs = calc_checksum(body)
    msg = sync + body + cs
    print(f"<<< Sending {get_msg_code(msg)} message: {msg}")
    print()  # Improve readability of log by adding an empty line
    ser.write(msg)


def send_nav_velned(ser,
                    time_of_week=None,
                    vel_n=0,
                    vel_e=0,
                    vel_d=0,
                    speed=0,
                    ground_speed=0,
                    heading=0,
                    speed_acc_est=0,
                    heading_acc_est=0):
    sync = b'\xb5\x62'
    body = b'\x01\x12\x24\x00'  # message body length is 36 bytes
    vel_n = int(vel_n).to_bytes(4, 'little')
    vel_e = int(vel_e).to_bytes(4, 'little')
    vel_d = int(vel_d).to_bytes(4, 'little')
    speed = int(speed).to_bytes(4, 'little')
    ground_speed = int(ground_speed).to_bytes(4, 'little')
    heading = int(heading * 1e5).to_bytes(4, 'little')
    speed_acc_est = int(speed_acc_est).to_bytes(4, 'little')
    heading_acc_est = int(heading_acc_est * 1e5).to_bytes(4, 'little')
    if time_of_week is None:
        time_of_week = get_time_of_week()
    itow = time_of_week.to_bytes(4, 'little')
    body += itow + vel_n + vel_e + vel_d + speed + ground_speed + heading
    body += speed_acc_est + heading_acc_est
    assert len(body) == 36, "Unexpected message body length."
    cs = calc_checksum(body)
    msg = sync + body + cs
    print(f"<<< Sending {get_msg_code(msg)} message: {msg}")
    print()  # Improve readability of log by adding an empty line
    ser.write(msg)


def send_nav_timegps(ser,
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
        time_of_week = get_time_of_week()
    frac_time_of_week = int(frac_time_of_week).to_bytes(4, 'little')
    week = int(week).to_bytes(2, 'little')
    leap_secs = int(leap_secs).to_bytes(1, 'little')
    time_acc_est = int(time_acc_est).to_bytes(4, 'little')
    itow = time_of_week.to_bytes(4, 'little')
    body += itow + frac_time_of_week + week + leap_secs + valid + time_acc_est
    assert len(body) == (4+16), "Unexpected message body length."
    cs = calc_checksum(body)
    msg['payload'] = sync + body + cs
    print(f"<<< Sending {get_msg_code(msg)} message: {msg['payload']}")
    print()  # Improve readability of log by adding an empty line
    ser.write(msg['payload'])


# def send_mon_hw(ser):
#    # pin_sel = ...


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


def process_message(ser, msg):
    # process message, i.e.
    # - decode class and ID to a human-readable code
    # - decode single messages in more detail
    # - reply with ACK-ACK messages to CFG-* messages

    # handle specific messages
    if msg['class'] == b'\x06':
        # "Configuration Input Messages: Set Dynamic Model, Set DOP Mask,
        #  Set Baud Rate, etc."
        # "The CFG Class can be used to configure the receiver and read out
        #  current configuration values. Any messages in Class CFG sent to the
        #  receiver are acknowledged (with Message ACK-ACK) if processed
        #  successfully, and rejected (with Message ACK-NAK) if processing the
        #  message failed."
        if msg['id'] == b'\x00':
            process_cfg_prt(msg, ser)
        elif msg['id'] == b'\x01':
            process_cfg_msg(msg)
        elif msg['id'] == b'\x02':
            process_cfg_inf(msg)
        elif msg['id'] == b'\x04':
            process_cfg_rst(msg)
        elif msg['id'] == b'\x06':
            process_cfg_cfg(msg)
        elif msg['id'] == b'\x07':
            process_cfg_tp(msg)
        elif msg['id'] == b'\x24':
            process_cfg_nav5(msg)
        elif msg['id'] == b'\x34':
            process_cfg_rinv(msg)
        else:
            print(f"    {get_msg_code(msg)}")

        # always send ACK-ACK (for now); FIXME: may want to implement different behaviour
        send_ack_ack(ser, msg['class'], msg['id'])
    elif msg['class'] == b'\x0a' and msg['id'] == b'\x04':
        process_mon_ver(msg)
    # elif msg['class'] == b'\x0b' and msg['id'] == b'\x01':
    #    process_aid_ini(msg)
    # elif msg['class'] == b'\x0b' and msg['id'] == b'\x32':
    #    process_aid_alpsrv(msg)
    elif msg['class'] == b'\x0b' and msg['id'] == b'\x50':
        process_aid_alp(msg)
        send_ack_ack(ser, msg['class'], msg['id'])  # allow to send next chunk directly
    else:
        print(f"    {get_msg_code(msg)} (unhandled)")
        print()  # Improve readability of log by adding an empty line


def process_cfg_prt(msg, ser):
    assert msg['class'] == b'\x06' and msg['id'] == b'\x00', "Unexpected call."
    payload_len = len(msg['payload'])
    assert payload_len in [0, 1, 20], "Unexpected CFG-MSG payload length (expecting 0, 1 or 20 bytes)."
    # FIXME: possibly also multiple of 20 bytes (i.e. multiple 'configuration units')

    if payload_len == 0:
        print("      Poll the configuration of the used I/O Port.")
        # TODO: should queue reply with message configuration (ACK comes first)
    elif payload_len == 1:
        print("      Poll the configuration of one I/O Port.")
        # TODO: should queue reply with message configuration (ACK comes first)
    else:
        port_id = msg['payload'][0]  # single element is interpeted as integer in the range 0..255 by default
        if port_id in [1, 2]:
            # decoding fields continued for UART ports:
            # byte #1 is reserved
            tx_ready = msg['payload'][2:4]
            mode = msg['payload'][4:8]
            baudrate = int.from_bytes(msg['payload'][8:12], 'little', signed=False)
            in_proto_mask = msg['payload'][12:14]
            out_proto_mask = msg['payload'][14:16]
            # bytes #16..#20 are reserved
            print(f"      Port ID:        #{port_id}")
            print(f"      TX ready:       {tx_ready}")
            print(f"      Mode:           {mode}")
            print(f"      Baudrate:       {baudrate} [Bits/s]")
            print(f"      In proto mask:  {in_proto_mask}")
            print(f"      Out proto mask: {out_proto_mask}")
            # FIXME: make this dynamic and do not assert that we're always on port #1
            #        (this should be a command line argument, and there should be an OOP approach)
            if port_id == 1:
                reconfig_baudrate(ser, baudrate)  # FIXME: should send ACK first!
        else:
            # FIXME: "also" add support for other configuration units
            print(f"      Not decoding details for non-UART ports.")


def reconfig_baudrate(ser, baudrate):
    # FIXME: do not duplicate list of accepted baudrates!
    baudrates_accepted = [4800, 9600, 19200, 38400, 57600, 115200]
    if baudrate in baudrates_accepted:
        ser.flush()
        print(f"!!! Reconfiguring serial's baudrate to {baudrate}")
        ser.baudrate = baudrate
        ser.reset_input_buffer()


def process_cfg_msg(msg):
    assert msg['class'] == b'\x06' and msg['id'] == b'\x01', "Unexpected call."
    payload_len = len(msg['payload'])
    assert payload_len in [2, 3, 8], "Unexpected CFG-MSG payload length (expecting 2, 3 or 8 bytes)."

    pl_msg_class = msg['payload'][0]
    pl_msg_id = msg['payload'][1]
    pl_rate = msg['payload'][2:]  # Send rate is relative to the event a message is registered on
    pl_msg = {'class': pl_msg_class.to_bytes(1, 'little'), 'id': pl_msg_id.to_bytes(1, 'little')}
    pl_msg_code = get_msg_code(pl_msg)
    print(f"    {get_msg_code(msg)} for class 0x{pl_msg_class:02X}, ID 0x{pl_msg_id:02X} ({pl_msg_code}).")
    if payload_len == 2:
        print("      Poll message configuration.")
        # TODO: should queue reply with message configuration (ACK comes first)
    elif payload_len == 3:
        print(f"      Rate for current target: {pl_rate}")
        set_msg_rate(pl_msg_class, pl_msg_id, pl_rate)
    elif payload_len == 8:
        print(f"      Rates for 6 I/O targets: {pl_rate[0]}, {pl_rate[1]}(*), {pl_rate[2]},"
              f" {pl_rate[4]}, {pl_rate[4]}, {pl_rate[5]}")
        # (where #0=DDC/I2C, #1=UART1, #2=UART2, #3=USB, #4=SPI, #5=reserved for future use)
        # FIXME: select for the target we are currently running (assue #1)
        set_msg_rate(pl_msg_class, pl_msg_id, pl_rate[1])


def set_msg_rate(msg_class, msg_id, rate):
    # FIXME: implement
    return


def process_cfg_cfg(msg):
    assert msg['class'] == b'\x06' and msg['id'] == b'\x09', "Unexpected call."
    payload_len = len(msg['payload'])
    assert payload_len in [12, 13], "Unexpected CFG-CFG payload length (expecting 12 or 13 bytes)."

    pl_clear_mask = msg['payload'][0:4]
    pl_save_mask = msg['payload'][4:8]
    pl_load_mask = msg['payload'][8:12]
    pl_device_mask = None
    if payload_len == 13:
        pl_device_mask = msg['payload'][12]

    print(f"    {get_msg_code(msg)} (Clear, Save and Load configurations) ", end="")
    if pl_device_mask:
        print(f"with optional device mask: 0x{ord(pl_device_mask):02X}.")
    else:
        print(f"w/o optional device mask.")
    print(f"      Clear mask: {pl_clear_mask}")
    print(f"      Save mask:  {pl_save_mask}")
    print(f"      Load mask:  {pl_load_mask}")


def process_cfg_tp(msg):
    assert msg['class'] == b'\x06' and msg['id'] == b'\x07', "Unexpected call."
    payload_len = len(msg['payload'])
    assert payload_len in [0, 20], "Unexpected CFG-CFG payload length (expecting 12 or 13 bytes)."

    print(f"    {get_msg_code(msg)} (TimePulse Parameters)")
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
        print(f"      Time reference:    {length}")
        print(f"      Flags:             0x{flags:02X}")
        print(f"        Sync mode:       {flags & 0x01}")
        print(f"      Ant. cable delay:  {ant_cable_delay} [ns]")
        print(f"      RX RF group delay: {rf_group_delay} [ns]")
        print(f"      User delay:        {user_delay} [ns]")


def process_cfg_nav5(msg):
    assert msg['class'] == b'\x06' and msg['id'] == b'\x24', "Unexpected call."
    payload_len = len(msg['payload'])
    assert payload_len in [0, 36], "Unexpected CFG-CFG payload length (expecting 0 or 36 bytes)."

    print(f"    {get_msg_code(msg)} (Navigation Engine Settings)")
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


def print_protocol_id(identifier):
    print("        Protocol ID: ", end="")
    if identifier == 0:
        print("UBX Protocol")
    elif identifier == 1:
        print("NMEA Protocol")
    else:
        print("Reserved")


def process_cfg_inf(msg):
    assert msg['class'] == b'\x06' and msg['id'] == b'\x02', "Unexpected call."
    payload_len = len(msg['payload'])
    assert payload_len in [1, 10, 20, 30, 40, 50, 60], \
        f"Unexpected {get_msg_code(msg)} payload length (expecting 1 or " \
        f"multiple of 10 bytes)."

    print(f"    {get_msg_code(msg)}")
    num_targets = payload_len // 10
    if payload_len == 1:
        protocol_id = msg['payload'][0]
        print_protocol_id(protocol_id)
        # TODO: this is a poll request, i.e. excepts an answer
    else:
        for target_id in range(0, num_targets):  # blocks for "I/O target" aka "configuration unit"
            print(f"      Target ID: #{target_id}")
            protocol_id = msg['payload'][target_id*10 + 0]
            print_protocol_id(protocol_id)
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


def process_cfg_rinv(msg):
    assert msg['class'] == b'\x06' and msg['id'] == b'\x34', "Unexpected call."
    payload_len = len(msg['payload'])
    assert payload_len == 0 or payload_len >= 2, "Unexpected payload length"

    print(f"    {get_msg_code(msg)} (remote inventory) ", end="")
    if payload_len == 0:
        print("Poll request.")
        # TODO: should queue reply with message configuration (ACK comes first)
        # Note: the default is: flags=0x00, data="Notice: no data saved!"
    elif payload_len >= 2:
        flags = msg['payload'][0]
        data = msg['payload'][1:31]  # "If N is greater than 30, the excess bytes are discarded"
        is_binary = True if flags & 0x2 else False
        dump = True if flags & 0x1 else False  # dump data at startup (does not work if flag 'binary' is set)
        print(f"      Flags: binary={is_binary}, dump={dump}. ", end="")
        print(f"      Data: {data}")
        if not is_binary:
            print(f"      Data (textual): {data.decode('ascii')}")


def process_cfg_rst(msg):
    assert msg['class'] == b'\x06' and msg['id'] == b'\x04', "Unexpected call."
    payload_len = len(msg['payload'])
    assert payload_len == 4, "Unexpected payload length"

    print(f"    {get_msg_code(msg)} (reset receiver/ clear backup data structure command).")
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


def process_mon_ver(msg):
    assert msg['class'] == b'\x0A' and msg['id'] == b'\x04', "Unexpected call."
    payload_len = len(msg['payload'])
    assert payload_len == 0, "Unexpected payload length"
    # or payload_len >= 70 -- nope, does not make sense to support a setter

    print(f"    {get_msg_code(msg)} (Receiver/Software/ROM Version, poll request)")
    # TODO: should queue reply with message configuration (ACK comes first)
    # sw_version = ... # 30 characters, NULL-terminated
    # hw_version = ... # 10 characters, NULL-terminated
    # rom_version = ... # 30 characters, NULL-terminated
    # extension = ... # optional extension data


def process_aid_alpsrv(msg):
    assert msg['class'] == b'\x0B' and msg['id'] == b'\x32', "Unexpected call."
    payload_len = len(msg['payload'])
    assert payload_len >= 8, "Unexpected payload length (must be >=8 bytes)"
    print(f"    {get_msg_code(msg)} (ALP server/client AlmanacPlus data; TODO)")
    # TODO/FIXME


# def process_aid_ini(msg):
#    assert msg['class'] == b'\x0B' and msg['id'] == b'\x01', "Unexpected call."


def process_aid_alp(msg):
    assert msg['class'] == b'\x0b' and msg['id'] == b'\x50', "Unexpected call."
    payload_len = len(msg['payload'])
    assert payload_len % 2 == 0 or payload_len == 1, "Unexpected payload length (must be even-sized or 1)"
    assert payload_len <= 700, "Payload too large"  # would exceed the receiver's internal buffering capabilities

    print(f"    {get_msg_code(msg)} (ALP file data transfer to the receiver)")
    if payload_len == 1:
        assert(msg['payload'][0] == b'\x00')
        print("      Marking end of transfer.")
    else:
        print(f"      ALP file data: {msg['payload']}")


def run():
    baudrates_accepted = [4800, 9600, 19200, 38400, 57600, 115200]
    baudrate_default = 9600
    target_ids_accepted = [1, 2]  # FIXME: currently unused
    target_id_default = 1  # FIXME: currently unused
    blocking_read_timeout = 0.05  # in seconds; this blocking time has influence of the jitter of the periodic transmits (as this script is currently single-threaded and switches between receiving and transmitting)
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

    # Not used yet (FIXME)
    # parser.add_argument('-t', '--io-target',
    #                    type=int,
    #                    help='I/O target ID '
    #                         f"(default: {target_id_default}, "
    #                         f"possible: {', '.join(str(t) for t in target_ids_accepted)})",
    #                    default=target_id_default)

    args = parser.parse_args()

    assert args.serial_baudrate in baudrates_accepted, "Invalid baudrate selected."

    # From the specification, section about "UART Ports":
    # "The serial ports consist of an RX and a TX line.
    #  Neither handshaking signals nor hardware flow control signals are available."
    # Configuration must be 8N1, but different baud rates are possible.
    ser = serial.Serial(port=args.serial_port_name,
                        baudrate=args.serial_baudrate,
                        timeout=blocking_read_timeout)
    print(f"Opened serial port '{ser.name}' with a baudrate of {ser.baudrate}.")
    # print(ser)
    use_mock = False
    # rx_mock_data = b"\xb5\x62\x06\x34\x00\x00\x3a\x40\xff\x1b\xad\x1d\xea\xc0\xff\xee\xb5"
    # for rx_byte in rx_mock_data:

    last_tx_time_millis = None
    startup_time = pendulum.now().microsecond

    # run the state machine, receiving and processing byte by byte;
    # please note that this script runs single-threaded and does both RX and TX
    rx_state = RxState.WAIT_SYNC_1
    msg = {}
    rx_byte = None
    while True:
        if use_mock:
            rx_byte = rx_byte.to_bytes(1, 'little')
        else:
            rx_byte = ser.read()
        # check if timeout has occurred or if a byte has been received
        # TODO: move this into a less complex part of code (state machine driver)
        if rx_byte:
            # print(f"Rx'ed character: {rx_byte}. Receiver in state: '{rx_state}' (Type: {type(rx_byte)}).")
            if rx_state == RxState.WAIT_SYNC_1:
                if rx_byte == b'\xb5':
                    # print("Found 1st sync byte.")
                    rx_state = RxState.WAIT_SYNC_2
                else:
                    # print("Did not find 1st sync byte.")
                    rx_state = RxState.WAIT_SYNC_1
            elif rx_state == RxState.WAIT_SYNC_2:
                if rx_byte == b'\x62':
                    # print("Found sync bytes (start of message).")
                    rx_state = RxState.WAIT_MSG_CLASS
                else:
                    rx_state = RxState.WAIT_SYNC_1
            elif rx_state == RxState.WAIT_MSG_CLASS:
                msg = {
                    'class': rx_byte,
                    'id': None,
                    'len_raw': None,
                    'remaining_len': 0,
                    'payload': b'',
                    'checksum': None
                }
                rx_state = RxState.WAIT_MSG_ID
            elif rx_state == RxState.WAIT_MSG_ID:
                msg['id'] = rx_byte
                rx_state = RxState.WAIT_LENGTH_1
            elif rx_state == RxState.WAIT_LENGTH_1:
                msg['len_raw'] = rx_byte
                rx_state = RxState.WAIT_LENGTH_2
            elif rx_state == RxState.WAIT_LENGTH_2:
                msg['len_raw'] += rx_byte
                # recalculate length from the two bytes
                remaining_len = int.from_bytes(msg['len_raw'], 'little', signed=False)
                # print(f"Expecting {remaining_len} payload bytes in message.")
                msg['remaining_len'] = remaining_len
                if remaining_len > 0:
                    rx_state = RxState.WAIT_PAYLOAD_CPLT
                else:
                    # skipping payload
                    rx_state = RxState.WAIT_CHECKSUM_START
            elif rx_state == RxState.WAIT_PAYLOAD_CPLT:
                msg['remaining_len'] -= 1
                msg['payload'] += rx_byte
                if msg['remaining_len'] <= 0:
                    rx_state = RxState.WAIT_CHECKSUM_START
            elif rx_state == RxState.WAIT_CHECKSUM_START:
                # here comes the first byte of the checksum
                msg['checksum'] = rx_byte
                rx_state = RxState.WAIT_MSG_CPLT
            elif rx_state == RxState.WAIT_MSG_CPLT:
                msg['checksum'] += rx_byte
                # print(f"Message checksum: {msg['checksum']}")
                if has_valid_checksum(msg):
                    print(f">>> Received VALID message: class 0x{ord(msg['class']):02X}, "
                          f"ID 0x{ord(msg['id']):02X} ", end="")
                    if msg['payload'] == b'':
                        print(f"w/o payload.")
                    else:
                        print(f"w/ payload {msg['payload']} (length: {len(msg['payload'])}).")
                    process_message(ser, msg)
                else:
                    print(f"!!! Received INVALID message: {msg}.")
                rx_state = RxState.WAIT_SYNC_1
            # print(f"  Processed the byte. Next state: {rx_state}")
        # else:
        #    print("Timeout? Could not read a single byte!")

        # make sure to transmit after having processed the received message as
        # this can have triggered some direct transmissions
        # (ACK-ACK, ACK-NAK, replies to poll requests)

        # TODO: processed queued transmissions

        # handle cyclic transmissions
        do_cyclic_transmit = False
        transmit_period = 1e3  # milliseconds, i.e. 1 second; TODO/FIXME: use dynamic rates for every message ID!
        # TODO/FIXME: check for time and if some message countdowns have elapsed
        #             depending on their rates and cyclic data needs to be sent
        current_time = pendulum.now()
        current_time_millis = int(current_time.format('x'))  # cannot just use the attribute 'microsends' due to wrap-around
        current_time_of_week = get_time_of_week(current_time)

        if last_tx_time_millis is not None:
            time_diff = current_time_millis - last_tx_time_millis
            if time_diff >= transmit_period:
                do_cyclic_transmit = True
        else:
            # there is no last time; so let's start with the first time to transmit something
            do_cyclic_transmit = True

        # FIXME: actually the following cyclic transmission is prepared;
        #        BUT: do not send "unreqeusted" messages yet without having rates properly configured!
        if False:  # do_cyclic_transmit:
            print(f"[{current_time.format('HH:mm:ss')}.{current_time.microsecond // 1000:03}] Cyclic transmit!")
            print()

            send_nav_posllh(ser,
                            current_time_of_week,
                            lon=11.574444, lat=48.139722,
                            height=519.0, hmsl=519.0,
                            hacc=0, vacc=0)
            # - send_nav_dop(ser)
            # - send_nav_status(ser)
            # - send_nav_velned(ser)
            # - send_nav_sol(ser)  # FIXME: not implemented yet
            send_nav_timegps(ser,
                             current_time_of_week,
                             frac_time_of_week=0,
                             week=current_time.week_of_year)
            # - send_nav_timeutc(ser)  # FIXME: not implemented yet
            # - send_mon_hw(ser)  # FIXME: not implemented yet

            last_tx_time_millis = current_time_millis  # just "now"
    print("Done.")


if __name__ == '__main__':
    run()
