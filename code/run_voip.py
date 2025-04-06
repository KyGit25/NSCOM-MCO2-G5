import sys
from tkinter import Tk
from Client import Client  # ✅ Use your working Client.py

if __name__ == "__main__":
    try:
        mode = sys.argv[1]
        local_ip = sys.argv[2]
        local_sip_port = sys.argv[3]
        peer_ip = sys.argv[4]
        peer_sip_port = sys.argv[5]
        rtp_port = sys.argv[6]
        filename = sys.argv[7] if mode == "caller" else "dummy.wav"
    except:
        print("Usage: python run_voip.py <caller|callee> localIP localSIPPort peerIP peerSIPPort rtpPort [audioFile.wav]")
        sys.exit(1)

    root = Tk()
    app = Client(root, peer_ip, peer_sip_port, rtp_port, filename)
    app.master.title("VoIP Audio Client")
    root.mainloop()
