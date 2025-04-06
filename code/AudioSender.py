import socket
import wave
import time
from RtpPacket import RtpPacket
import threading
import struct

class AudioSender:
    def __init__(self, audio_file, dest_ip, dest_port, rtcp_port=None):
        self.audio_file = audio_file
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.rtcp_port = rtcp_port
        self.rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sequence_number = 0
        self.ssrc = 12345
        self.running = False
        self.timestamp = 0
        self.rtcp_thread = None

    def start_stream(self):
        wf = wave.open(self.audio_file, 'rb')
        frame_rate = wf.getframerate()
        frame_size = 160  # 20ms worth of 8kHz PCM = 160 bytes

        print("[RTP] Starting audio stream...")

        self.running = True
        if self.rtcp_port:
            self.rtcp_thread = threading.Thread(target=self.send_rtcp_reports)
            self.rtcp_thread.start()

        while self.running:
            data = wf.readframes(frame_size)
            if not data:
                break

            rtp_packet = RtpPacket()
            rtp_packet.encode(
                version=2,
                padding=0,
                extension=0,
                cc=0,
                seqnum=self.sequence_number,
                marker=0,
                pt=0,  # Payload type 0 = PCM µ-law
                ssrc=self.ssrc,
                payload=data
            )

            packet = rtp_packet.getPacket()
            self.rtp_socket.sendto(packet, (self.dest_ip, self.dest_port))
            print(f"[RTP] Sent packet Seq={self.sequence_number}")

            self.sequence_number += 1
            self.timestamp += int((frame_size / wf.getsampwidth()) * (8000 / frame_size))

            time.sleep(0.02)  # 20ms per frame = 50 fps

        wf.close()
        self.rtp_socket.close()
        self.running = False
        print("[RTP] Audio stream ended.")

    def stop_stream(self):
        self.running = False

    def send_rtcp_reports(self):
        rtcp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while self.running:
            time.sleep(5)
            packet_count = self.sequence_number
            report = self.build_rtcp_report(packet_count)
            rtcp_socket.sendto(report, (self.dest_ip, self.rtcp_port))
            print("[RTCP] Sender report sent")

    def build_rtcp_report(self, packet_count):
        # Very simplified RTCP Sender Report (not fully RFC-compliant)
        header = struct.pack('!BBH', 0x80, 200, 6)  # SR, length=6
        ssrc = struct.pack('!I', self.ssrc)
        ntp = struct.pack('!II', 0, int(time.time()))  # Fake NTP timestamp
        rtp_ts = struct.pack('!I', self.timestamp)
        count = struct.pack('!I', packet_count)
        octets = struct.pack('!I', packet_count * 160)  # fake: 160 bytes per packet
        return header + ssrc + ntp + rtp_ts + count + octets
