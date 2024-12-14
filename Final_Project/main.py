from machine import Pin, SPI, PWM
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


# Socket Info
CMD_PORT = 7000

SERVER_IP = "192.168.1.81"
RESP_PORT = 7001

CARD_DET_TIMEOUT = 10000

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
        print(f"Server at {client_addr} connected to this socket")
        data = client_sock.recv(1024).decode('utf-8')
        data = ujson.loads(data)
        print(f"Recieved data: {data}")
        print(f"Recieved payload: {data['payload']}")
        print(f"Recieved command: {data['command']}")
        return client_sock, data

    except Exception as e:
        if isinstance(e, OSError) and (e.errno == errno.EAGAIN or e.errno == errno.ETIMEDOUT):
            pass 
        else:
            print(f"An error occurred: {e}")
    
    return None, None

def send_response(s, response):

    try:

        ujson.loads(response)
        s.sendall(response.encode('utf-8'))
        print("Sent: ", response)

    except Exception as e:
        print(f"error: {e}")
    finally:
        # Close the client socket
        s.close()

def open_command_socket(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, port))
    s.listen(1)
    s.settimeout(1)
    return s

def user_attempt_write(pn532, data):

    try:
        print(f"Waiting {CARD_DET_TIMEOUT/1000.0}s for a card to appear...")
        uid = pn532.read_nfc(CARD_DET_TIMEOUT)
        
        s = ujson.dumps(data)
        print(f"Trying to write string of size {len(s)}")

        pn532.mifare_classic_multi_write_block(uid, 2, bytearray(s, "utf-8"))

    except Exception as e:
        print(f"user_attempt_write: error: {e}")
        return {"status": "fail", "message": "fail"}
    
    return {"status": "success", "message": "done"}

def user_attempt_read(pn532, data):

    try:
        print(f"Waiting {CARD_DET_TIMEOUT/1000.0}s for a card to appear...")
        uid = pn532.read_nfc(CARD_DET_TIMEOUT)
        
        print(f"Trying to read all data on card")

        b = pn532.mifare_classic_multi_read_block(uid, 2, 256)
        strings = [ba.decode("utf-8") for ba in b.split(b'\x00')]

    except Exception as e:
        print(f"user_attempt_write: error: {type(e)}, {e}")
        return {"status": "fail", "message": "fail"}
    
    if (len(strings) > 0):
        return {"status": "success", "message": ujson.loads(strings[0])}
    
    
    return {"status:": "fail", "message": "tag is empty"}        

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

    piezo_pwm = PWM(Pin(4), freq=500, duty=0)   # Piezo buzzer on pin 5

    while True:

        client_sock, json_cmd = check_for_commands(s)
        
        if (json_cmd == None):
            continue

        if (json_cmd['command'] == "read"):
            piezo_pwm.duty(512)
            ret = user_attempt_read(pn532=pn532, data=json_cmd['payload'])
            send_response(client_sock, ujson.dumps(ret))
            piezo_pwm.duty(0)

        elif (json_cmd['command'] == "write"):
            piezo_pwm.duty(512)
            ret = user_attempt_write(pn532=pn532, data=json_cmd['payload'])
            send_response(client_sock, ujson.dumps(ret))
            piezo_pwm.duty(0)
        
        else:
            print("Received packet: ", json_cmd)
            send_response(client_sock, ujson.dumps({'status' : 'fail', 'message': 'invalid command'}))


if __name__ == '__main__':
    main()