import sys
import tkinter as tk
from VoipClientGUI import VoipClientGUI

if __name__ == '__main__':
    mode = sys.argv[1]  # 'caller' or 'callee'
    local_ip = sys.argv[2]
    local_sip_port = int(sys.argv[3])
    peer_ip = sys.argv[4]
    peer_sip_port = int(sys.argv[5])
    media_port = int(sys.argv[6])
    audio_file = sys.argv[7] if mode == 'caller' else None

    root = tk.Tk()
    app = VoipClientGUI(
        root,
        local_ip,
        local_sip_port,
        peer_ip,
        peer_sip_port,
        media_port,
        is_caller=(mode == 'caller'),
        audio_file=audio_file
    )
    root.mainloop()
