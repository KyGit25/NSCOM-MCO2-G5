import socket
import time
import pyaudio
import random
from RTPPacket import RTPPacket

class MicStreamer:
    def __init__(self, dest_ip, dest_port):
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.ssrc = random.randint(1000, 9999)
        self.sequence_number = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt8,
            channels=1,
            rate=8000,
            input=True,
            frames_per_buffer=160
        )

    def stream_microphone(self):
        print(f"[MIC STREAMER] Sending microphone audio to {self.dest_ip}:{self.dest_port}")
        try:
            while True:
                data = self.stream.read(160, exception_on_overflow=False)
                packet = RTPPacket.create_packet(
                    sequence_number=self.sequence_number,
                    ssrc=self.ssrc,
                    payload=data
                )
                self.sock.sendto(packet.encode(), (self.dest_ip, self.dest_port))
                self.sequence_number += 1
                time.sleep(0.02)
        except KeyboardInterrupt:
            print("[MIC STREAMER] Interrupted by user")
        finally:
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            self.sock.close()
            print("[MIC STREAMER] Microphone stream stopped")

    def get_ssrc(self):
        return self.ssrc
