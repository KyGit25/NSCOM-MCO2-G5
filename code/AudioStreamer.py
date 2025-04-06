import wave
import socket
import time
from RTPPacket import RTPPacket
import random

class AudioStreamer:
    def __init__(self, file_path, dest_ip, dest_port):
        self.file_path = file_path
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.ssrc = random.randint(1000, 9999)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sequence_number = 0

    def stream(self):
        try:
            wf = wave.open(self.file_path, 'rb')
            frame_size = 160  # For PCMU @8000Hz: 160 bytes = 20ms
            print(f"[AUDIO] Streaming {self.file_path} to {self.dest_ip}:{self.dest_port}...")

            while True:
                data = wf.readframes(frame_size)
                if not data:
                    break

                packet = RTPPacket.create_packet(
                    sequence_number=self.sequence_number,
                    ssrc=self.ssrc,
                    payload=data
                )
                self.sock.sendto(packet.encode(), (self.dest_ip, self.dest_port))
                self.sequence_number += 1
                time.sleep(0.02)  # 20 ms for 8000Hz audio
        except Exception as e:
            print(f"[AUDIO] Error: {e}")
        finally:
            self.sock.close()
            wf.close()
            print("[AUDIO] Streaming finished")

    def get_ssrc(self):
        return self.ssrc
