import tkinter as tk
from sip_signaling import SIPSignaling
from rtp_receiver import RTPReceiver

class VoIPClient2:
    def __init__(self, master):
        self.master = master
        master.title("VoIP Client 2 (Receiver)")
        master.geometry("400x300")

        self.log_box = tk.Text(master, height=10, width=50)
        self.log_box.pack(pady=10)

        self.status_label = tk.Label(master, text="Waiting for call...", fg="blue")
        self.status_label.pack()

        self.end_btn = tk.Button(master, text="End Call", command=self.end_call, state=tk.DISABLED)
        self.end_btn.pack(pady=10)

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
            self.log("[SIP] Call Active. Receiving audio...")
            self.status_label.config(text="Call Active", fg="green")
            self.rtp.start()
            self.end_btn.config(state=tk.NORMAL)
        else:
            self.master.after(500, self.check_call_status)

    def end_call(self):
        self.log("Call ended.")
        self.status_label.config(text="Waiting for call...", fg="blue")
        self.rtp.stop()
        self.end_btn.config(state=tk.DISABLED)

# Run GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = VoIPClient2(root)
    root.mainloop()
