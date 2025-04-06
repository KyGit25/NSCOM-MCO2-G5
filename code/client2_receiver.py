from SIPClient import SIPClient
from AudioReceiver import AudioReceiver
from MicStreamer import MicStreamer
import time

LOCAL_IP = "127.0.0.1"
LOCAL_SIP_PORT = 6060
RTP_PORT = 7078
REMOTE_IP = "127.0.0.1"
REMOTE_SIP_PORT = 5060
use_mic_reply = False  # 🔄 Set to True to enable mic-based two-way reply

sip = SIPClient(LOCAL_IP, LOCAL_SIP_PORT, REMOTE_IP, REMOTE_SIP_PORT)
receiver = None
reply_streamer = None

def handle_invite(msg):
    print("[CLIENT 2] INVITE received")
    sip.send_ok()

def handle_ack(msg):
    print("[CLIENT 2] ACK received. Starting audio receiver...")
    global receiver, reply_streamer
    receiver = AudioReceiver(LOCAL_IP, RTP_PORT)
    receiver.start_receiving()

    if use_mic_reply:
        reply_streamer = MicStreamer(REMOTE_IP, RTP_PORT)
        reply_streamer.stream_microphone()

def handle_bye(msg):
    print("[CLIENT 2] BYE received. Ending call.")
    if receiver:
        receiver.close()
    sip.close()

sip.on_invite = handle_invite
sip.on_ack = handle_ack
sip.on_bye = handle_bye
sip.start_listener()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[CLIENT 2] Interrupted.")
    if receiver:
        receiver.close()
    sip.close()
