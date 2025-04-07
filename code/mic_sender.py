import socket
import threading
import pyaudio
import struct
import random
import time

class MicSender:
    def __init__(self, remote_ip, remote_port):
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sequence_number = 0
        self.timestamp = 0
        self.ssrc = random.randint(1000, 9999)
        self.running = False

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=8000,
            input=True,
            frames_per_buffer=160
        )

    def build_rtp_packet(self, payload):
        header = struct.pack(
            "!BBHII",
            (2 << 6),         # version = 2
            0,                # payload type
            self.sequence_number,
            self.timestamp,
            self.ssrc
        )
        return header + payload

    def send_mic_audio(self):
        self.running = True
        while self.running:
            data = self.stream.read(160, exception_on_overflow=False)
            rtp_packet = self.build_rtp_packet(data)
            self.socket.sendto(rtp_packet, (self.remote_ip, self.remote_port))
            self.sequence_number = (self.sequence_number + 1) % 65536
            self.timestamp += 160
            time.sleep(0.02)

    def start(self):
        self.thread = threading.Thread(target=self.send_mic_audio)
        self.thread.start()

    def stop(self):
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
