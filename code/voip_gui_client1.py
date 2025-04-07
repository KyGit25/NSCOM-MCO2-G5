import os
import wave
import tkinter as tk
from tkinter import filedialog
from sip_signaling import SIPSignaling
from rtp_sender import RTPSender
from rtcp_sender import RTCPSender
from mic_sender import MicSender

class VoIPClient1:
    def __init__(self, master):
        self.master = master
        master.title("VoIP Client 1 (Caller)")
        master.geometry("400x300")

        self.log_box = tk.Text(master, height=10, width=50)
        self.log_box.pack(pady=10)

        self.select_btn = tk.Button(master, text="Choose Audio File", command=self.select_audio_file)
        self.select_btn.pack(pady=5)

        self.call_btn = tk.Button(master, text="Start Call", command=self.start_call)
        self.call_btn.pack(pady=5)

        self.end_btn = tk.Button(master, text="End Call", command=self.end_call, state=tk.DISABLED)
        self.end_btn.pack(pady=5)

        # Network and Audio Config (Edit these for your local test)
        self.local_ip = "127.0.0.1"
        self.remote_ip = "127.0.0.1"
        self.sip_port_local = 5060
        self.sip_port_remote = 6060
        self.rtp_port = 5004
        self.rtcp_port = 5005
        self.audio_file = "audio.wav"  # Ensure this exists

        # Initialize objects
        self.sip = SIPSignaling(
            local_ip=self.local_ip,
            local_port=self.sip_port_local,
            remote_ip=self.remote_ip,
            remote_port=self.sip_port_remote,
            rtp_port=self.rtp_port
        )

        self.rtp = RTPSender(
            rtp_ip=self.remote_ip,
            rtp_port=self.rtp_port,
            audio_path=self.audio_file
        )

        self.rtcp = RTCPSender(
            remote_ip=self.remote_ip,
            rtcp_port=self.rtcp_port
        )

        self.mic = MicSender(self.remote_ip, self.rtp_port)  # ← NEW mic sender
        self.mic_on = False  # ← NEW state tracker
        self.mic_btn = tk.Button(master, text="Mic ON", command=self.toggle_mic)  # ← Button
        self.mic_btn.pack(pady=5)  # ← Add button to GUI

    def select_audio_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if not filepath:
            self.log("No file selected.")
            return

        # Verify format
        try:
            with wave.open(filepath, 'rb') as wf:
                if wf.getnchannels() != 1 or wf.getframerate() != 8000 or wf.getsampwidth() != 2:
                    self.log("Audio must be 8kHz, 16-bit, mono WAV.")
                    return
        except Exception as e:
            self.log(f"Invalid WAV file: {e}")
            return

        self.audio_file = filepath
        self.log(f"Audio file loaded: {os.path.basename(filepath)}")


    def log(self, text):
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.see(tk.END)

    def start_call(self):
        if not self.audio_file:
            self.log("Please choose an audio file before calling.")
            return        
        self.log("Starting call...")
        self.sip.listen()
        self.sip.send_invite()
        self.call_btn.config(state=tk.DISABLED)
        self.end_btn.config(state=tk.NORMAL)

        # Wait a moment for 200 OK, then start RTP
        self.master.after(1000, self.start_media)


    def start_media(self):
        if self.sip.call_active:
            self.log("Call accepted. Starting RTP + RTCP...")
            self.rtp.start(rtcp_sender=self.rtcp)
            self.rtcp.start()

        else:
            self.log("Waiting for call to be accepted...")
            self.master.after(500, self.start_media)

    def end_call(self):
        self.log("Ending call...")
        self.sip.send_bye()
        self.rtp.stop()
        self.rtcp.stop()
        self.call_btn.config(state=tk.NORMAL)
        self.end_btn.config(state=tk.DISABLED)
        
    def toggle_mic(self):
        if not self.sip.call_active:
            self.log("Mic can't start before call is active.")
            return

        if not self.mic_on:
            self.log("Microphone streaming started.")
            self.mic.start()
            self.mic_btn.config(text="Mic OFF")
        else:
            self.log("Microphone streaming stopped.")
            self.mic.stop()
            self.mic_btn.config(text="Mic ON")

        self.mic_on = not self.mic_on


# Run GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = VoIPClient1(root)
    root.mainloop()
