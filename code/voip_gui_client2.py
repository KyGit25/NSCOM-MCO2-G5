import tkinter as tk
from sip_signaling import SIPSignaling
from rtp_receiver import RTPReceiver

class VoIPClient2:
    def __init__(self, master):

        # create the frame of the gui
        self.master = master
        master.title("VoIP Client 2 (Receiver)")
        master.geometry("400x350")

        # gui elements
        self.log_box = tk.Text(master, height=10, width=50)
        self.log_box.pack(pady=10)

        self.status_label = tk.Label(master, text="Waiting for call...", fg="blue")
        self.status_label.pack()

        self.play_btn = tk.Button(master, text="Play", command=self.play_audio, state=tk.DISABLED)
        self.play_btn.pack(pady=5)

        self.pause_btn = tk.Button(master, text="Pause", command=self.pause_audio, state=tk.DISABLED)
        self.pause_btn.pack(pady=5)

        self.teardown_btn = tk.Button(master, text="End Call", command=self.end_call, state=tk.DISABLED)
        self.teardown_btn.pack(pady=10)

        # configurations
        self.local_ip = "127.0.0.1"
        self.remote_ip = "127.0.0.1"
        self.sip_port_local = 6060
        self.sip_port_remote = 5060
        self.rtp_port = 5004

        # back-end components

        # used for handling sessions
        self.sip = SIPSignaling(
            local_ip=self.local_ip,
            local_port=self.sip_port_local,
            remote_ip=self.remote_ip,
            remote_port=self.sip_port_remote,
            rtp_port=self.rtp_port
        )

        # used for receiving audio
        self.rtp = RTPReceiver(
            local_ip=self.local_ip,
            rtp_port=self.rtp_port
        )

        self.start_listening()

    # a function for printing messages in the gui
    def log(self, message):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)

    # a function for listening to SIP messages
    def start_listening(self):
        self.log("[SIP] Listening for incoming INVITE...")
        self.sip.listen()
        self.check_call_status()

    # a function for checking the status of the call
    def check_call_status(self):
        if self.sip.call_active:
            # if the call is active but gui states its not active, then change it to active
            if self.status_label.cget("text") != "Call Active":
                self.log("[SIP] Call Active. Press 'Play' to start audio.")
                self.status_label.config(text="Call Active", fg="green")
                self.play_btn.config(state=tk.NORMAL)
                self.pause_btn.config(state=tk.DISABLED)
                self.teardown_btn.config(state=tk.NORMAL)
        else:
            # if the call is not active but gui states it is active, then change it to inactive
            if self.status_label.cget("text") == "Call Active":
                self.log("[SIP] Caller ended the call.")
                self.status_label.config(text="Waiting for call...", fg="blue")
                self.rtp.stop()
                self.play_btn.config(state=tk.DISABLED)
                self.pause_btn.config(state=tk.DISABLED)
                self.teardown_btn.config(state=tk.DISABLED)
                self.master.after(1000, self.start_listening)

        self.master.after(500, self.check_call_status)

    # a function used for playing audio through usage of RTP
    def play_audio(self):
        if not self.rtp.running:
            self.log("[RTP] Playing audio stream.")
            self.rtp.stop()
            self.rtp = RTPReceiver(local_ip=self.local_ip, rtp_port=self.rtp_port)

            self.rtp.start()
        else:
            self.log("[RTP] Audio already playing.")
        self.play_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)

    # a function for pausing the audio
    def pause_audio(self):
        if self.rtp.running:
            self.log("[RTP] Audio paused.")
            self.rtp.stop()
        self.play_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)

    # a function for ending the session between client 1
    def end_call(self):
        # print message
        self.log("[SIP] Ending call...")
        # change back to waiting for call
        self.status_label.config(text="Waiting for call...", fg="blue")
        # stop the actions, clean up
        self.rtp.stop()
        self.play_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.DISABLED)
        self.teardown_btn.config(state=tk.DISABLED)
        self.sip.call_active = False  # reset flag

        # send a BYE message to client 1
        self.sip.send_bye()

        # allow listen again
        self.master.after(1000, self.start_listening)

# run GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = VoIPClient2(root)
    root.mainloop()

