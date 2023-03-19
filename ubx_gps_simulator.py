import argparse
import serial
from enum import Enum


class RxState(Enum):
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
    # print(f"  Checking message {msg} for valid checksum")
    calculated_checksum = calc_checksum(msg['class']+msg['id']+msg['len_raw']+msg['payload'])
    if calculated_checksum != msg['checksum']:
        # print("  Checksum mismatch!")
        # print(f"  Calculated checksum: {calculated_checksum}")
        # print(f"  Received checksum: {msg['checksum']}")
        return False
    else:
        return True


def send_ack_ack(ser, cls_id, msg_id):
    sync = b'\xb5\x62'
    body = b'\x05\x01\x02\x00' + cls_id + msg_id
    cs = calc_checksum(body)
    msg = sync + body + cs
    print(f"<<< Sending ACK-ACK response: {msg}")
    ser.write(msg)


def process_message(ser, msg):
    # print(f"Processing message {msg}")
    if msg['class'] == b'\x06':
        # "Configuration Input Messages: Set Dynamic Model, Set DOP Mask,
        # Set Baud Rate, etc."
        # "The CFG Class can be used to configure the receiver and read out
        # current configuration values. Any messages in Class CFG sent to the
        # receiver are acknowledged (with Message ACK-ACK) if processed
        # successfully, and rejected (with Message ACK-NAK) if processing the
        # message failed."
        if msg['id'] == b'\x00':
            print("    CFG-PRT")
        elif msg['id'] == b'\x01':
            print("    CFG-MSG")
        elif msg['id'] == b'\x02':
            print("    CFG-INF")
        elif msg['id'] == b'\x04':
            print("    CFG-RST")
        elif msg['id'] == b'\x06':
            print("    CFG-DAT")
        elif msg['id'] == b'\x07':
            print("    CFG-TP")
        elif msg['id'] == b'\x08':
            print("    CFG-RATE")
        elif msg['id'] == b'\x09':
            print("    CFG-CFG")
        elif msg['id'] == b'\x11':
            print("    CFG-RXM")
        elif msg['id'] == b'\x16':
            print("    CFG-SBAS")
        elif msg['id'] == b'\x0E':
            print("    CFG-FXN")
        elif msg['id'] == b'\x12':
            print("    CFG-EKF")
        elif msg['id'] == b'\x13':
            print("    CFG-ANT")
        elif msg['id'] == b'\x17':
            print("    CFG-NMEA")
        elif msg['id'] == b'\x1B':
            print("    CFG-USB")
        elif msg['id'] == b'\x1D':
            print("    CFG-TMODE")
        elif msg['id'] == b'\x22':
            print("    CFG-NVS")
        elif msg['id'] == b'\x23':
            print("    CFG-NAVX5")
        elif msg['id'] == b'\x24':
            print("    CFG-NAV5")
        elif msg['id'] == b'\x29':
            print("    CFG-ESFGWT")
        elif msg['id'] == b'\x31':
            print("    CFG-TP5")
        elif msg['id'] == b'\x32':
            print("    CFG-PM")
        elif msg['id'] == b'\x34':
            print("    CFG-RINV")
        elif msg['id'] == b'\x3B':
            print("    CFG-PM2")
        elif msg['id'] == b'\x3D':
            print("    CFG-TMODE2")
        elif msg['id'] == b'\x39':
            print("    CFG-ITFM")
        else:
            print("    CFG-???")
        # always send ACK-ACK (for now)
        send_ack_ack(ser, msg['class'], msg['id'])


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
                print(f">>> Received VALID message class 0x{ord(msg['class']):02X}, "
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
