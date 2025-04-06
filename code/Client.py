from tkinter import *
import tkinter.messagebox
import socket, threading, sys, os
import pyaudio

from RtpPacket import RtpPacket

class Client:
    INIT = 0
    READY = 1
    PLAYING = 2
    state = INIT

    SETUP = 0
    PLAY = 1
    PAUSE = 2
    TEARDOWN = 3

    def __init__(self, master, serveraddr, serverport, rtpport, filename):
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.handler)
        self.createWidgets()

        self.serverAddr = serveraddr
        self.serverPort = int(serverport)
        self.rtpPort = int(rtpport)
        self.fileName = filename
        self.rtspSeq = 0
        self.sessionId = 0
        self.requestSent = -1
        self.teardownAcked = 0
        self.frameNbr = 0

        self.connectToServer()

        # Setup PyAudio
        self.audio = pyaudio.PyAudio()
        self.audioStream = None

    def createWidgets(self):
        self.setup = Button(self.master, width=20, text="Setup", command=self.setupAudio)
        self.setup.grid(row=1, column=0, padx=2, pady=2)

        self.start = Button(self.master, width=20, text="Play", command=self.playAudio)
        self.start.grid(row=1, column=1, padx=2, pady=2)

        self.pause = Button(self.master, width=20, text="Pause", command=self.pauseAudio)
        self.pause.grid(row=1, column=2, padx=2, pady=2)

        self.teardown = Button(self.master, width=20, text="Teardown", command=self.exitClient)
        self.teardown.grid(row=1, column=3, padx=2, pady=2)

        self.label = Label(self.master, text="VoIP Client Ready")
        self.label.grid(row=0, column=0, columnspan=4, padx=5, pady=5)

    def setupAudio(self):
        if self.state == self.INIT:
            self.sendRtspRequest(self.SETUP)

    def playAudio(self):
        if self.state == self.READY:
            self.playEvent = threading.Event()
            self.playEvent.clear()
            threading.Thread(target=self.listenRtp).start()
            self.sendRtspRequest(self.PLAY)

    def pauseAudio(self):
        if self.state == self.PLAYING:
            self.sendRtspRequest(self.PAUSE)

    def exitClient(self):
        self.sendRtspRequest(self.TEARDOWN)
        self.master.destroy()

    def listenRtp(self):
        self.audioStream = self.audio.open(format=pyaudio.paInt8,
                                           channels=1,
                                           rate=8000,
                                           output=True)

        while True:
            try:
                data = self.rtpSocket.recv(20480)
                if data:
                    rtpPacket = RtpPacket()
                    rtpPacket.decode(data)

                    currFrameNbr = rtpPacket.seqNum()
                    print(f"[RTP] Received packet #{currFrameNbr}")

                    if currFrameNbr > self.frameNbr:
                        self.frameNbr = currFrameNbr
                        self.audioStream.write(rtpPacket.getPayload())
            except:
                if self.playEvent.isSet():
                    break
                if self.teardownAcked:
                    self.rtpSocket.close()
                    break

    def connectToServer(self):
        self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.rtspSocket.connect((self.serverAddr, self.serverPort))
        except:
            tkinter.messagebox.showwarning('Connection Failed', f"Can't connect to {self.serverAddr}")

    def sendRtspRequest(self, requestCode):
        self.rtspSeq += 1
        request = ""

        if requestCode == self.SETUP and self.state == self.INIT:
            threading.Thread(target=self.recvRtspReply).start()
            request = f"SETUP {self.fileName} RTSP/1.0\nCSeq: {self.rtspSeq}\nTransport: RTP/UDP; client_port= {self.rtpPort}"
            self.requestSent = self.SETUP

        elif requestCode == self.PLAY and self.state == self.READY:
            request = f"PLAY {self.fileName} RTSP/1.0\nCSeq: {self.rtspSeq}\nSession: {self.sessionId}"
            self.requestSent = self.PLAY

        elif requestCode == self.PAUSE and self.state == self.PLAYING:
            request = f"PAUSE {self.fileName} RTSP/1.0\nCSeq: {self.rtspSeq}\nSession: {self.sessionId}"
            self.requestSent = self.PAUSE

        elif requestCode == self.TEARDOWN:
            request = f"TEARDOWN {self.fileName} RTSP/1.0\nCSeq: {self.rtspSeq}\nSession: {self.sessionId}"
            self.requestSent = self.TEARDOWN

        if request:
            self.rtspSocket.send(request.encode())
            print(f"[RTSP] Sent:\n{request}")

    def recvRtspReply(self):
        while True:
            reply = self.rtspSocket.recv(1024)
            if reply:
                self.parseRtspReply(reply.decode("utf-8"))
            if self.requestSent == self.TEARDOWN:
                self.rtspSocket.close()
                break

    def parseRtspReply(self, data):
        lines = data.split('\n')
        seqNum = int(lines[1].split(' ')[1])
        session = int(lines[2].split(' ')[1])

        if seqNum == self.rtspSeq:
            if self.sessionId == 0:
                self.sessionId = session
            if self.sessionId == session:
                if int(lines[0].split(' ')[1]) == 200:
                    if self.requestSent == self.SETUP:
                        self.state = self.READY
                        self.openRtpPort()
                        self.label.config(text="SETUP complete.")
                    elif self.requestSent == self.PLAY:
                        self.state = self.PLAYING
                        self.label.config(text="Playing audio...")
                    elif self.requestSent == self.PAUSE:
                        self.state = self.READY
                        self.playEvent.set()
                        self.label.config(text="Paused.")
                    elif self.requestSent == self.TEARDOWN:
                        self.state = self.INIT
                        self.teardownAcked = 1
                        self.label.config(text="Call Ended.")

    def openRtpPort(self):
        self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rtpSocket.settimeout(0.5)
        try:
            self.rtpSocket.bind(('', self.rtpPort))
        except:
            tkinter.messagebox.showwarning('Unable to Bind', f"RTP port {self.rtpPort} already in use.")

    def handler(self):
        self.pauseAudio()
        if tkinter.messagebox.askokcancel("Quit?", "Do you want to quit?"):
            self.exitClient()
        else:
            self.playAudio()
