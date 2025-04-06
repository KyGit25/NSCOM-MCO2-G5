import tkinter as tk
from SipClient import SipClient
from AudioSender import AudioSender
from AudioReceiver import AudioReceiver

class VoIPClientGUI:
    def __init__(self, master):
        self.master = master
        master.title("VoIP Audio Client")

        self.local_ip = "127.0.0.1"
        self.local_sip_port = 5060
        self.remote_ip = "127.0.0.1"
        self.remote_sip_port = 5070
        self.audio_port = 5004
        self.rtcp_port = 5005
        self.audio_file = "sample.wav"

        self.sip = None
        self.sender = None
        self.receiver = None

        # GUI Widgets
        tk.Label(master, text="Remote IP:").grid(row=0, column=0)
        self.ip_entry = tk.Entry(master)
        self.ip_entry.insert(0, self.remote_ip)
        self.ip_entry.grid(row=0, column=1)

        tk.Button(master, text="Call", width=20, command=self.start_call).grid(row=1, column=0, pady=5)
        tk.Button(master, text="Hang Up", width=20, command=self.end_call).grid(row=1, column=1, pady=5)

        self.status = tk.Label(master, text="Status: Ready")
        self.status.grid(row=2, column=0, columnspan=2)

    def start_call(self):
        self.remote_ip = self.ip_entry.get()
        self.status.config(text="Status: Calling...")

        self.sip = SipClient(self.local_ip, self.local_sip_port, self.remote_ip, self.remote_sip_port, self.audio_port)
        self.sip.send_invite()

        self.receiver = AudioReceiver(self.audio_port, rtcp_port=self.rtcp_port)
        self.receiver.start_receiving()

        self.sender = AudioSender(self.audio_file, self.remote_ip, self.audio_port, rtcp_port=self.rtcp_port)
        self.sender_thread = threading.Thread(target=self.sender.start_stream)
        self.sender_thread.start()

        self.status.config(text="Status: In Call")

    def end_call(self):
        if self.sender:
            self.sender.stop_stream()
        if self.receiver:
            self.receiver.stop_receiving()
        if self.sip:
            self.sip.send_bye()
        self.status.config(text="Status: Call Ended")
