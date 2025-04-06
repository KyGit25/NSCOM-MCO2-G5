import socket
import struct
import threading
import time
import audioop
import pyaudio
from collections import deque

class RTPHandler:
    def __init__(self, local_ip, local_rtp_port, local_rtcp_port):
        self.local_ip = local_ip
        self.local_rtp_port = local_rtp_port
        self.local_rtcp_port = local_rtcp_port
        self.remote_rtp_port = None
        self.remote_rtcp_port = None
        self.remote_ip = None
        self.ssrc = int(time.time())  # Random SSRC identifier
        self.sequence_num = 0
        self.timestamp = 0
        self.packet_count = 0
        self.octet_count = 0
        self.last_rtcp_time = 0
        self.running = False
        self.audio_active = False
        
        # Audio configuration
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 8000
        self.CHUNK = 160  # 20ms of audio at 8kHz
        
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        self.input_stream = None
        self.output_stream = None
        
        # Create sockets
        self.rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rtp_socket.bind((local_ip, local_rtp_port))
        
        self.rtcp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rtcp_socket.bind((local_ip, local_rtcp_port))
        
        # Queues for incoming packets
        self.rtp_queue = deque(maxlen=100)
        self.rtcp_queue = deque(maxlen=10)
        
    def set_remote(self, remote_ip, remote_rtp_port, remote_rtcp_port=None):
        """Set remote endpoint information"""
        self.remote_ip = remote_ip
        self.remote_rtp_port = remote_rtp_port
        self.remote_rtcp_port = remote_rtcp_port if remote_rtcp_port else remote_rtp_port + 1
        
    def start(self):
        """Start RTP and RTCP threads"""
        if self.running:
            return
            
        self.running = True
        threading.Thread(target=self._rtp_receiver, daemon=True).start()
        threading.Thread(target=self._rtcp_receiver, daemon=True).start()
        threading.Thread(target=self._rtcp_sender, daemon=True).start()
        
    def stop(self):
        """Stop all RTP/RTCP activities"""
        self.running = False
        self.stop_audio()
        self.rtp_socket.close()
        self.rtcp_socket.close()
        
    def start_audio(self):
        """Start audio capture and playback"""
        if self.audio_active:
            return
            
        self.audio_active = True
        self.input_stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
            stream_callback=self._audio_input_callback
        )
        
        self.output_stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            output=True,
            frames_per_buffer=self.CHUNK
        )
        
        print("Audio streaming started")
        
    def stop_audio(self):
        """Stop audio capture and playback"""
        if not self.audio_active:
            return
            
        self.audio_active = False
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
            
        print("Audio streaming stopped")
        
    def _audio_input_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio input - sends RTP packets"""
        if self.remote_ip and self.remote_rtp_port:
            # Create RTP packet
            rtp_packet = self._create_rtp_packet(in_data)
            self.rtp_socket.sendto(rtp_packet, (self.remote_ip, self.remote_rtp_port))
            
            # Update stats for RTCP
            self.packet_count += 1
            self.octet_count += len(in_data)
            
        return (in_data, pyaudio.paContinue)
        
    def _create_rtp_packet(self, payload):
        """Create RTP packet with header and payload"""
        self.sequence_num = (self.sequence_num + 1) % 65536
        self.timestamp = (self.timestamp + self.CHUNK) % 4294967296
        
        # RTP header (12 bytes)
        # Version (2), Padding (0), Extension (0), CSRC count (0) -> 0x80
        # Marker (0), Payload Type (0 for PCMU) -> 0x00
        header = struct.pack('!BBHII', 
                            0x80,  # Version/P/Extension/CC
                            0x00,  # Marker/Payload type
                            self.sequence_num,
                            self.timestamp,
                            self.ssrc)
                            
        return header + payload
        
    def _parse_rtp_packet(self, packet):
        """Parse RTP packet and return header fields and payload"""
        if len(packet) < 12:
            return None
            
        header = struct.unpack('!BBHII', packet[:12])
        version = (header[0] >> 6) & 0x03
        padding = (header[0] >> 5) & 0x01
        extension = (header[0] >> 4) & 0x01
        csrc_count = header[0] & 0x0F
        marker = (header[1] >> 7) & 0x01
        payload_type = header[1] & 0x7F
        sequence_num = header[2]
        timestamp = header[3]
        ssrc = header[4]
        
        payload = packet[12:]
        
        return {
            'version': version,
            'padding': padding,
            'extension': extension,
            'csrc_count': csrc_count,
            'marker': marker,
            'payload_type': payload_type,
            'sequence_num': sequence_num,
            'timestamp': timestamp,
            'ssrc': ssrc,
            'payload': payload
        }
        
    def _create_rtcp_sr(self):
        """Create RTCP Sender Report packet"""
        ntp_time = time.time() + 2208988800  # Convert to NTP timestamp
        ntp_sec = int(ntp_time)
        ntp_frac = int((ntp_time - ntp_sec) * 4294967296)
        
        # SR packet (8 bytes header + 20 bytes report blocks)
        packet = struct.pack('!BBHIIIIIIII',
                            0x80,  # Version/P/RC
                            200,   # PT (SR)
                            1,     # Length in words - 1
                            self.ssrc,
                            ntp_sec,
                            ntp_frac,
                            self.timestamp,
                            self.packet_count,
                            self.octet_count)
                            
        return packet
        
    def _parse_rtcp_packet(self, packet):
        """Parse RTCP packet"""
        if len(packet) < 8:
            return None
            
        header = struct.unpack('!BBH', packet[:4])
        version = (header[0] >> 6) & 0x03
        padding = (header[0] >> 5) & 0x01
        report_count = header[0] & 0x1F
        packet_type = header[1]
        length = header[2] * 4
        
        return {
            'version': version,
            'padding': padding,
            'report_count': report_count,
            'packet_type': packet_type,
            'length': length,
            'payload': packet[4:4+length]
        }
        
    def _rtp_receiver(self):
        """Thread to receive and process RTP packets"""
        while self.running:
            try:
                data, addr = self.rtp_socket.recvfrom(2048)
                if data:
                    parsed = self._parse_rtp_packet(data)
                    if parsed:
                        self.rtp_queue.append(parsed)
                        if self.output_stream and self.audio_active:
                            self.output_stream.write(parsed['payload'])
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"RTP receive error: {e}")
                    
    def _rtcp_receiver(self):
        """Thread to receive and process RTCP packets"""
        while self.running:
            try:
                data, addr = self.rtcp_socket.recvfrom(1024)
                if data:
                    parsed = self._parse_rtcp_packet(data)
                    if parsed:
                        self.rtcp_queue.append(parsed)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"RTCP receive error: {e}")
                    
    def _rtcp_sender(self):
        """Thread to periodically send RTCP reports"""
        while self.running:
            if self.remote_ip and self.remote_rtcp_port and time.time() - self.last_rtcp_time > 5:
                sr_packet = self._create_rtcp_sr()
                self.rtcp_socket.sendto(sr_packet, (self.remote_ip, self.remote_rtcp_port))
                self.last_rtcp_time = time.time()
            time.sleep(1)
