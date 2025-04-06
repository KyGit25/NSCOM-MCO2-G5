import struct
import time
import random

class RTPPacket:
    def __init__(self, payload_type=0, sequence_number=0, timestamp=0, ssrc=0, payload=b""):
        self.version = 2
        self.padding = 0
        self.extension = 0
        self.csrc_count = 0
        self.marker = 0
        self.payload_type = payload_type  # 0 = PCMU
        self.sequence_number = sequence_number
        self.timestamp = timestamp
        self.ssrc = ssrc
        self.payload = payload

    def encode(self):
        header = 0
        header |= (self.version & 0x03) << 14
        header |= (self.padding & 0x01) << 13
        header |= (self.extension & 0x01) << 12
        header |= (self.csrc_count & 0x0F) << 8
        header |= (self.marker & 0x01) << 7
        header |= (self.payload_type & 0x7F)

        # First two bytes: version, padding, extension, csrc, marker, payload type
        first_part = struct.pack("!H", header)
        # Sequence number, timestamp, SSRC
        second_part = struct.pack("!HII", self.sequence_number, self.timestamp, self.ssrc)
        return first_part + second_part + self.payload

    @staticmethod
    def decode(packet_bytes):
        header = struct.unpack("!H", packet_bytes[0:2])[0]
        version = (header >> 14) & 0x03
        payload_type = header & 0x7F
        sequence_number, timestamp, ssrc = struct.unpack("!HII", packet_bytes[2:12])
        payload = packet_bytes[12:]
        return RTPPacket(payload_type, sequence_number, timestamp, ssrc, payload)

    @staticmethod
    def create_packet(sequence_number, ssrc, payload):
        timestamp = int(time.time() * 1000)
        return RTPPacket(payload_type=0, sequence_number=sequence_number, timestamp=timestamp, ssrc=ssrc, payload=payload)
