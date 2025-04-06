class SIPMessage:
    @staticmethod
    def build_invite(caller_ip, caller_port, callee_ip, callee_port, codec="PCMU", ssrc="12345"):
        return (
            f"INVITE sip:user@{callee_ip}:{callee_port} SIP/2.0\r\n"
            f"Via: SIP/2.0/UDP {caller_ip}:{caller_port};branch=z9hG4bK123456\r\n"
            f"From: <sip:user@{caller_ip}>;tag=1234\r\n"
            f"To: <sip:user@{callee_ip}>\r\n"
            f"Call-ID: 123456789@{caller_ip}\r\n"
            f"CSeq: 1 INVITE\r\n"
            f"Contact: <sip:user@{caller_ip}:{caller_port}>\r\n"
            f"Content-Type: application/sdp\r\n"
            f"Content-Length: {len(SIPMessage.build_sdp_body(caller_ip, caller_port, codec, ssrc))}\r\n\r\n"
            f"{SIPMessage.build_sdp_body(caller_ip, caller_port, codec, ssrc)}"
        )

    @staticmethod
    def build_sdp_body(ip, port, codec, ssrc):
        return (
            "v=0\r\n"
            f"o=- 0 0 IN IP4 {ip}\r\n"
            "s=VoIP Call\r\n"
            f"c=IN IP4 {ip}\r\n"
            "t=0 0\r\n"
            f"m=audio {port} RTP/AVP 0\r\n"
            "a=rtpmap:0 PCMU/8000\r\n"
            f"a=ssrc:{ssrc}\r\n"
        )

    @staticmethod
    def build_ok(callee_ip, callee_port, caller_ip):
        return (
            f"SIP/2.0 200 OK\r\n"
            f"Via: SIP/2.0/UDP {caller_ip};branch=z9hG4bK123456\r\n"
            f"From: <sip:user@{caller_ip}>;tag=1234\r\n"
            f"To: <sip:user@{callee_ip}>;tag=5678\r\n"
            f"Call-ID: 123456789@{caller_ip}\r\n"
            f"CSeq: 1 INVITE\r\n"
            f"Contact: <sip:user@{callee_ip}:{callee_port}>\r\n"
            f"Content-Type: application/sdp\r\n"
            f"Content-Length: {len(SIPMessage.build_sdp_body(callee_ip, callee_port, 'PCMU', '67890'))}\r\n\r\n"
            f"{SIPMessage.build_sdp_body(callee_ip, callee_port, 'PCMU', '67890')}"
        )

    @staticmethod
    def build_ack(caller_ip, caller_port, callee_ip):
        return (
            f"ACK sip:user@{callee_ip} SIP/2.0\r\n"
            f"Via: SIP/2.0/UDP {caller_ip}:{caller_port};branch=z9hG4bK123456\r\n"
            f"From: <sip:user@{caller_ip}>;tag=1234\r\n"
            f"To: <sip:user@{callee_ip}>;tag=5678\r\n"
            f"Call-ID: 123456789@{caller_ip}\r\n"
            f"CSeq: 1 ACK\r\n"
            f"Content-Length: 0\r\n\r\n"
        )

    @staticmethod
    def build_bye(caller_ip, callee_ip):
        return (
            f"BYE sip:user@{callee_ip} SIP/2.0\r\n"
            f"Via: SIP/2.0/UDP {caller_ip};branch=z9hG4bK123456\r\n"
            f"From: <sip:user@{caller_ip}>;tag=1234\r\n"
            f"To: <sip:user@{callee_ip}>;tag=5678\r\n"
            f"Call-ID: 123456789@{caller_ip}\r\n"
            f"CSeq: 2 BYE\r\n"
            f"Content-Length: 0\r\n\r\n"
        )

    @staticmethod
    def parse_sdp(sip_message):
        """Extracts IP, port, codec from SDP body"""
        try:
            lines = sip_message.splitlines()
            media_line = [l for l in lines if l.startswith("m=audio")][0]
            connection_line = [l for l in lines if l.startswith("c=IN IP4")][0]
            port = int(media_line.split()[1])
            ip = connection_line.split()[-1]
            return ip, port
        except Exception as e:
            print("Failed to parse SDP:", e)
            return None, None

