import socket
import struct
import threading
import time

class RTCPHandler:
    def __init__(self, local_ip, local_port, dest_ip, dest_port, ssrc):
        self.local_ip = local_ip
        self.local_port = local_port
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.ssrc = ssrc
        self.packet_count = 0
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.local_ip, self.local_port))
    
    def start_sending_reports(self, interval=5):
        threading.Thread(target=self._send_reports, args=(interval,), daemon=True).start()

    def _send_reports(self, interval):
        while self.running:
            report = self._build_sender_report()
            self.sock.sendto(report, (self.dest_ip, self.dest_port))
            print("[RTCP] Sender Report sent")
            time.sleep(interval)

    def _build_sender_report(self):
        # Very simplified RTCP Sender Report (SR) format
        version = 2
        padding = 0
        report_count = 0  # No report blocks
        packet_type = 200  # SR
        length = 6  # In 32-bit words - 1 (6 means 28 bytes total)

        header = (version << 30) | (padding << 29) | (report_count << 24) | (packet_type << 16) | length
        header_bytes = struct.pack("!I", header)

        ntp_sec = int(time.time())
        ntp_frac = int((time.time() % 1) * (2**32))
        rtp_timestamp = int(time.time() * 1000)
        sender_packet_count = self.packet_count
        sender_octet_count = self.packet_count * 160  # assuming 160 bytes per frame

        body = struct.pack("!IIIIII",
            self.ssrc,
            ntp_sec,
            ntp_frac,
            rtp_timestamp,
            sender_packet_count,
            sender_octet_count
        )
        return header_bytes + body

    def increment_packet_count(self):
        self.packet_count += 1

    def stop(self):
        self.running = False
        self.sock.close()
        print("[RTCP] RTCP handler stopped")
