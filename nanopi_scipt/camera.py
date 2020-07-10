import numpy
import pathlib
from PIL import Image

from PyV4L2Camera.camera import Camera
from PyV4L2Camera.controls import ControlIDs

camera = Camera('/dev/video1', 1920, 1080)
controls = camera.get_controls()

for control in controls:
    print(control.name)

camera.set_control_value(ControlIDs.BRIGHTNESS, 48)

pathlib.Path('images').mkdir(parents=True, exist_ok=True)

for _ in range(2):
    frame = camera.get_frame()

    # Decode the image
    im = Image.frombytes('RGB', (camera.width, camera.height), frame, 'raw',
                         'RGB')

    # Convert the image to a numpy array and back to the pillow image
    arr = numpy.asarray(im)
    im = Image.fromarray(numpy.uint8(arr))

    # Display the image to show that everything works fine
    im.save("images/test.jpg")

camera.close()
