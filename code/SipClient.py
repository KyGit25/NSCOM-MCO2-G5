# SipClient.py
import socket

class SipClient:
    def __init__(self, local_ip, local_port, peer_ip, peer_port, media_port, codec="G711"):
        self.local_ip = local_ip
        self.local_port = local_port
        self.peer_ip = peer_ip
        self.peer_port = peer_port
        self.media_port = media_port
        self.codec = codec
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.local_ip, self.local_port))
        self.session_id = "123456"
        self.call_active = False

    def build_sdp(self):
        return f"v=0\n" \
               f"o=- 0 0 IN IP4 {self.local_ip}\n" \
               f"s=VoIP Call\n" \
               f"c=IN IP4 {self.local_ip}\n" \
               f"t=0 0\n" \
               f"m=audio {self.media_port} RTP/AVP 0\n" \
               f"a=rtpmap:0 {self.codec}/8000"

    def send_invite(self):
        sdp = self.build_sdp()
        invite = f"INVITE sip:user@{self.peer_ip} SIP/2.0\n" \
                 f"Via: SIP/2.0/UDP {self.local_ip}:{self.local_port}\n" \
                 f"From: <sip:client@{self.local_ip}>;tag=1234\n" \
                 f"To: <sip:user@{self.peer_ip}>\n" \
                 f"Call-ID: {self.session_id}\n" \
                 f"CSeq: 1 INVITE\n" \
                 f"Contact: <sip:client@{self.local_ip}:{self.local_port}>\n" \
                 f"Content-Type: application/sdp\n" \
                 f"Content-Length: {len(sdp)}\n\n" \
                 f"{sdp}"
        self.sock.sendto(invite.encode(), (self.peer_ip, self.peer_port))
        print("[SIP] INVITE sent.")

    def send_ack(self):
        ack = f"ACK sip:user@{self.peer_ip} SIP/2.0\n" \
              f"Via: SIP/2.0/UDP {self.local_ip}:{self.local_port}\n" \
              f"From: <sip:client@{self.local_ip}>;tag=1234\n" \
              f"To: <sip:user@{self.peer_ip}>\n" \
              f"Call-ID: {self.session_id}\n" \
              f"CSeq: 1 ACK\n\n"
        self.sock.sendto(ack.encode(), (self.peer_ip, self.peer_port))
        print("[SIP] ACK sent.")

    def send_bye(self):
        bye = f"BYE sip:user@{self.peer_ip} SIP/2.0\n" \
              f"Via: SIP/2.0/UDP {self.local_ip}:{self.local_port}\n" \
              f"From: <sip:client@{self.local_ip}>;tag=1234\n" \
              f"To: <sip:user@{self.peer_ip}>\n" \
              f"Call-ID: {self.session_id}\n" \
              f"CSeq: 2 BYE\n\n"
        self.sock.sendto(bye.encode(), (self.peer_ip, self.peer_port))
        print("[SIP] BYE sent.")

    def listen(self):
        """Listen for SIP responses."""
        while True:
            try:
                data, addr = self.sock.recvfrom(2048)
                message = data.decode()
                print(f"[SIP] Received:\n{message}")
                if "200 OK" in message and "CSeq: 1 INVITE" in message:
                    self.send_ack()
                    self.call_active = True
                    return self.parse_sdp(message)
                elif message.startswith("SIP/2.0 4") or message.startswith("SIP/2.0 5"):
                    print("[SIP] Received error response.")
                    break
            except Exception as e:
                print("[SIP] Error:", e)
                break

    def parse_sdp(self, message):
        """Extract media IP and port from the SDP body."""
        lines = message.splitlines()
        media_ip = None
        media_port = None
        for line in lines:
            if line.startswith("c=IN IP4"):
                media_ip = line.split()[-1]
            elif line.startswith("m=audio"):
                media_port = int(line.split()[1])
        print(f"[SIP] SDP Parsed - Media IP: {media_ip}, Port: {media_port}")
        return media_ip, media_port
