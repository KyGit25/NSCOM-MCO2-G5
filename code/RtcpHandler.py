import socket
import threading
import time
import struct

class RtcpHandler:
    def __init__(self, ssrc, dest_ip, dest_port):
        self.ssrc = ssrc
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.running = False
        self.packet_count = 0
        self.rtcp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        self.running = True
        threading.Thread(target=self.send_reports).start()
        print(f"[RTCP] Sending RTCP reports to {self.dest_ip}:{self.dest_port}")

    def increment_packet_count(self):
        self.packet_count += 1

    def send_reports(self):
        while self.running:
            report = self.build_sender_report()
            self.rtcp_socket.sendto(report, (self.dest_ip, self.dest_port))
            print(f"[RTCP] Sent Sender Report | Packets: {self.packet_count}")
            time.sleep(5)  # send report every 5 seconds

    def build_sender_report(self):
        version = 2
        padding = 0
        rc = 0  # report count
        pt = 200  # sender report
        length = 6  # header + sender info
        ntp_sec = int(time.time())
        ntp_frac = 0
        rtp_ts = ntp_sec  # using same for simplicity

        header = (version << 30) | (padding << 29) | (rc << 24) | (pt << 16) | length
        packet = struct.pack("!I I I I I I", 
                             header, 
                             self.ssrc, 
                             ntp_sec, 
                             ntp_frac, 
                             rtp_ts, 
                             self.packet_count)
        return packet

    def stop(self):
        self.running = False
        self.rtcp_socket.close()
        print("[RTCP] Stopped sending reports.")
