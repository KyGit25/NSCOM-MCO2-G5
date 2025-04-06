from SIPClient import SIPClient
from AudioStreamer import AudioStreamer
from MicStreamer import MicStreamer
from RTCPHandler import RTCPHandler
import time

# Configuration
LOCAL_IP = "127.0.0.1"
LOCAL_SIP_PORT = 5060
REMOTE_IP = "127.0.0.1"
REMOTE_SIP_PORT = 6060
AUDIO_FILE = "audio.wav"
use_mic = False  # 🔄 Set to True to use microphone input

sip = SIPClient(LOCAL_IP, LOCAL_SIP_PORT, REMOTE_IP, REMOTE_SIP_PORT)

def handle_ok(msg):
    print("[CLIENT 1] 200 OK received")
    remote_ip, remote_rtp_port = SIPClient.parse_sdp(msg)
    
    sip.send_ack()

    if use_mic:
        streamer = MicStreamer(remote_ip, remote_rtp_port)
    else:
        streamer = AudioStreamer(AUDIO_FILE, remote_ip, remote_rtp_port)

    ssrc = streamer.get_ssrc()
    rtcp = RTCPHandler(LOCAL_IP, LOCAL_SIP_PORT + 1, remote_ip, remote_rtp_port + 1, ssrc)
    rtcp.start_sending_reports()

    try:
        if use_mic:
            streamer.stream_microphone()
        else:
            streamer.stream()
    finally:
        rtcp.stop()

    sip.send_bye()
    sip.close()

sip.on_ok = handle_ok
sip.start_listener()

sip.send_invite()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[CLIENT 1] Interrupted.")
    sip.send_bye()
    sip.close()

except KeyboardInterrupt:
    print("\n[CLIENT 1] Interrupted.")
    sip.send_bye()
    sip.close()
