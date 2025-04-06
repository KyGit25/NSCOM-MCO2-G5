import socket
import threading
import pyaudio
from RtpPacket import RtpPacket

class AudioReceiver:
    def __init__(self, listen_port, rtcp_port=None):
        self.listen_port = listen_port
        self.rtcp_port = rtcp_port
        self.running = False
        self.rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rtp_socket.bind(('', self.listen_port))

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,  # Assuming 16-bit PCM
            channels=1,
            rate=8000,
            output=True
        )

    def start_receiving(self):
        print(f"[RTP] Listening on port {self.listen_port}...")
        self.running = True
        threading.Thread(target=self.receive_loop, daemon=True).start()

        if self.rtcp_port:
            threading.Thread(target=self.listen_rtcp, daemon=True).start()

    def receive_loop(self):
        while self.running:
            try:
                packet, addr = self.rtp_socket.recvfrom(20480)
                rtp_packet = RtpPacket()
                rtp_packet.decode(packet)
                payload = rtp_packet.getPayload()

                print(f"[RTP] Received Seq={rtp_packet.seqNum()} Len={len(payload)}")
                self.stream.write(payload)
            except Exception as e:
                print(f"[RTP] Error receiving: {e}")

    def listen_rtcp(self):
        rtcp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        rtcp_socket.bind(('', self.rtcp_port))
        while self.running:
            try:
                data, addr = rtcp_socket.recvfrom(1024)
                print(f"[RTCP] Received report from {addr}: {data.hex()}")
            except Exception as e:
                print(f"[RTCP] Error: {e}")

    def stop_receiving(self):
        self.running = False
        self.rtp_socket.close()
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        print("[RTP] Receiver stopped.")
