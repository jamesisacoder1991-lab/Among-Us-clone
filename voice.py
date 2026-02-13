#!/usr/bin/python3

import socket
import threading
import pyaudio


class Client:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True

        while True:
            try:
                self.target_ip = input('Enter IP address of server --> ')
                #self.target_port = int(input('Enter target port of server --> '))
                self.target_port = 4322

                self.s.connect((self.target_ip, self.target_port))

                break
            except OSError:
                print("Couldn't connect to server")

        chunk_size = 1024
        audio_format = pyaudio.paInt16
        channels = 1
        rate = 20000

        # initialise microphone recording
        self.p = pyaudio.PyAudio()
        self.playing_stream = self.p.open(
            format=audio_format,
            channels=channels,
            rate=rate,
            output=True,
            frames_per_buffer=chunk_size,
        )
        self.recording_stream = self.p.open(
            format=audio_format,
            channels=channels,
            rate=rate,
            input=True,
            frames_per_buffer=chunk_size,
        )

        print("Connected to Server")

        threading.Thread(target=self.receive_server_data, daemon=True).start()
        self.send_data_to_server()

    def stop(self):
        self.running = False

        try:
            self.s.close()
        except OSError:
            pass

        self.playing_stream.stop_stream()
        self.playing_stream.close()
        self.recording_stream.stop_stream()
        self.recording_stream.close()
        self.p.terminate()

    def receive_server_data(self):
        while self.running:
            try:
                data = self.s.recv(1024)
                if not data:
                    self.stop()
                    break
                self.playing_stream.write(data)
            except OSError:
                self.stop()
                break

    def send_data_to_server(self):
        try:
            while self.running:
                data = self.recording_stream.read(1024, exception_on_overflow=False)
                self.s.sendall(data)
        except (OSError, KeyboardInterrupt):
            self.stop()


client = Client()
