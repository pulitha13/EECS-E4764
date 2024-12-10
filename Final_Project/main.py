from machine import Pin, SPI
import network
import time
import ujson
import errno
import socket
import gc
import pn532 as nfc

# Check free memory
print("Free memory:", gc.mem_free())

# Wifi credentials
SSID = "Columbia University"
Password = ""

# SSID = "SpectrumSetup-57F5"
# Password = "silvertune468"

# Socket
CMD_PORT = 7000
RESP_PORT = 7001

CARD_DET_TIMEOUT = 5000

def connect_to_wifi(station, ssid, password):
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

def send_response():
    

def open_command_socket(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, port))
    s.listen(1)
    s.setblocking(False)
    return s

def main():

    print("Free memory:", gc.mem_free())
    
    station = network.WLAN(network.STA_IF)
    ip = connect_to_wifi(station, SSID, Password)
    s = open_command_socket(ip, CMD_PORT)

    spi_dev = SPI(1, baudrate=1000000)
    cs = Pin(5, Pin.OUT)
    cs.on()

    # SENSOR INIT
    pn532 = nfc.PN532(spi_dev,cs, debug=False)
    # ic, ver, rev, support = pn532.get_firmware_version()
    # print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

    # Configure PN532 to communicate with MiFare cards
    pn532.SAM_configuration()

    print("Free memory (after init):", gc.mem_free())

    print(f"Waiting {CARD_DET_TIMEOUT/1000}s for a card to appear...")
    uid = pn532.read_nfc(CARD_DET_TIMEOUT)

    # Write to one block...
    if(pn532.mifare_classic_authenticate_block(uid=uid, block_number=2)):
        print("Successfully authenticated block 2")
        
        print("Reading block 2...")
        read_data = pn532.mifare_classic_read_block(block_number=2)    
        print("Result: ", read_data)

        write_data = bytearray(16)
        write_data[:len(b"hello world")] = b"hello world"
        
        print("Writing \"hello world\" to block 2...")
        res = pn532.mifare_classic_write_block(block_number=2, data=write_data)
        print ("Result: ", res)

        print("Reading block 2...")
        read_data = pn532.mifare_classic_read_block(block_number=2)
        print("Result: ", read_data.split(b'\x00', 1)[0].decode('utf-8'))

    print("Sleeping for 5s")
    time.sleep(5)

    # Try writing a big boi string
    print(f"Waiting {CARD_DET_TIMEOUT/1000.0}s for a card to appear...")
    uid = pn532.read_nfc(CARD_DET_TIMEOUT)
    print("Trying to write a long string")
    pn532.mifare_classic_multi_write_block(uid, 2, bytearray(b"The quick brown fox jumps over the lazy dog"))

    print("Sleeping for 5s")
    time.sleep(5)

    # Try reading it back a big boi string
    print(f"Waiting {CARD_DET_TIMEOUT/1000.0}s for a card to appear...")
    uid = pn532.read_nfc(CARD_DET_TIMEOUT)
    print("Trying to read a long string")
    read_data = pn532.mifare_classic_multi_read_block(uid, 2, 1+len("The quick brown fox jumps over the lazy dog"))
    print("Result: ", read_data.split(b'\x00', 1)[0].decode('utf-8'))

    while True:
        json_cmd = check_for_commands(s)
        
        if (json_cmd):
            print("Received packet: ", json_cmd)

            send_response()


if __name__ == '__main__':
    main()