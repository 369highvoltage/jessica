from cscore import CameraServer

def main():
    cs = CameraServer.getInstance()
    cs.enableLogging()

    cs.startAutomaticCapture()
    cs.waitForever()
