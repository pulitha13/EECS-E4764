import pn532_core as core

class PN532(core.PN532_Core):

	def __init__(self, spi, cs_pin, irq=None, reset=None, debug=False):
		"""Create an instance of the PN532 class using SPI"""
		super().__init__(spi=spi, cs_pin=cs_pin, irq=irq, reset=reset, debug=debug)
		self.debug = debug

	def mifare_classic_multi_write_block(self, uid, start_block, data):
		"""Writes to as many successive blocks as necessary until either
		device is out of memory or the MAX_WRITE_AMT has been hit
		"""
		block_offset = 0
		for data_idx in range(0, len(data), 16):
			
			data_chunk = data[data_idx:data_idx + 16]

			# Null terminate the end
			while (len(data_chunk) < 16):
				data_chunk.append(0x00)

			# Dont write to the security blocks
			if ((start_block + block_offset)%4 == 3):
				block_offset = block_offset + 1

			block = start_block + block_offset
			
			if (self.debug):
				print(f"Authenticating block {block}")
			if(not self.mifare_classic_authenticate_block(uid=uid, block_number=block)):
				raise RuntimeError(f'Could not authenticate block {block}')

			if (self.debug):
				print(f"Writing to the {block}th block = {data_chunk}")
			if(not self.mifare_classic_write_block(block, data_chunk)):
				raise RuntimeError(f'Could not successfully write {data_chunk} to block {block}')

			block_offset = block_offset + 1

	def mifare_classic_multi_read_block(self, uid, start_block, size):
		"""Reads to as many successive blocks as necessary until either
		size bytes (aligned to 16 bytes) have been read
		"""
		block_offset = 0
		read_data = bytearray(b'')

		while (len(read_data) < size):

			# Dont read the security blocks
			if ((start_block + block_offset)%4 == 3):
				block_offset = block_offset + 1

			block = start_block + block_offset
			if(self.debug):
				print(f"Authenticating block {block}")
			if(not self.mifare_classic_authenticate_block(uid=uid, block_number=block)):
				raise RuntimeError(f'Could not authenticate block {block}')

			if(self.debug):
				print(f"Reading the {block}th block")
			read_chunk = self.mifare_classic_read_block(block_number=block)
			if(read_chunk == None):
				raise RuntimeError(f'Read nothing')

			read_data.extend(read_chunk)
			block_offset = block_offset + 1

		return read_data

	def read_nfc(self, tmot):
		"""Accepts a device and a timeout in millisecs """
		uid = self.read_passive_target(timeout=tmot)
		if uid is None:
			print('CARD NOT FOUND')
		else:
			numbers = [i for i in uid]
			string_ID = '{}-{}-{}-{}'.format(*numbers)
			if(self.debug):
				print('Found card with UID:', [hex(i) for i in uid])
				print('Number_id: {}'.format(string_ID))
		return uid