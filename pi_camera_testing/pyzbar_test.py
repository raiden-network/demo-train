import numpy
import pathlib
import time
from PIL import Image
from PyV4L2Camera.camera import Camera
from PyV4L2Camera.controls import ControlIDs

from pyzbar.pyzbar import decode


def run():
    camera = Camera('/dev/video0')
    # OLD CAMERA SETTINGS
    # camera = Camera('/dev/video0', 640, 240)

    """
    Camera Settings 
    """
    # controls = camera.get_controls()
    # for control in controls:
    #    print(control.name)
    #    print(camera.get_control_value(control.id))

    # Video setting options are:
    # options = [ControlIDs.AUTO_WHITE_BALANCE, ControlIDs.BACKLIGHT_COMPENSATION,
    #           ControlIDs.BLACK_LEVEL, ControlIDs.BLUE_BALANCE, ControlIDs.BRIGHTNESS,
    #           ControlIDs.CHROMA_AGC, ControlIDs.COLORFX, ControlIDs.COLOR_KILLER,
    #           ControlIDs.CONTRAST, ControlIDs.DO_WHITE_BALANCE, ControlIDs.EXPOSURE,
    #           ControlIDs.GAIN, ControlIDs.GAMMA, ControlIDs.HFLIP, ControlIDs.HUE,
    #           ControlIDs.HUE_AUTO, ControlIDs.POWER_LINE_FREQUENCY, ControlIDs.RED_BALANCE,
    #           ControlIDs.SATURATION, ControlIDs.SHARPNESS, ControlIDs.VFLIP,
    #           ControlIDs.WHITENESS, ControlIDs.WHITE_BALANCE_TEMPERATURE]
    camera.set_control_value(ControlIDs.CONTRAST, 10)
    camera.set_control_value(ControlIDs.SATURATION, 10)

    pathlib.Path('images').mkdir(parents=True, exist_ok=True)

    while True:
        start = time.monotonic()
        for _ in range(2):
            frame = camera.get_frame()

            # Decode the image
            im = Image.frombytes('RGB', (camera.width, camera.height), frame, 'raw',
                                 'RGB')

            # Convert the image to a numpy array and back to the pillow image
            # arr = numpy.asarray(im)
            # im = Image.fromarray(numpy.uint8(arr))
            # Save the image to show that everything works fine
            im.save(f"images/test{time.monotonic()}.jpg")
            try:
                data = decode(im)[0].data
                camera.close()
                print(eval(data.decode('utf8')))
                return eval(data.decode('utf8'))
            except IndexError:
                print("Couldn't find any QR codes")
            print("Stream reading and QR detection took us %s s" % (time.monotonic() - start))


if __name__ == "__main__":
    run()
