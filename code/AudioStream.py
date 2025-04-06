# AudioStream.py
class AudioStream:
    def __init__(self, filename):
        self.filename = filename
        try:
            self.file = open(filename, 'rb')
        except:
            raise IOError
        self.frameNum = 0

    def nextFrame(self):
        """Read next 160 bytes (20ms of G.711 PCM audio)."""
        data = self.file.read(160)  # fixed-size chunk
        if data:
            self.frameNum += 1
        return data

    def frameNbr(self):
        """Get current frame number."""
        return self.frameNum
