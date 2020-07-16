import pyaudio
import wave
import threading
from kivy_KoTA108 import Widgets
import time

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS=2
RATE = 4410
RECORD_SECONDS = 1

class audioRecord:
    def __init__(self):
        self.going = False
        self.process = None
        self.filename = ""
        self.p = pyaudio.PyAudio()
        self.devices = [None]
        self.error = False
        self.finish = False
        self.statusRecord = True

    def record(self, filename):
        if self.process and self.process.is_alive():
            self.going = False
            self.finish = True
        self.error = False

        self.process = threading.Thread(target=self._record)
        self.process.start()
        self.filename = filename

    def _record(self):
        try:
            frames = []
            stream = self.p.open(format=FORMAT,
                                 channels=CHANNELS,
                                 rate=RATE,
                                 input=True,
                                 frames_per_buffer=CHUNK)

            print("recording")
            self.going = True

            while self.going:
                for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                    data = stream.read(CHUNK)
                    frames.append(data)

            stream.stop_stream()
            stream.close()
            print("done")
            self.statusRecord = False

            # write the audio data to a file (tmp/tmp.wav)
            wf = wave.open(self.filename, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
        except Exception as e:
            self.error = True

    def getStatus(self):
        return self.statusRecord

    def getDeviceCount(self):
        return self.p.get_device_count()

    def getDeviceName(self, deviceID):
        return self.p.get_device_info_by_index(deviceID)["name"]

    def isInputDevice(self, deviceID):
        return int(self.p.get_device_info_by_index(deviceID)["maxInputChannels"]) > 0

    def getAPIName(self, deviceID):
        return self.p.get_host_api_info_by_index(self.p.get_device_info_by_index(deviceID)["hostApi"])["name"]

    def setToDefault(self):
        self.devices = [None]

    def setToDevices(self, devices):
        self.devices = devices

    def stop_recording(self):
        self.going = False

    def destroy(self):
        self.p.terminate()