import socket
import threading
from SIPMessage import SIPMessage

class SIPClient:
    def __init__(self, local_ip, local_port, peer_ip, peer_port):
        self.local_ip = local_ip
        self.local_port = local_port
        self.peer_ip = peer_ip
        self.peer_port = peer_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.local_ip, self.local_port))
        self.running = True
        self.on_invite = None
        self.on_bye = None
        self.on_ok = None
        self.on_ack = None

    def start_listener(self):
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def _listen_loop(self):
        while self.running:
            try:
                data, addr = self.socket.recvfrom(4096)
                msg = data.decode()
                print(f"[SIP] Received from {addr}:\n{msg}")

                if msg.startswith("INVITE"):
                    if self.on_invite:
                        self.on_invite(msg)
                elif msg.startswith("SIP/2.0 200 OK"):
                    if self.on_ok:
                        self.on_ok(msg)
                elif msg.startswith("ACK"):
                    if self.on_ack:
                        self.on_ack(msg)
                elif msg.startswith("BYE"):
                    if self.on_bye:
                        self.on_bye(msg)
            except Exception as e:
                print(f"[SIP] Error in listener: {e}")

    def send_invite(self):
        invite_msg = SIPMessage.build_invite(self.local_ip, self.local_port, self.peer_ip, self.peer_port)
        self.socket.sendto(invite_msg.encode(), (self.peer_ip, self.peer_port))
        print("[SIP] INVITE sent")

    def send_ok(self):
        ok_msg = SIPMessage.build_ok(self.local_ip, self.local_port, self.peer_ip)
        self.socket.sendto(ok_msg.encode(), (self.peer_ip, self.peer_port))
        print("[SIP] 200 OK sent")

    def send_ack(self):
        ack_msg = SIPMessage.build_ack(self.local_ip, self.local_port, self.peer_ip)
        self.socket.sendto(ack_msg.encode(), (self.peer_ip, self.peer_port))
        print("[SIP] ACK sent")

    def send_bye(self):
        bye_msg = SIPMessage.build_bye(self.local_ip, self.peer_ip)
        self.socket.sendto(bye_msg.encode(), (self.peer_ip, self.peer_port))
        print("[SIP] BYE sent")

    def close(self):
        self.running = False
        self.socket.close()
        print("[SIP] Socket closed")
