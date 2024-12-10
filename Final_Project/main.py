from machine import Pin, SPI
import NFC_PN532 as nfc
import network
import time
import ujson
import errno
import socket

# Wifi credentials
# SSID = "Columbia University"
# Password = ""

SSID = "SpectrumSetup-57F5"
Password = "silvertune468"

# Socket
CMD_PORT = 7000

CARD_DET_TIMEOUT = 5000

station = network.WLAN(network.STA_IF)

def read_nfc(dev, tmot):
    """Accepts a device and a timeout in millisecs """
    print('Reading...')
    uid = dev.read_passive_target(timeout=tmot)
    if uid is None:
        print('CARD NOT FOUND')
    else:
        numbers = [i for i in uid]
        string_ID = '{}-{}-{}-{}'.format(*numbers)
        print('Found card with UID:', [hex(i) for i in uid])
        print('Number_id: {}'.format(string_ID))

    return uid

def connect_to_wifi(ssid, password):
    station.active(True)
    print('Connecting to Wi-Fi...')
    station.connect(ssid, password)

    attempts = 0
    while not station.isconnected() and attempts < 20:  # 20 attempts
        attempts += 1
        print(f'Attempt {attempts}...')
        time.sleep(1)

    if station.isconnected():
        print('Connected to Wi-Fi!')
        print('Network config:', station.ifconfig())
    else:
        # print('Failed to connect to Wi-Fi')
        raise Exception('Failed to connect to Wi-Fi.')  # Generic exception
    
    return station.ifconfig()[0]


def check_for_commands(s):
    try:
        client_sock, client_addr = s.accept()
        print(f"Connected to client socket: {client_addr}")

        data = client_sock.recv(1024).decode('utf-8')
        data = ujson.loads(data)
        print(f"Recieved command: {data['cmd']}")
        print(f"Recieved args: {data['args']}")
        return data

    except Exception as e:
        if isinstance(e, OSError) and (e.errno == errno.EAGAIN or e.errno == errno.ETIMEDOUT):
            pass 
        else:
            print(f"An error occurred: {e}")
    
    return None

def open_command_socket(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, port))
    s.listen(1)
    s.setblocking(False)
    return s

def main():

    ip = connect_to_wifi(SSID, Password)
    s = open_command_socket(ip, CMD_PORT)

    spi_dev = SPI(1, baudrate=1000000)
    cs = Pin(5, Pin.OUT)
    cs.on()

    # SENSOR INIT
    pn532 = nfc.PN532(spi_dev,cs, debug=True)
    ic, ver, rev, support = pn532.get_firmware_version()
    print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))



    # Configure PN532 to communicate with MiFare cards
    pn532.SAM_configuration()

    print(f"Waiting {CARD_DET_TIMEOUT/1000}s for a card to appear...")
    uid = read_nfc(pn532, CARD_DET_TIMEOUT)
    print(f"Found card with UID={uid}")

    # Authenticate using the UID, and once authenticated do things
    # if(pn532.mifare_classic_authenticate_block(uid=uid, block_number=2)):
    #     print("Successfully authenticated block 2")
        
    #     print("Attempting a read on block 2")
    #     read_data = pn532.mifare_classic_read_block(block_number=2)    
    #     print("Result: ", read_data)

    #     write_data = bytearray(16)
    #     write_data[:len(b"hello world")] = b"hello world"
        
    #     print("Attempting a write on block 2")
    #     res = pn532.mifare_classic_write_block(block_number=2, data=write_data)
    #     print ("Result: ", res)

    #     print("Attempting a read on block 2")
    #     read_data = pn532.mifare_classic_read_block(block_number=2)
    #     print("Result: ", read_data.split(b'\x00', 1)[0].decode('utf-8'))


    # Try writing a big boi string
    print(f"Waiting {CARD_DET_TIMEOUT/1000.0}s for a card to appear...")
    uid = read_nfc(pn532, CARD_DET_TIMEOUT)
    print(f"Found card with UID={uid}")
    print("Trying to write a long string")
    pn532.mifare_classic_multi_write_block(uid, 2, bytearray(b"The quick brown fox jumps over the lazy dog"))

    while True:

        json_cmd = check_for_commands(s)
        if (json_cmd):
            print("Received packet: ", json_cmd)


if __name__ == '__main__':
    main()