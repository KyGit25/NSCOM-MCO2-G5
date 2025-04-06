import socket
import threading

class SipClient:
    def __init__(self, local_ip, local_port, remote_ip, remote_port, media_port):
        self.local_ip = local_ip
        self.local_port = local_port
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.media_port = media_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((local_ip, local_port))
        self.call_active = False
        self.session_id = 123456  # Hardcoded or randomized

    def send_invite(self):
        sdp = (
            f"v=0\r\n"
            f"o=- 0 0 IN IP4 {self.local_ip}\r\n"
            f"s=Audio Session\r\n"
            f"c=IN IP4 {self.local_ip}\r\n"
            f"t=0 0\r\n"
            f"m=audio {self.media_port} RTP/AVP 0\r\n"
            f"a=rtpmap:0 PCMU/8000\r\n"
        )

        invite = (
            f"INVITE sip:user@{self.remote_ip} SIP/2.0\r\n"
            f"Via: SIP/2.0/UDP {self.local_ip}:{self.local_port}\r\n"
            f"From: <sip:caller@{self.local_ip}>;tag=1234\r\n"
            f"To: <sip:user@{self.remote_ip}>\r\n"
            f"Call-ID: {self.session_id}@{self.local_ip}\r\n"
            f"CSeq: 1 INVITE\r\n"
            f"Contact: <sip:caller@{self.local_ip}:{self.local_port}>\r\n"
            f"Content-Type: application/sdp\r\n"
            f"Content-Length: {len(sdp)}\r\n\r\n"
            f"{sdp}"
        )

        self.sock.sendto(invite.encode(), (self.remote_ip, self.remote_port))
        print("[SIP] INVITE sent")
        threading.Thread(target=self.listen_for_response, daemon=True).start()

    def listen_for_response(self):
        while not self.call_active:
            data, addr = self.sock.recvfrom(2048)
            msg = data.decode()
            if "200 OK" in msg:
                print("[SIP] 200 OK received")
                self.send_ack()
                self.call_active = True
            elif msg.startswith("SIP/2.0 4") or msg.startswith("SIP/2.0 5"):
                print("[SIP] Error response received:", msg)
                break

    def send_ack(self):
        ack = (
            f"ACK sip:user@{self.remote_ip} SIP/2.0\r\n"
            f"Via: SIP/2.0/UDP {self.local_ip}:{self.local_port}\r\n"
            f"From: <sip:caller@{self.local_ip}>;tag=1234\r\n"
            f"To: <sip:user@{self.remote_ip}>\r\n"
            f"Call-ID: {self.session_id}@{self.local_ip}\r\n"
            f"CSeq: 1 ACK\r\n"
            f"Content-Length: 0\r\n\r\n"
        )
        self.sock.sendto(ack.encode(), (self.remote_ip, self.remote_port))
        print("[SIP] ACK sent")

    def send_bye(self):
        bye = (
            f"BYE sip:user@{self.remote_ip} SIP/2.0\r\n"
            f"Via: SIP/2.0/UDP {self.local_ip}:{self.local_port}\r\n"
            f"From: <sip:caller@{self.local_ip}>;tag=1234\r\n"
            f"To: <sip:user@{self.remote_ip}>\r\n"
            f"Call-ID: {self.session_id}@{self.local_ip}\r\n"
            f"CSeq: 2 BYE\r\n"
            f"Content-Length: 0\r\n\r\n"
        )
        self.sock.sendto(bye.encode(), (self.remote_ip, self.remote_port))
        print("[SIP] BYE sent")
