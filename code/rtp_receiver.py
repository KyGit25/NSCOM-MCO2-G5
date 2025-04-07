import socket
import threading
import struct
import pyaudio

class RTPReceiver:
    def __init__(self, local_ip, rtp_port):
        self.local_ip = local_ip
        self.rtp_port = rtp_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((local_ip, rtp_port))
        self.running = False

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,  # PCM 16-bit, adjust for G.711 if needed
            channels=1,
            rate=8000,
            output=True
        )

    def parse_rtp_packet(self, data):
        header = data[:12]
        payload = data[12:]
        version, payload_type = struct.unpack('!BB', header[:2])
        sequence_number, timestamp, ssrc = struct.unpack('!HII', header[2:])
        return payload

    def receive_audio(self):
        print("[RTP] Listening for incoming RTP packets...")
        self.running = True

        while self.running:
            try:
                data, _ = self.socket.recvfrom(2048)
                audio = self.parse_rtp_packet(data)
                self.stream.write(audio)
            except Exception as e:
                print("[RTP] Error:", e)

        print("[RTP] Stopped receiving.")

    def start(self):
        thread = threading.Thread(target=self.receive_audio)
        thread.start()

    def stop(self):
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.socket.close()
