import tkinter as tk
from tkinter import ttk, messagebox
import threading
import socket
import time

class VoIPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python VoIP Client")
        self.root.geometry("400x300")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Network configuration
        self.local_ip = self.get_local_ip()
        self.local_sip_port = 5060
        self.local_rtp_port = 5004
        self.local_rtcp_port = 5005
        
        # SIP and RTP handlers
        self.sip_handler = None
        self.rtp_handler = None
        
        # Call state
        self.in_call = False
        self.remote_ip = None
        self.remote_sip_port = 5060
        
        # Create GUI
        self.create_widgets()
        
    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Connection info
        info_frame = ttk.LabelFrame(main_frame, text="Connection Info", padding="10")
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text=f"Your IP: {self.local_ip}").pack(anchor=tk.W)
        ttk.Label(info_frame, text="SIP Port: 5060 | RTP Port: 5004").pack(anchor=tk.W)
        
        # Remote address entry
        addr_frame = ttk.Frame(main_frame)
        addr_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(addr_frame, text="Remote IP:").pack(side=tk.LEFT, padx=5)
        self.remote_ip_entry = ttk.Entry(addr_frame)
        self.remote_ip_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.remote_ip_entry.insert(0, "127.0.0.1")
        
        # Call controls
        ctrl_frame = ttk.Frame(main_frame)
        ctrl_frame.pack(fill=tk.X, pady=10)
        
        self.call_button = ttk.Button(ctrl_frame, text="Call", command=self.start_call)
        self.call_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.hangup_button = ttk.Button(ctrl_frame, text="Hang Up", command=self.end_call, state=tk.DISABLED)
        self.hangup_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Status display
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.status_text = tk.Text(status_frame, height=8, state=tk.DISABLED, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Audio controls
        audio_frame = ttk.LabelFrame(main_frame, text="Audio Controls", padding="10")
        audio_frame.pack(fill=tk.X, pady=5)
        
        self.mute_button = ttk.Button(audio_frame, text="Mute", command=self.toggle_mute, state=tk.DISABLED)
        self.mute_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.speaker_button = ttk.Button(audio_frame, text="Speaker Off", command=self.toggle_speaker, state=tk.DISABLED)
        self.speaker_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Initialize SIP and RTP
        self.init_network()
        
    def init_network(self):
        """Initialize SIP and RTP handlers"""
        try:
            self.sip_handler = SIPHandler(self.local_ip, self.local_sip_port, "", 0)
            self.rtp_handler = RTPHandler(self.local_ip, self.local_rtp_port, self.local_rtcp_port)
            self.rtp_handler.start()
            self.update_status("System initialized and ready")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize network: {str(e)}")
            self.root.destroy()
            
    def update_status(self, message):
        """Update status text area"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        
    def start_call(self):
        """Initiate a call to remote party"""
        if self.in_call:
            return
            
        remote_ip = self.remote_ip_entry.get().strip()
        if not remote_ip:
            messagebox.showwarning("Warning", "Please enter remote IP address")
            return
            
        try:
            self.remote_ip = remote_ip
            self.sip_handler.remote_ip = remote_ip
            self.sip_handler.remote_port = self.remote_sip_port
            
            # Start the call
            self.sip_handler.send_invite(self.local_rtp_port)
            self.update_status(f"Calling {remote_ip}...")
            
            # Update UI
            self.call_button.config(state=tk.DISABLED)
            self.hangup_button.config(state=tk.NORMAL)
            self.mute_button.config(state=tk.NORMAL)
            self.speaker_button.config(state=tk.NORMAL)
            self.in_call = True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start call: {str(e)}")
            self.update_status(f"Call failed: {str(e)}")
            
    def end_call(self):
        """End the current call"""
        if not self.in_call:
            return
            
        try:
            if self.sip_handler.call_established:
                self.sip_handler.send_bye()
                self.update_status("Call ended")
            else:
                self.update_status("Call canceled")
                
            # Stop audio streams
            self.rtp_handler.stop_audio()
            
            # Reset UI
            self.call_button.config(state=tk.NORMAL)
            self.hangup_button.config(state=tk.DISABLED)
            self.mute_button.config(state=tk.DISABLED)
            self.speaker_button.config(state=tk.DISABLED)
            self.in_call = False
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to end call: {str(e)}")
            
    def toggle_mute(self):
        """Toggle mute state"""
        if not self.rtp_handler:
            return
            
        if self.rtp_handler.audio_active:
            self.rtp_handler.stop_audio()
            self.mute_button.config(text="Unmute")
            self.update_status("Microphone muted")
        else:
            self.rtp_handler.start_audio()
            self.mute_button.config(text="Mute")
            self.update_status("Microphone unmuted")
            
    def toggle_speaker(self):
        """Toggle speaker state"""
        # This would control speaker output in a real implementation
        if self.speaker_button["text"] == "Speaker Off":
            self.speaker_button.config(text="Speaker On")
            self.update_status("Speaker enabled")
        else:
            self.speaker_button.config(text="Speaker Off")
            self.update_status("Speaker disabled")
            
    def on_close(self):
        """Handle window close event"""
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            if self.in_call:
                self.end_call()
            if self.sip_handler:
                self.sip_handler.close()
            if self.rtp_handler:
                self.rtp_handler.stop()
            self.root.destroy()
            
def main():
    root = tk.Tk()
    app = VoIPApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
