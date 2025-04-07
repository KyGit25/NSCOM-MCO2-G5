import tkinter as tk
from sip_signaling import SIPSignaling
from rtp_receiver import RTPReceiver
from mic_sender import MicSender  # ← NEW

class VoIPClient2:
    def __init__(self, master):
        self.master = master
        master.title("VoIP Client 2 (Receiver)")
        master.geometry("400x350")

        self.log_box = tk.Text(master, height=10, width=50)
        self.log_box.pack(pady=10)

        self.status_label = tk.Label(master, text="Waiting for call...", fg="blue")
        self.status_label.pack()

        self.play_btn = tk.Button(master, text="Play", command=self.play_audio, state=tk.DISABLED)
        self.play_btn.pack(pady=5)

        self.teardown_btn = tk.Button(master, text="Teardown", command=self.end_call, state=tk.DISABLED)
        self.teardown_btn.pack(pady=10)

        # Configs
        self.local_ip = "127.0.0.1"
        self.remote_ip = "127.0.0.1"
        self.sip_port_local = 6060
        self.sip_port_remote = 5060
        self.rtp_port = 5004

        # Components
        self.sip = SIPSignaling(
            local_ip=self.local_ip,
            local_port=self.sip_port_local,
            remote_ip=self.remote_ip,
            remote_port=self.sip_port_remote,
            rtp_port=self.rtp_port
        )

        self.rtp = RTPReceiver(
            local_ip=self.local_ip,
            rtp_port=self.rtp_port
        )

        self.mic = MicSender(self.remote_ip, self.rtp_port)  # ← NEW mic sender
        self.mic_on = False  # ← NEW state tracker
        self.mic_btn = tk.Button(master, text="Mic ON", command=self.toggle_mic)  # ← Button
        self.mic_btn.pack(pady=5)  # ← Add button to GUI


        self.start_listening()

    def log(self, message):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)

    def start_listening(self):
        self.log("[SIP] Listening for incoming INVITE...")
        self.sip.listen()
        self.check_call_status()

    def check_call_status(self):
        if self.sip.call_active:
            self.log("[SIP] Call Active. Press 'Play' to start audio.")
            self.status_label.config(text="Call Active", fg="green")
            self.play_btn.config(state=tk.NORMAL)
            self.teardown_btn.config(state=tk.NORMAL)
        else:
            self.master.after(500, self.check_call_status)

    def play_audio(self):
        if not self.rtp.running:
            self.log("[RTP] Playing audio stream.")
            self.rtp.stop()
            self.rtp = RTPReceiver(local_ip=self.local_ip, rtp_port=self.rtp_port)

            self.rtp.start()
        else:
            self.log("[RTP] Audio already playing.")
        self.play_btn.config(state=tk.DISABLED)

    def end_call(self):
        self.log("[SIP] Call ended by receiver.")
        self.status_label.config(text="Waiting for call...", fg="blue")
        self.rtp.stop()
        self.play_btn.config(state=tk.DISABLED)
        self.teardown_btn.config(state=tk.DISABLED)
        self.sip.call_active = False  # Reset flag

        # allow listen again
        self.master.after(1000, self.start_listening)

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
    app = VoIPClient2(root)
    root.mainloop()

