import socket
import wave
import time
import threading
import struct
import random

class RTPSender:

    # initialize the instance
    # rtp_ip and rtp_port is of the receiver
    # audio_path is the filepath of the audio file
    def __init__(self, rtp_ip, rtp_port, audio_path):
        self.rtp_ip = rtp_ip
        self.rtp_port = rtp_port
        self.audio_path = audio_path
        # create a UDP socket for sending RTP packets
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # initialize sequence number, timestamp, SSRC
        self.sequence_number = 0
        self.timestamp = 0
        self.ssrc = random.randint(1000, 5000)
        self.running = False

    #  builds RTP packet with a header and the audio payload.
    def build_rtp_packet(self, payload):
        version = 2
        padding = 0
        extension = 0
        cc = 0
        marker = 0
        payload_type = 0
        # create the header
        header = (
            (version << 6) | (padding << 5) | (extension << 4) | cc,
            (marker << 7) | payload_type,
            self.sequence_number,
            self.timestamp,
            self.ssrc
        )
        rtp_header = struct.pack('!BBHII', *header)

        # return the full RTP packet (header + payload)
        return rtp_header + payload

    # send the audio (file) through packets
    def send_audio(self):
        # open the WAV file to read audio data
        wf = wave.open(self.audio_path, 'rb')
        sample_rate = wf.getframerate()
        frame_size = 160

        # set to true
        self.running = True

        # while running, read and send the audio data in chunks
        while self.running:
            audio_data = wf.readframes(frame_size)
            if not audio_data:
                break  # EOF

            # build the packet, and send it
            rtp_packet = self.build_rtp_packet(audio_data)
            self.socket.sendto(rtp_packet, (self.rtp_ip, self.rtp_port))

            # increment the seq number
            self.sequence_number = (self.sequence_number + 1) % 65536
            self.timestamp += frame_size
            time.sleep(0.02)  # sleep for 20ms before sending next one
        # close the WAV file and stop the sender after reaching EOF
        wf.close()
        self.running = False
        print("[RTP] Finished sending audio.")

        # if RTCP sender exists, stop
        if self.rtcp_sender:
            self.rtcp_sender.stop()

    # the "main" function of the RTCPSender instance
    def start(self, rtcp_sender=None):
        self.rtcp_sender = rtcp_sender
        # create and start a new thread to send packets
        thread = threading.Thread(target=self.send_audio)
        thread.start()

    # stops all operations, cleans up
    def stop(self):
        self.running = False
