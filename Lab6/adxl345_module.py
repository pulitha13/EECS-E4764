from machine import SPI, Pin
import time
import utime

#ADXL345 SPI protocol
#SPI Read/Write bit
SPI_READ = 1 << 7
SPI_WRITE = 0 << 6
##Choosing to read 1 or multiple bytes
SPI_SINGLE_BYTE = 0 << 6
SPI_MULTIPLE_BYTES = 1 << 6
#Read ID register
read_buffer = bytearray(2)

class ADXL345:
    def __init__(self, spi_bus, cs_pin):
        self.spi = SPI(spi_bus, baudrate=1500000, polarity=1, phase=1)
        self.cs = Pin(cs_pin, mode=Pin.OUT)
        self.registers= {
            0x00: 0xE5,  # REG_DEVID
            0x2C: 0x0A,  # REG_BW_RATE
            0x2D: 0x08,  # REG_POWER_CTL
            0x2E: 0x00,  # REG_INT_ENABLE
            0x21: 0x00,  # REG_DUR
            0x31: 0x00,  # REG_DATA_FORMAT
            0x32: 0x00,  # REG_DATAX0
            0x33: 0x00,  # REG_DATAX1
            0x34: 0x00,  # REG_DATAY0
            0x35: 0x00,  # REG_DATAY1
            0x36: 0x00,  # REG_DATAZ0
            0x37: 0x00,  # REG_DATAZ1
            0x38: 0x00   # REG_FIFO_CTL
        }
    
    def initialize_device(self):
        print("starting to initialize registers")
        for register, value in self.registers.items():
            self.cs(0)
            self.spi.write(bytes([register, value]))
            time.sleep(0.1)
            self.cs(1)
            print(f"wrote to register { hex(register)}: {hex(value)}")
        print("Done initializing registers")

    def read_device_id(self):
        ID_REG = 0x00
        read_buffer = bytearray(2)
        self.cs.value(0)
        self.spi.readinto(read_buffer, SPI_READ | SPI_SINGLE_BYTE | ID_REG)
        self.cs.value(1)
        read_buffer_hex = read_buffer.hex()
        print("This is DEVID: ",read_buffer_hex)
        # print(type(read_buffer_hex))
        return read_buffer.hex()

    def adxl345_read_xyz(self):
        self.cs(0) # Select device
        read_buffer = bytearray(6)
        # print(f"Writing {bytearray([SPI_READ| SPI_MULTIPLE_BYTES | 0x32])} to accel")
        self.spi.write(bytearray([SPI_READ| SPI_MULTIPLE_BYTES | 0x32])) #SEND READ COMMAND
        self.spi.readinto(read_buffer) # read into buffer
        self.cs(1) # Deselect device

        # print(f'Raw XYZ: {read_buffer}')  # Debug print
        x = (read_buffer[1] << 8) | read_buffer[0] # Combine high and low bytes for X
        y = (read_buffer[3] << 8) | read_buffer[2] # Combine high and low bytes for Y
        z = (read_buffer[5] << 8) | read_buffer[4] # Combine high and low bytes for Z

        # Convert to signed 16-bit integers (two's complement)
        if x & (1 << 15):
            x -= 1 << 16
        if y & (1 << 15):
            y -= 1 << 16
        if z & (1 << 15):
            z -= 1 << 16
        # print(f'X:{x},Y:{y},Z:{z}')
        # time.sleep(1)

        return x, y, z #returned combined values