import socket
import threading
import time
import struct
import random

class RTCPSender:
    def __init__(self, remote_ip, rtcp_port):
        self.remote_ip = remote_ip
        self.rtcp_port = rtcp_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.packet_count = 0
        self.octet_count = 0
        self.running = False
        self.ssrc = random.randint(1000, 9999)

    def build_sender_report(self):
        version = 2
        padding = 0
        rc = 0
        pt = 200  # RTCP Sender Report
        length = 6  # 28 bytes / 4 - 1

        ntp_ts_high = int(time.time())
        ntp_ts_low = int((time.time() % 1) * (2**32))
        rtp_ts = int(time.time() * 8000)  # assuming 8kHz

        header = struct.pack("!BBH", (version << 6) | (padding << 5) | rc, pt, length)
        body = struct.pack("!I2I2I", self.ssrc, ntp_ts_high, ntp_ts_low, rtp_ts, self.packet_count, self.octet_count)
        return header + body

    def send_reports(self):
        self.running = True
        while self.running:
            report = self.build_sender_report()
            self.socket.sendto(report, (self.remote_ip, self.rtcp_port))
            print("[RTCP] Sent Sender Report.")
            time.sleep(5)  # every 5 seconds

    def start(self):
        thread = threading.Thread(target=self.send_reports)
        thread.start()

    def stop(self):
        self.running = False

    def update_stats(self, packet_len):
        self.packet_count += 1
        self.octet_count += packet_len
