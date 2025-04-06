from SIPClient import SIPClient
from AudioReceiver import AudioReceiver
import time

# Configuration
LOCAL_IP = "127.0.0.1"
LOCAL_SIP_PORT = 6060
RTP_PORT = 7078  # Any unused UDP port
RTCP_PORT = RTP_PORT + 1
REMOTE_IP = "127.0.0.1"
REMOTE_SIP_PORT = 5060

# Start SIP client
sip = SIPClient(LOCAL_IP, LOCAL_SIP_PORT, REMOTE_IP, REMOTE_SIP_PORT)

receiver = None

# Handle incoming INVITE
def handle_invite(msg):
    print("[CLIENT 2] INVITE received")
    sip.send_ok()

# Handle ACK to start audio playback
def handle_ack(msg):
    print("[CLIENT 2] ACK received. Starting audio receiver...")
    global receiver
    receiver = AudioReceiver(LOCAL_IP, RTP_PORT)
    receiver.start_receiving()

# Handle BYE to end call
def handle_bye(msg):
    print("[CLIENT 2] BYE received. Ending call.")
    if receiver:
        receiver.close()
    sip.close()

sip.on_invite = handle_invite
sip.on_ack = handle_ack
sip.on_bye = handle_bye
sip.start_listener()

# Keep main thread alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[CLIENT 2] Interrupted.")
    if receiver:
        receiver.close()
    sip.close()
