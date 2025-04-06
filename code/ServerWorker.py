from random import randint
import sys, threading, socket
from AudioStream import AudioStream
from RtpPacket import RtpPacket

class ServerWorker:
    SETUP = 'SETUP'
    PLAY = 'PLAY'
    PAUSE = 'PAUSE'
    TEARDOWN = 'TEARDOWN'

    INIT = 0
    READY = 1
    PLAYING = 2
    state = INIT

    OK_200 = 0
    FILE_NOT_FOUND_404 = 1
    CON_ERR_500 = 2

    clientInfo = {}

    def __init__(self, clientInfo):
        self.clientInfo = clientInfo

    def run(self):
        threading.Thread(target=self.recvRtspRequest).start()

    def recvRtspRequest(self):
        connSocket = self.clientInfo['rtspSocket'][0]
        while True:
            data = connSocket.recv(256)
            if data:
                print("RTSP Received:\n" + data.decode("utf-8"))
                self.processRtspRequest(data.decode("utf-8"))

    def processRtspRequest(self, data):
        request = data.split('\n')
        requestType = request[0].split(' ')[0]
        filename = request[0].split(' ')[1]
        seq = request[1].split(' ')[1]

        if requestType == self.SETUP and self.state == self.INIT:
            try:
                self.clientInfo['audioStream'] = AudioStream(filename)
                self.state = self.READY
            except IOError:
                self.replyRtsp(self.FILE_NOT_FOUND_404, seq)
                return

            self.clientInfo['session'] = randint(100000, 999999)
            self.replyRtsp(self.OK_200, seq)

            # Extract RTP port from Transport header
            self.clientInfo['rtpPort'] = int(request[2].split(' ')[3])
            print(f"[SETUP] RTP port set to {self.clientInfo['rtpPort']}")

        elif requestType == self.PLAY and self.state == self.READY:
            self.state = self.PLAYING
            self.clientInfo['event'] = threading.Event()
            self.replyRtsp(self.OK_200, seq)

            self.clientInfo['rtpSocket'] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.clientInfo['worker'] = threading.Thread(target=self.sendRtp)
            self.clientInfo['worker'].start()
            print("[PLAY] Streaming started.")

        elif requestType == self.PAUSE and self.state == self.PLAYING:
            self.state = self.READY
            self.clientInfo['event'].set()
            self.replyRtsp(self.OK_200, seq)
            print("[PAUSE] Streaming paused.")

        elif requestType == self.TEARDOWN:
            self.clientInfo['event'].set()
            self.replyRtsp(self.OK_200, seq)
            self.clientInfo['rtpSocket'].close()
            print("[TEARDOWN] Session ended.")
            self.state = self.INIT

    def sendRtp(self):
        """Send RTP packets with audio frames."""
        while True:
            self.clientInfo['event'].wait(0.02)  # 20ms interval
            if self.clientInfo['event'].is_set():
                break

            data = self.clientInfo['audioStream'].nextFrame()
            if data:
                frameNbr = self.clientInfo['audioStream'].frameNbr()
                try:
                    packet = self.makeRtp(data, frameNbr)
                    addr = self.clientInfo['rtspSocket'][1][0]
                    port = self.clientInfo['rtpPort']
                    self.clientInfo['rtpSocket'].sendto(packet, (addr, port))
                    print(f"[RTP] Sent packet #{frameNbr}")
                except Exception as e:
                    print("[RTP] Error sending packet:", e)
            else:
                break  # EOF

    def makeRtp(self, payload, frameNbr):
        rtpPacket = RtpPacket()
        rtpPacket.encode(
            version=2,
            padding=0,
            extension=0,
            cc=0,
            seqnum=frameNbr,
            marker=0,
            pt=0,        # Payload Type 0 = G.711
            ssrc=12345,
            payload=payload
        )
        return rtpPacket.getPacket()

    def replyRtsp(self, code, seq):
        connSocket = self.clientInfo['rtspSocket'][0]
        if code == self.OK_200:
            reply = f"RTSP/1.0 200 OK\nCSeq: {seq}\nSession: {self.clientInfo['session']}"
            connSocket.send(reply.encode())
        elif code == self.FILE_NOT_FOUND_404:
            print("[RTSP] 404 NOT FOUND")
        elif code == self.CON_ERR_500:
            print("[RTSP] 500 CONNECTION ERROR")
