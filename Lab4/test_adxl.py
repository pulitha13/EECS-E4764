# from machine import Pin, SPI
# import time

# def main():
#     spi = SPI(1, baudrate=1500000, polarity=1, phase=1)
#     cs = Pin(15, Pin.OUT)

#     SPI_READ = 1 << 7
#     SPI_WRITE = 0 << 7

#     SPI_SINGLE_BYTE = 0 << 6
#     SPI_MULTIPLE_BYTES = 1 << 6


#     registers= {
#         0x00: 0xE5,  # REG_DEVID
#         0x2C: 0x0A,  # REG_BW_RATE
#         0x2D: 0x08,  # REG_POWER_CTL
#         0x2E: 0x00,  # REG_INT_ENABLE
#         0x21: 0x00,  # REG_DUR
#         0x31: 0x00,  # REG_DATA_FORMAT
#         0x32: 0x00,  # REG_DATAX0
#         0x33: 0x00,  # REG_DATAX1
#         0x34: 0x00,  # REG_DATAY0
#         0x35: 0x00,  # REG_DATAY1
#         0x36: 0x00,  # REG_DATAZ0
#         0x37: 0x00,  # REG_DATAZ1
#         0x38: 0x00   # REG_FIFO_CTL   
#     }

#     read_buffer = bytearray(2)
#     print("starting to initialize registers")
#     for register, value in registers.items():
#         cs(0)
#         spi.write(bytes([register,value]))
#         time.sleep(0.1)
#         cs(1)
#         print(f'Initialized {hex(register)} with {hex(value)}')
#     print("Done initializing registers")

#     while True:
#         cs(0) # Select device
#         read_buffer = bytearray(6)
#         spi.write(bytearray([SPI_READ| SPI_MULTIPLE_BYTES | 0x32])) #SEND READ COMMAND
#         spi.readinto(read_buffer) # read into buffer
#         time.sleep(1)
#         cs(1) # Deselect device

#         print(f'Raw XYZ: {read_buffer}')  # Debug print
#         x = (read_buffer[1] << 8) | read_buffer[0] # Combine high and low bytes for X
#         y = (read_buffer[3] << 8) | read_buffer[2] # Combine high and low bytes for Y
#         z = (read_buffer[5] << 8) | read_buffer[4] # Combine high and low bytes for Z

#         # Convert to signed 16-bit integers (two's complement)
#         if x & (1 << 15):
#             x -= 1 << 16
#         if y & (1 << 15):
#             y -= 1 << 16
#         if z & (1 << 15):
#             z -= 1 << 16

#         print(f'X:{x},Y:{y},Z:{z}')


# if __name__ == '__main__':
#     main()





# # cmd_int = SPI_WRITE | SPI_SINGLE_BYTE | register
# # cmd_bytes = cmd_int.to_bytes(1, "big")
# # value_bytes = value.to_bytes(1, "big")
# # write_buffer = bytearray(cmd_bytes) + bytearray(value_bytes)
# # self.spi.write(write_buffer)
# # print(f"wrote to register { hex(register)}: {write_buffer.hex()}")
# # ID_REG = 0x00

# # cs.value(0)
# # spi.readinto(read_buffer, SPI_READ | SPI_SINGLE_BYTE | ID_REG)
# # cs.value(1)

# # print(read_buffer)