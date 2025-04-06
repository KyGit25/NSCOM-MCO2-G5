from SIPClient import SIPClient
from AudioStreamer import AudioStreamer
from RTCPHandler import RTCPHandler
import time

# Configuration
LOCAL_IP = "127.0.0.1"
LOCAL_SIP_PORT = 5060
REMOTE_IP = "127.0.0.1"
REMOTE_SIP_PORT = 6060
AUDIO_FILE = "audio.wav"  # Use a short 8kHz mono WAV file

# Start SIP client
sip = SIPClient(LOCAL_IP, LOCAL_SIP_PORT, REMOTE_IP, REMOTE_SIP_PORT)

# Event handler when 200 OK is received
def handle_ok(msg):
    print("[CLIENT 1] 200 OK received")
    remote_ip, remote_rtp_port = SIPClient.parse_sdp(msg)
    
    # Send ACK to confirm the call
    sip.send_ack()

    # Start streaming audio via RTP
    streamer = AudioStreamer(AUDIO_FILE, remote_ip, remote_rtp_port)
    ssrc = streamer.get_ssrc()

    # Start RTCP Sender Report on RTP+1
    rtcp = RTCPHandler(LOCAL_IP, LOCAL_SIP_PORT + 1, remote_ip, remote_rtp_port + 1, ssrc)
    rtcp.start_sending_reports()

    # Stream audio and update RTCP stats
    try:
        wf = streamer.stream()
    finally:
        rtcp.stop()

    # End call with BYE
    sip.send_bye()
    sip.close()

sip.on_ok = handle_ok
sip.start_listener()

# Begin SIP call
sip.send_invite()

# Keep main thread alive until streaming is done
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[CLIENT 1] Interrupted.")
    sip.send_bye()
    sip.close()
