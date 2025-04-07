import socket
import threading
import time
import struct
import random

class RTCPSender:

    # initialize the RTCPSender instance
    # remote_ip is the ip address of the host to send reports to
    # rtcp_port is the port number used along with ip address
    def __init__(self, remote_ip, rtcp_port):
        self.remote_ip = remote_ip
        self.rtcp_port = rtcp_port
        # create a UDP socket for sending RTCP packets
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # initialize packet statistics
        self.packet_count = 0
        self.octet_count = 0
        # boolean flag if the instance is active
        self.running = False
        # randomly generate an SSRC
        self.ssrc = random.randint(1000, 9999)

    # builds a sender report packet
    def build_sender_report(self):
        # initialize
        version = 2
        padding = 0
        rc = 0
        pt = 200  # RTCP SR
        length = 6  # 28 bytes / 4 - 1

        # generate proper 64-bit NTP timestamp split into 2 parts
        ntp_time = time.time()
        ntp_ts_high = int(ntp_time)              # seconds part
        ntp_ts_low = int((ntp_time % 1) * (2**32))  # fractional part

        # wrap RTP timestamp at 2^32
        rtp_ts = int(ntp_time * 8000) % (2**32)

        # create header for the packet
        header = struct.pack("!BBH", (version << 6) | (padding << 5) | rc, pt, length)

        # build the body of the packet
        body = struct.pack("!IIIIII",
            self.ssrc,
            ntp_ts_high,
            ntp_ts_low,
            rtp_ts,
            self.packet_count,
            self.octet_count
        )

        # return the packet
        return header + body

    # send the reports
    def send_reports(self):
        # set running flag to true
        self.running = True
        # while running flag, build the report and send it to the remote IP and RTCP port
        while self.running:
            report = self.build_sender_report()
            self.socket.sendto(report, (self.remote_ip, self.rtcp_port))
            print("[RTCP] Sent Sender Report.")
            time.sleep(5)  # every 5 seconds

    # the "main" function of the RTCPSender instance
    def start(self):
        # create and start a new thread to send reports
        thread = threading.Thread(target=self.send_reports)
        thread.start()

    # stops all operations
    def stop(self):
        self.running = False

    # updates the statistics
    def update_stats(self, packet_len):
        self.packet_count += 1
        self.octet_count += packet_len
