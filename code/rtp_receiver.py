import socket
import threading
import struct
import pyaudio

class RTPReceiver:

    # initialize instance to listen for incoming packets
    # local_ip is address to listen on for incoming packets
    def __init__(self, local_ip, rtp_port):
        self.local_ip = local_ip
        self.rtp_port = rtp_port
        # create a UDP socket and bind it to the local IP and port to listen for incoming RTP packets
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((local_ip, rtp_port))

        # flag to track if receiver is running
        self.running = False

        # initialize PyAudio to play the received audio data
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,  # PCM 16-bit
            channels=1,             # mono audio channel
            rate=8000,              # audio rate of 8000 Hz
            output=True             # output audio
        )

    # parse rtp packet to extract audio, returns the audio
    def parse_rtp_packet(self, data):
        header = data[:12]
        payload = data[12:]
        version, payload_type = struct.unpack('!BB', header[:2])
        sequence_number, timestamp, ssrc = struct.unpack('!HII', header[2:])
        return payload

    # listen for the packets and processes the packets. also plays the audio
    def receive_audio(self):
        print("[RTP] Listening for incoming RTP packets...")

        # set flag to true
        self.running = True

        # while true
        while self.running:
            try:
                # receive data from the socket
                data, _ = self.socket.recvfrom(2048)
                # parse the RTP packet and extract the audio payload
                audio = self.parse_rtp_packet(data)
                # write the audio data to the output stream aka play the aduio
                self.stream.write(audio)
            except Exception as e:
                if not self.running:
                    break
                print("[RTP] Error:", e)

        print("[RTP] Stopped receiving.")

    # the "main" function of the RTCPSender instance
    def start(self):
        # create and start a new thread to receive packets
        thread = threading.Thread(target=self.receive_audio)
        thread.start()

    # stops all operations, cleans up
    def stop(self):
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.socket.close()
