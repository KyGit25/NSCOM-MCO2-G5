import socket
import time
from RtpPacket import RtpPacket

class RtpSender:
    def __init__(self, audio_file, destination_ip, destination_port, ssrc=12345):
        self.audio_file = audio_file
        self.dest_ip = destination_ip
        self.dest_port = destination_port
        self.ssrc = ssrc
        self.seq_num = 0
        self.rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = False

    def start_stream(self):
        """Start reading audio and sending RTP packets."""
        try:
            with open(self.audio_file, 'rb') as f:
                self.running = True
                while self.running:
                    frame = f.read(160)  # ~20ms for G.711 @ 8000 Hz
                    if not frame:
                        print("[RTP] End of audio file.")
                        break

                    self.send_rtp_packet(frame)
                    self.seq_num += 1
                    time.sleep(0.02)  # Simulate 20ms audio frame timing
        except FileNotFoundError:
            print("[RTP] Audio file not found.")

    def stop_stream(self):
        self.running = False

    def send_rtp_packet(self, payload):
        """Build and send RTP packet."""
        packet = RtpPacket()
        packet.encode(
            version=2,
            padding=0,
            extension=0,
            cc=0,
            seqnum=self.seq_num,
            marker=0,
            pt=0,  # PT=0 is G.711 PCMU
            ssrc=self.ssrc,
            payload=payload
        )
        self.rtp_socket.sendto(packet.getPacket(), (self.dest_ip, self.dest_port))
        print(f"[RTP] Sent packet #{self.seq_num}")
