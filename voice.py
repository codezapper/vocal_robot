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


class VoiceInput:
    def __init__(self):
        self.q = queue.Queue()
        self.tts = Piper(model='it_IT-paola-medium', length_scale=1.2, sample_rate=44100)
        #self.tts = Piper(model='it_IT-riccardo-x_low', length_scale=1.2, sample_rate=44100)
        self.model = Model(lang="it")
        self.tts = Piper(model='it_IT-paola-medium', length_scale=1.2, sample_rate=44100)
        self.tts.piper.config.sample_rate = 26000

    def callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.q.put(bytes(indata))

    @staticmethod
    def get_microphone_id():
        for device in sd.query_devices():
            if device["max_input_channels"] == 1:
                return device["index"]
        
        print("Microphone not found!")
        sys.exit(1)

    @staticmethod
    def run_as_thread(commands_queue):
        voice = VoiceInput()
        samplerate=16000
        # response = chat( model='gemma3:270m', messages=[{'role': 'system', 'content': 'you are a playful assistant and you always reply in the Italian language even when the request is in another language'}, {'role': 'user', 'content': 'Pronto per iniziare?'}],)
        with sd.RawInputStream(samplerate=samplerate, blocksize = 0, device=VoiceInput.get_microphone_id(),
                dtype="int16", channels=1, callback=voice.callback):
            print("#" * 80)
            print("Press Ctrl+C to stop the recording")
            print("#" * 80)

            rec = KaldiRecognizer(voice.model, samplerate)
            while True:
                data = voice.q.get()
                command = ""
                if rec.AcceptWaveform(data):
                    command = rec.Result()
                else:
                    command = rec.PartialResult()
                print(command)

                command_json = json.loads(command)
                actual_query = command_json.get("text", "")
                if "arrabbiat" in actual_query:
                    commands_queue.put("ANGRY")
                elif "trist" in actual_query:
                    commands_queue.put("TIRED")
                elif "normal" in actual_query:
                    commands_queue.put("DEFAULT")
                elif "felic" in actual_query:
                    commands_queue.put("HAPPY")
                else:
                    if actual_query:
                        response = chat( model='gemma3:270m', messages=[{'role': 'user', 'content': actual_query}],)
                        #  stream=True,
                    
                        # tts.say(".")
                        #for chunk in stream:
                        print(response['message']['content'], flush=True)
                        voice.tts.say(response['message']['content'].replace("😊", ""), stream=True)
                        #run_command('echo "' + response['message']['content'] + ' | piper --model /opt/piper_models/it_IT-riccardo-x_low --output-raw --length_scale 1.4 | aplay -r 16000 -f S16_LE -t raw -')
