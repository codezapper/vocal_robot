from visuals.eyes import RoboEyes
import pygame
import threading
import sys
import json


import argparse
import queue
import sys
import sounddevice as sd

from ollama import chat
from vosk import Model, KaldiRecognizer
from sunfounder_voice_assistant.tts import Piper
import subprocess
import os
import sys
from sunfounder_voice_assistant.tts import Piper 
from voice import VoiceInput
import time


def run_command(cmd=""):
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    return status, result



commands_queue = queue.Queue()


def main():
    kaldi_model = Model(lang="it")
    pygame.init()

    threads = [threading.Thread(target=RoboEyes.run_as_thread, args=(commands_queue,), kwargs={}), threading.Thread(target=VoiceInput.run_as_thread, args=(commands_queue,), kwargs={})]

    for thread in threads:
        thread.start()
    
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
