import socket
import threading
import pyaudio
from RTPPacket import RTPPacket

class AudioReceiver:
    def __init__(self, local_ip, local_port):
        self.local_ip = local_ip
        self.local_port = local_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.local_ip, self.local_port))
        
        # PyAudio parameters: assuming 8-bit mono PCM at 8000Hz for PCMU
        self.pyaudio_instance = pyaudio.PyAudio()
        self.stream = self.pyaudio_instance.open(
            format=pyaudio.paInt8, 
            channels=1, 
            rate=8000, 
            output=True,
            frames_per_buffer=160
        )
        self.running = True

    def start_receiving(self):
        threading.Thread(target=self._receive_loop, daemon=True).start()
        print(f"[AUDIO RECEIVER] Listening on {self.local_ip}:{self.local_port}...")

    def _receive_loop(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                packet = RTPPacket.decode(data)
                # Play the audio payload from the RTP packet
                self.stream.write(packet.payload)
            except Exception as e:
                print(f"[AUDIO RECEIVER] Error: {e}")

    def close(self):
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio_instance.terminate()
        self.sock.close()
        print("[AUDIO RECEIVER] Audio receiver closed")
