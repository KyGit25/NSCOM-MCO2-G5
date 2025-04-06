import pyaudio
import socket
import time
import threading
from RtpPacket import RtpPacket

class MicStreamer:
    def __init__(self, dest_ip, dest_port, rtcp_port=None):
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.rtcp_port = rtcp_port
        self.ssrc = 33333
        self.seqnum = 0
        self.timestamp = 0
        self.running = False

        self.rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=8000,
            input=True,
            frames_per_buffer=160
        )

    def start(self):
        self.running = True
        threading.Thread(target=self.stream_audio, daemon=True).start()
        print("[MIC] Microphone streaming started.")

    def stop(self):
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        self.rtp_socket.close()
        print("[MIC] Microphone streaming stopped.")

    def stream_audio(self):
        while self.running:
            audio_data = self.stream.read(160, exception_on_overflow=False)

            rtp_packet = RtpPacket()
            rtp_packet.encode(
                version=2,
                padding=0,
                extension=0,
                cc=0,
                seqnum=self.seqnum,
                marker=0,
                pt=0,
                ssrc=self.ssrc,
                payload=audio_data
            )
            packet = rtp_packet.getPacket()
            self.rtp_socket.sendto(packet, (self.dest_ip, self.dest_port))
            self.seqnum += 1
            time.sleep(0.02)  # 20ms
