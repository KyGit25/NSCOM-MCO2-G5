import socket
import wave
import time
import threading
import struct
import random

class RTPSender:
    def __init__(self, rtp_ip, rtp_port, audio_path):
        self.rtp_ip = rtp_ip
        self.rtp_port = rtp_port
        self.audio_path = audio_path
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sequence_number = 0
        self.timestamp = 0
        self.ssrc = random.randint(1000, 5000)
        self.running = False

    def build_rtp_packet(self, payload):
        version = 2
        padding = 0
        extension = 0
        cc = 0
        marker = 0
        payload_type = 0  # G.711 µ-law
        header = (
            (version << 6) | (padding << 5) | (extension << 4) | cc,
            (marker << 7) | payload_type,
            self.sequence_number,
            self.timestamp,
            self.ssrc
        )
        rtp_header = struct.pack('!BBHII', *header)
        return rtp_header + payload

    def send_audio(self):
        wf = wave.open(self.audio_path, 'rb')
        sample_rate = wf.getframerate()
        frame_size = 160  # 20ms for 8kHz audio (G.711)
        self.running = True

        while self.running:
            audio_data = wf.readframes(frame_size)
            if not audio_data:
                break

            rtp_packet = self.build_rtp_packet(audio_data)
            self.socket.sendto(rtp_packet, (self.rtp_ip, self.rtp_port))

            self.sequence_number = (self.sequence_number + 1) % 65536
            self.timestamp += frame_size
            time.sleep(0.02)  # 20ms per packet
        wf.close()
        self.running = False
        print("[RTP] Finished sending audio.")

        if self.rtcp_sender:
            self.rtcp_sender.stop()


    def start(self, rtcp_sender=None):
        self.rtcp_sender = rtcp_sender
        thread = threading.Thread(target=self.send_audio)
        thread.start()


    def stop(self):
        self.running = False
