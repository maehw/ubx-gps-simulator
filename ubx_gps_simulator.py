import argparse
import serial
from enum import Enum

messages = {
    b'\x01': {
        'class_name': 'NAV',
        b'\x01': {'code': 'POSECEF'},
        b'\x02': {'code': 'POSLLH'},
        b'\x03': {'code': 'STATUS'},
        b'\x04': {'code': 'DOP'},
        b'\x06': {'code': 'SOL'},
        b'\x11': {'code': 'VELECEF'},
        b'\x12': {'code': 'VELNED'},
        b'\x20': {'code': 'TIMEGPS'},
        b'\x21': {'code': 'TIMEUTC'},
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
        b'\x00': {'code': 'PRT'},
        b'\x01': {'code': 'MSG'},
        b'\x02': {'code': 'INF'},
        b'\x04': {'code': 'RST'},
        b'\x06': {'code': 'DAT'},
        b'\x07': {'code': 'TP'},
        b'\x08': {'code': 'RATE'},
        b'\x09': {'code': 'CFG'},
        b'\x0E': {'code': 'FXN'},
        b'\x11': {'code': 'RXM'},
        b'\x12': {'code': 'EKF'},
        b'\x13': {'code': 'ANT'},
        b'\x16': {'code': 'SBAS'},
        b'\x17': {'code': 'NMEA'},
        b'\x1B': {'code': 'USB'},
        b'\x1D': {'code': 'TMODE'},
        b'\x22': {'code': 'NVS'},
        b'\x23': {'code': 'NAVX5'},
        b'\x24': {'code': 'NAV5'},
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
        b'\x04': {'code': 'VER'},
        b'\x06': {'code': 'MSGPP'},
        b'\x07': {'code': 'RXBUF'},
        b'\x08': {'code': 'TXBUF'},
        b'\x09': {'code': 'HW'},
        b'\x0B': {'code': 'HW2'},
        b'\x21': {'code': 'RXR'},
    },
    b'\x0B': {
        'class_name': 'AID',
        b'\x00': {'code': 'REQ'},
        b'\x01': {'code': 'INI'},
        b'\x02': {'code': 'HUI'},
        b'\x10': {'code': 'DATA'},
        b'\x30': {'code': 'ALM'},
        b'\x31': {'code': 'EPH'},
        b'\x32': {'code': 'ALPSRV'},
        b'\x33': {'code': 'AOP'},
        b'\x50': {'code': 'ALP'},
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
    sync = b'\xb5\x62'
    body = b'\x05\x01\x02\x00' + cls_id + msg_id
    cs = calc_checksum(body)
    msg = sync + body + cs
    print(f"<<< Sending ACK-ACK response: {msg}")
    print()  # Improve readability of log by adding an empty line
    ser.write(msg)


def get_msg_code(msg):
    code = ''
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
        # Set Baud Rate, etc."
        # "The CFG Class can be used to configure the receiver and read out
        # current configuration values. Any messages in Class CFG sent to the
        # receiver are acknowledged (with Message ACK-ACK) if processed
        # successfully, and rejected (with Message ACK-NAK) if processing the
        # message failed."
        # always send ACK-ACK (for now); FIXME: may want to implement different behaviour
        if msg['id'] == b'\x01':
            process_cfg_msg(msg)
        elif msg['id'] == b'\x04':
            process_cfg_rst(msg)
        elif msg['id'] == b'\x34':
            process_cfg_rinv(msg)
        else:
            print(f"    {get_msg_code(msg)}")
        send_ack_ack(ser, msg['class'], msg['id'])
    elif msg['class'] == b'\x0b' and msg['id'] == b'\x50':
        process_aid_alp(msg)
        send_ack_ack(ser, msg['class'], msg['id'])  # allow to send next chunk directly
    else:
        print(f"    {get_msg_code(msg)}")
        print()  # Improve readability of log by adding an empty line


def process_cfg_msg(msg):
    assert msg['class'] == b'\x06' and msg['id'] == b'\x01', "Unexpected call."
    payload_len = len(msg['payload'])
    assert payload_len in [2, 3, 8], "Unexpected CFG-MSG payload length (expecting 2, 3 or 8 bytes)."

    pl_msg_class = msg['payload'][0]
    pl_msg_id = msg['payload'][1]
    pl_rate = msg['payload'][2:]
    pl_msg = {'class': pl_msg_class.to_bytes(1, 'little'), 'id': pl_msg_id.to_bytes(1, 'little')}
    pl_msg_code = get_msg_code(pl_msg)
    print(f"    {get_msg_code(msg)} for class 0x{pl_msg_class:02X}, ID 0x{pl_msg_id:02X} ({pl_msg_code}).")
    if payload_len == 2:
        print("      Poll request.")
    elif payload_len == 3:
        print(f"      Rate for current target: {pl_rate}")
    elif payload_len == 8:
        print(f"      Rates for 6 I/O targets: {pl_rate}")


def process_cfg_rinv(msg):
    assert msg['class'] == b'\x06' and msg['id'] == b'\x34', "Unexpected call."
    payload_len = len(msg['payload'])
    assert payload_len == 0 or payload_len >= 2, "Unexpected payload length"

    print(f"    {get_msg_code(msg)} (remote inventory). ", end="")
    if payload_len == 0:
        print("Poll request.")
    elif payload_len >= 2:
        flags = msg['payload'][0]
        data = msg['payload'][1:]
        print(f"Flags: binary={1 if flags & 0x2 else 0}, dump={1 if flags & 0x1 else 0}. ", end="")
        print(f"Data: {data}.")


def process_cfg_rst(msg):
    assert msg['class'] == b'\x06' and msg['id'] == b'\x04', "Unexpected call."
    payload_len = len(msg['payload'])
    assert payload_len == 4, "Unexpected payload length"

    print(f"    {get_msg_code(msg)} (reset receiver/ clear backup data structure command).")
    nav_bbr_mask = msg['payload'][0:2]
    nav_bbr_mask_special = ''
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
    baudrate_default = 115200
    parser = argparse.ArgumentParser(description='%(prog)s '
                                                 'Run simulated UBX GPX receiver.')

    parser.add_argument(dest='serial_port_name',
                        help='Serial port name')

    parser.add_argument('-b', '--baudrate',
                        type=int,
                        help=f'Serial baudrate (default: {baudrate_default})',
                        default=baudrate_default)

    args = parser.parse_args()

    ser = serial.Serial(args.serial_port_name, args.baudrate)
    print(f"Opened serial port '{ser.name}' with a baudrate of {ser.baudrate}.")
    # print(ser)
    use_mock = False
    # rx_mock_data = b"\xb5\x62\x06\x34\x00\x00\x3a\x40\xff\x1b\xad\x1d\xea\xc0\xff\xee\xb5"
    # for rx_byte in rx_mock_data:

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
            remaining_len = int.from_bytes(msg['len_raw'], 'little')
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
    print("Done.")


if __name__ == '__main__':
    run()
