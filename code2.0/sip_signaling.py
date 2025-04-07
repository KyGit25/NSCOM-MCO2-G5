import socket
import threading

class SIPSignaling:
    def __init__(self, local_ip, local_port, remote_ip, remote_port, rtp_port):
        self.local_ip = local_ip
        self.local_port = local_port
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.rtp_port = rtp_port
        self.sip_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sip_socket.bind((local_ip, local_port))
        self.call_active = False

    def build_sdp(self):
        return (
            "v=0\r\n"
            f"o=- 0 0 IN IP4 {self.local_ip}\r\n"
            "s=VoIP Call\r\n"
            f"c=IN IP4 {self.local_ip}\r\n"
            "t=0 0\r\n"
            f"m=audio {self.rtp_port} RTP/AVP 0\r\n"
            "a=rtpmap:0 PCMU/8000\r\n"
        )

    def build_invite(self):
        sdp = self.build_sdp()
        return (
            f"INVITE sip:client@{self.remote_ip}:{self.remote_port} SIP/2.0\r\n"
            f"Via: SIP/2.0/UDP {self.local_ip}:{self.local_port}\r\n"
            f"From: <sip:client@{self.local_ip}>;tag=1234\r\n"
            f"To: <sip:client@{self.remote_ip}>\r\n"
            "Call-ID: 1001@localhost\r\n"
            "CSeq: 1 INVITE\r\n"
            "Content-Type: application/sdp\r\n"
            f"Content-Length: {len(sdp)}\r\n\r\n"
            f"{sdp}"
        )

    def build_ack(self):
        return (
            f"ACK sip:client@{self.remote_ip}:{self.remote_port} SIP/2.0\r\n"
            f"Via: SIP/2.0/UDP {self.local_ip}:{self.local_port}\r\n"
            f"From: <sip:client@{self.local_ip}>;tag=1234\r\n"
            f"To: <sip:client@{self.remote_ip}>\r\n"
            "Call-ID: 1001@localhost\r\n"
            "CSeq: 1 ACK\r\n\r\n"
        )

    def build_bye(self):
        return (
            f"BYE sip:client@{self.remote_ip}:{self.remote_port} SIP/2.0\r\n"
            f"Via: SIP/2.0/UDP {self.local_ip}:{self.local_port}\r\n"
            f"From: <sip:client@{self.local_ip}>;tag=1234\r\n"
            f"To: <sip:client@{self.remote_ip}>\r\n"
            "Call-ID: 1001@localhost\r\n"
            "CSeq: 2 BYE\r\n\r\n"
        )

    def send_invite(self):
        invite_msg = self.build_invite()
        self.sip_socket.sendto(invite_msg.encode(), (self.remote_ip, self.remote_port))

    def send_ack(self):
        ack_msg = self.build_ack()
        self.sip_socket.sendto(ack_msg.encode(), (self.remote_ip, self.remote_port))

    def send_bye(self):
        bye_msg = self.build_bye()
        self.sip_socket.sendto(bye_msg.encode(), (self.remote_ip, self.remote_port))
        self.call_active = False
        print("[SIP] Call ended.")

    def listen(self):
        def handle_messages():
            while True:
                data, addr = self.sip_socket.recvfrom(2048)
                message = data.decode()
                print("[SIP] Received:\n", message)

                if "200 OK" in message:
                    print("[SIP] 200 OK received. Sending ACK.")
                    self.send_ack()
                    self.call_active = True

                elif message.startswith("INVITE"):
                    print("[SIP] INVITE received. Sending 200 OK.")
                    sdp = self.build_sdp()
                    response = (
                        f"SIP/2.0 200 OK\r\n"
                        f"Via: SIP/2.0/UDP {self.remote_ip}:{self.remote_port}\r\n"
                        f"From: <sip:client@{self.remote_ip}>;tag=1234\r\n"
                        f"To: <sip:client@{self.local_ip}>\r\n"
                        "Call-ID: 1001@localhost\r\n"
                        "CSeq: 1 INVITE\r\n"
                        "Content-Type: application/sdp\r\n"
                        f"Content-Length: {len(sdp)}\r\n\r\n"
                        f"{sdp}"
                    )
                    self.sip_socket.sendto(response.encode(), addr)

                elif message.startswith("BYE"):
                    print("[SIP] BYE received. Call ending.")
                    self.call_active = False
                    break

        thread = threading.Thread(target=handle_messages, daemon=True)
        thread.start()
