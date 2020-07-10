import subprocess
import time


def run():
    while True:
        start = time.monotonic()
        try:
            barcode = subprocess.check_output(["zbarcam", "--nodisplay"])
        except subprocess.CalledProcessError as e:
            print("Fuck an error")
            continue
        print(barcode)
        print("Stream reading and QR detection took us %s s" % (time.monotonic() - start))


if __name__ == "__main__":
    run()
