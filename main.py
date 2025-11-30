from visuals.eyes import RoboEyes
import pygame
import threading
import sys


import argparse
import queue
import sys
import sounddevice as sd

from vosk import Model, KaldiRecognizer

q = queue.Queue()
commands_queue = queue.Queue()


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "-l", "--list-devices", action="store_true",
    help="show list of audio devices and exit")
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    "-f", "--filename", type=str, metavar="FILENAME",
    help="audio file to store recording to")
parser.add_argument(
    "-d", "--device", type=int_or_str,
    help="input device (numeric ID or substring)")
parser.add_argument(
    "-r", "--samplerate", type=int, help="sampling rate")
parser.add_argument(
    "-m", "--model", type=str, help="language model; e.g. en-us, fr, nl; default is en-us")
args = parser.parse_args(remaining)

def eyes_thread(commands_queue):
    # Screen settings
    screen_width = 800   # Rotated width
    screen_height = 480  # Rotated height
    window = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("RoboEyes Simulation")

    # Create a separate surface for drawing (unrotated)
    draw_width = 800
    draw_height = 480
    draw_surface = pygame.Surface((draw_width, draw_height))

    # Create RoboEyes instance
    robo_eyes = RoboEyes(draw_surface, window, width=draw_width, height=draw_height, frame_rate=50)
    draw_surface.fill(robo_eyes.colors["BACKGROUND"])  # Ensure it's cleared initially
    robo_eyes.begin()

    # Example configurations
    robo_eyes.setMood(robo_eyes.moods["DEFAULT"])
    robo_eyes.setAutoblinker(True, interval=2, variation=3)
    robo_eyes.setIdleMode(True, interval=5, variation=5)
    robo_eyes.setCuriosity(True)
    # robo_eyes.setCyclops(False)
    # robo_eyes.setHFlicker(True, amplitude=4)
    # robo_eyes.setVFlicker(True, amplitude=20)
    clock = pygame.time.Clock()

    while True:
        robo_eyes.keep_going(commands_queue, clock)
        try:
            command = commands_queue.get_nowait()
            if command in robo_eyes.moods:
                robo_eyes.setMood(robo_eyes.moods[command])
            else:
                print(robo_eyes.moods)
        except queue.Empty:
            print("EMPTY QUEUE")


def main():
    pygame.init()

    if args.samplerate is None:
        device_info = sd.query_devices(args.device, "input")
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info["default_samplerate"])

    if args.model is None:
        model = Model(lang="it")
    else:
        model = Model(lang=args.model)

    if args.filename:
        dump_fn = open(args.filename, "wb")
    else:
        dump_fn = None

    t = threading.Thread(target=eyes_thread, args=(commands_queue,), kwargs={})
    t.start()

    with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device,
            dtype="int16", channels=1, callback=callback):
        print("#" * 80)
        print("Press Ctrl+C to stop the recording")
        print("#" * 80)

        rec = KaldiRecognizer(model, args.samplerate)
        while True:
            data = q.get()
            command = ""
            if rec.AcceptWaveform(data):
                command = rec.Result()
            else:
                command = rec.PartialResult()
            print(command)

            if "arrabbiat" in command:
                commands_queue.put("ANGRY")
            elif "trist" in command:
                commands_queue.put("TIRED")
            elif "normal" in command:
                commands_queue.put("TIRED")
            elif "felic" in command:
                commands_queue.put("TIRED")

if __name__ == "__main__":
    main()
