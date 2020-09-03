# Fast reading from the raspberry camera with Python, Numpy, and OpenCV
# Allows to process grayscale video up to 124 FPS (tested in Raspberry Zero Wifi with V2.1 camera)
#
# Made by @CarlosGS in May 2017
# Club de Robotica - Universidad Autonoma de Madrid
# http://crm.ii.uam.es/
# License: Public Domain, attribution appreciated

import cv2
import numpy as np
import subprocess as sp
import time
import atexit
from pyzbar.pyzbar import decode
from queue import Queue


class BarcodeScanner:
    """
    "raspividyuv" is the command that provides camera frames in YUV format
     "--output -" specifies stdout as the output
     "--timeout 0" specifies continuous video
     "--luma" discards chroma channels, only luminance is sent through the pipeline
    see "raspividyuv --help" for more information on the parameters
    """


    def __init__(self, width=640, height=240, fps=250):
        self.width = width
        self.height =height
        self.fps = fps
        self.queue = Queue(maxsize=30)
        self.camera = sp.Popen(self.VIDEO_CMD, stdout=sp.PIPE)

        atexit.register(self.camera.terminate)
        self.camera.stdout.read(self.bytes_per_frame)

    @property
    def video_cmd(self):
        return f"raspividyuv -w {str(self.width)} -h {str(self.height)} --output - --timeout 0 \
        --framerate {str(fps)} --luma --nopreview".split()

    @property
    def bytes_per_frame(self):
        return self.width * self.height

    def find_barcodes(self):
        while True:
            barcode = self.process_frame(self.camera)
            print(barcode)
            # self.queue.put(barcode)
        # TODO stop process and gracefuly handle errors

    def stop(self):
        self.camera.terminate() # stop the camera

    def process_frame(self):
        start_time = time.time()
        self.camera.stdout.flush() # discard any frames that we were not able to process in time
        # Parse the raw stream into a numpy array
        frame = np.fromfile(self.camera.stdout, count=self.bytes_per_frame, dtype=np.uint8)
        if frame.size != self.bytes_per_frame:
            raise IOError("Error: Camera stream closed unexpectedly")
        frame.shape = (self.height, self.width)  # set the correct dimensions for the numpy array
        
        # The frame can be processed here using any function in the OpenCV library.
        
        # Full image processing will slow down the pipeline, so the requested FPS should be set accordingly.
        #frame = cv2.Canny(frame, 50,150)
        # For instance, in this example you can enable the Canny edge function above.
        # You will see that the frame rate drops to ~35fps and video playback is erratic.
        # If you then set fps = 30 at the beginning of the script, there will be enough cycle time between frames to provide accurate video.
        # One optimization could be to work with a decimated (downscaled) version of the image: deci = frame[::2, ::2]
        end_time = time.time()
        elapsed_seconds = end_time - start_time
        print(f"Processing took {elapsed_seconds}")
        return frame

    @staticmethod
    def decode_barcode(frame):
        try:
            data = decode(frame)[0].data
            print(data)
            # FIXME sometimes, the decoding seems to miss something,
            # resulting in a string that is split in a tuple of len 1.
            # this cause
            return_val = tuple(int(i) for i in data.decode('utf8').split(","))
            if return_val == 2:
                return return_val
            print(f"Did not find comma separated value: {data.decode('utf8')}")
        except IndexError:
            print("Couldn't find any QR codes")
            print("Stream reading and QR detection took us %s s" % (time.monotonic() - start))
        except ValueError:
            print("Decodation of the QR code failed due to wrong result")



if __name__ == '__main__':
    bc = BarcodeScanner()
    bc.find_barcodes()
