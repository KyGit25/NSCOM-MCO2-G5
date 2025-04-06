import socket
import threading
import time
from collections import deque

class SIPHandler:
    def __init__(self, local_ip, local_port, remote_ip, remote_port):
        self.local_ip = local_ip
        self.local_port = local_port
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.sip_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sip_socket.bind((local_ip, local_port))
        self.call_id = str(int(time.time()))
        self.cseq = 1
        self.invite_sent = False
        self.call_established = False
        self.remote_rtp_port = None
        self.message_queue = deque()
        self.running = True
        
        # Start receiver thread
        threading.Thread(target=self.receive_messages).start()
        
    def generate_sip_message(self, method, sdp=None):
        """Generate SIP messages with required headers"""
        self.cseq += 1
        via = f"Via: SIP/2.0/UDP {self.local_ip}:{self.local_port};rport;branch=z9hG4bK{self.call_id}"
        from_header = f"From: <sip:{self.local_ip}:{self.local_port}>;tag={self.call_id}"
        to_header = f"To: <sip:{self.remote_ip}:{self.remote_port}>"
        call_id = f"Call-ID: {self.call_id}@{self.local_ip}"
        cseq = f"CSeq: {self.cseq} {method}"
        contact = f"Contact: <sip:{self.local_ip}:{self.local_port}>"
        max_forwards = "Max-Forwards: 70"
        
        message = [f"{method} sip:{self.remote_ip}:{self.remote_port} SIP/2.0",
                   via, from_header, to_header, call_id, cseq, contact, max_forwards]
        
        if sdp:
            content_type = "Content-Type: application/sdp"
            content_length = f"Content-Length: {len(sdp)}"
            message.extend([content_type, content_length, "", sdp])
        else:
            message.append("\r\n")
            
        return "\r\n".join(message)
    
    def send_invite(self, rtp_port):
        """Send SIP INVITE with SDP for RTP negotiation"""
        sdp = self.generate_sdp(rtp_port)
        invite = self.generate_sip_message("INVITE", sdp)
        self.sip_socket.sendto(invite.encode(), (self.remote_ip, self.remote_port))
        self.invite_sent = True
        print("Sent INVITE")
        
    def generate_sdp(self, rtp_port):
        """Generate SDP for media negotiation"""
        sdp = [
            "v=0",
            f"o=- {self.call_id} 1 IN IP4 {self.local_ip}",
            "s=VoIP Call",
            f"c=IN IP4 {self.local_ip}",
            "t=0 0",
            "m=audio {} RTP/AVP 0".format(rtp_port),
            "a=rtpmap:0 PCMU/8000",
            "a=sendrecv"
        ]
        return "\r\n".join(sdp)
    
    def send_ack(self):
        """Send ACK after receiving 200 OK"""
        ack = self.generate_sip_message("ACK")
        self.sip_socket.sendto(ack.encode(), (self.remote_ip, self.remote_port))
        print("Sent ACK")
        self.call_established = True
        
    def send_bye(self):
        """Send BYE to terminate call"""
        bye = self.generate_sip_message("BYE")
        self.sip_socket.sendto(bye.encode(), (self.remote_ip, self.remote_port))
        print("Sent BYE")
        self.call_established = False
        
    def receive_messages(self):
        """Receive and process incoming SIP messages"""
        while self.running:
            try:
                data, addr = self.sip_socket.recvfrom(4096)
                message = data.decode()
                print(f"Received message:\n{message}")
                
                if "INVITE" in message.split()[0]:
                    self.handle_invite(message, addr)
                elif "200 OK" in message:
                    self.handle_200_ok(message)
                elif "BYE" in message.split()[0]:
                    self.handle_bye()
                    
            except Exception as e:
                if self.running:
                    print(f"Error receiving SIP message: {e}")
                    
    def handle_invite(self, message, addr):
        """Handle incoming INVITE request"""
        if self.call_established:
            self.send_response("486 Busy Here")
            return
            
        # Parse SDP to get remote RTP port
        sdp_part = message.split("\r\n\r\n")[1]
        for line in sdp_part.split("\r\n"):
            if line.startswith("m=audio"):
                self.remote_rtp_port = int(line.split()[1])
                break
                
        self.remote_ip, self.remote_port = addr
        self.send_response("200 OK", self.generate_sdp(self.remote_rtp_port))
        self.call_established = True
        
    def handle_200_ok(self, message):
        """Handle 200 OK response to our INVITE"""
        if not self.invite_sent:
            return
            
        # Parse SDP to get remote RTP port
        sdp_part = message.split("\r\n\r\n")[1]
        for line in sdp_part.split("\r\n"):
            if line.startswith("m=audio"):
                self.remote_rtp_port = int(line.split()[1])
                break
                
        self.send_ack()
        
    def handle_bye(self):
        """Handle BYE request"""
        self.send_response("200 OK")
        self.call_established = False
        print("Call terminated by remote party")
        
    def send_response(self, status_code, sdp=None):
        """Send SIP response"""
        response = f"SIP/2.0 {status_code}"
        via = f"Via: SIP/2.0/UDP {self.remote_ip}:{self.remote_port};received={self.remote_ip}"
        from_header = f"From: <sip:{self.remote_ip}:{self.remote_port}>"
        to_header = f"To: <sip:{self.local_ip}:{self.local_port}>;tag={self.call_id}"
        call_id = f"Call-ID: {self.call_id}@{self.local_ip}"
        cseq = f"CSeq: {self.cseq} INVITE"
        contact = f"Contact: <sip:{self.local_ip}:{self.local_port}>"
        
        message = [response, via, from_header, to_header, call_id, cseq, contact]
        
        if sdp:
            content_type = "Content-Type: application/sdp"
            content_length = f"Content-Length: {len(sdp)}"
            message.extend([content_type, content_length, "", sdp])
        else:
            message.append("\r\n")
            
        self.sip_socket.sendto("\r\n".join(message).encode(), (self.remote_ip, self.remote_port))
        
    def close(self):
        """Clean up resources"""
        self.running = False
        self.sip_socket.close()
