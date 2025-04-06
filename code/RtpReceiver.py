import socket
import threading
import pyaudio
from RtpPacket import RtpPacket

class RtpReceiver:
    def __init__(self, listen_port):
        self.listen_port = listen_port
        self.rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rtp_socket.bind(('', self.listen_port))
        self.rtp_socket.settimeout(1.0)
        self.playing = False
        self.audio = pyaudio.PyAudio()
        self.stream = None

    def start_receiving(self):
        self.playing = True
        self.stream = self.audio.open(format=pyaudio.paInt8,
                                      channels=1,
                                      rate=8000,
                                      output=True)
        threading.Thread(target=self.listen_rtp).start()
        print(f"[RTP] Listening for RTP on port {self.listen_port}...")

    def listen_rtp(self):
        while self.playing:
            try:
                data, _ = self.rtp_socket.recvfrom(20480)
                if data:
                    rtp = RtpPacket()
                    rtp.decode(data)
                    payload = rtp.getPayload()
                    self.stream.write(payload)
                    print(f"[RTP] Received packet #{rtp.seqNum()}")
            except socket.timeout:
                continue
            except Exception as e:
                print("[RTP] Error receiving:", e)
                break

    def stop(self):
        self.playing = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()
        self.rtp_socket.close()
        print("[RTP] Receiver stopped.")
