# VoipClientGUI.py
import tkinter as tk
from SipClient import SipClient
from RtpSender import RtpSender
from RtpReceiver import RtpReceiver
from RtcpHandler import RtcpHandler

class VoipClientGUI:
    def __init__(self, root, local_ip, local_sip_port, peer_ip, peer_sip_port, media_port, is_caller, audio_file=None):
        self.root = root
        self.root.title("VoIP Client")
        self.is_caller = is_caller
        self.audio_file = audio_file

        self.sip = SipClient(local_ip, local_sip_port, peer_ip, peer_sip_port, media_port)
        self.rtp = None
        self.rtcp = None
        self.receiver = None
        self.media_ip = None
        self.media_port = None

        self.status_label = tk.Label(root, text="Status: Idle")
        self.status_label.pack(pady=5)

        self.setup_button = tk.Button(root, text="Setup (INVITE)", command=self.setup_call)
        self.setup_button.pack(pady=5)

        self.play_button = tk.Button(root, text="Play", state='disabled', command=self.start_media)
        self.play_button.pack(pady=5)

        self.teardown_button = tk.Button(root, text="End Call (BYE)", state='disabled', command=self.end_call)
        self.teardown_button.pack(pady=5)

    def setup_call(self):
        if self.is_caller:
            self.sip.send_invite()
            self.media_ip, self.media_port = self.sip.listen()
        else:
            self.media_ip, self.media_port = self.sip.listen()
            self.sip.send_ack()

        self.status_label.config(text=f"Status: Call Setup → Media @ {self.media_ip}:{self.media_port}")
        self.play_button.config(state='normal')
        self.teardown_button.config(state='normal')

    def start_media(self):
        if self.is_caller and self.audio_file:
            self.rtp = RtpSender(self.audio_file, self.media_ip, self.media_port)
            self.rtcp = RtcpHandler(ssrc=12345, dest_ip=self.media_ip, dest_port=self.media_port + 1)
            self.rtcp.start()
            self.rtp.start_stream()
        else:
            self.receiver = RtpReceiver(self.sip.media_port)
            self.receiver.start_receiving()

        self.status_label.config(text="Status: Media Streaming")

    def end_call(self):
        self.status_label.config(text="Status: Ending Call")
        self.sip.send_bye()

        if self.rtp:
            self.rtp.stop_stream()
        if self.rtcp:
            self.rtcp.stop()
        if self.receiver:
            self.receiver.stop()

        self.play_button.config(state='disabled')
        self.teardown_button.config(state='disabled')
        self.status_label.config(text="Status: Call Ended")
