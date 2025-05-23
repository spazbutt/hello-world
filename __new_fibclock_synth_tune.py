import itertools
from turtle import *
import turtle
import random
from math import *
import numpy as np
import pyaudio
import threading
import time
import keyboard
import tkinter as tk
from tkinter import simpledialog
playing = False
###=======================================
## Fibonacci period iterator mod 400
## with lt(total angle mod279) by Honkaloid
##  FROM X7Q5a96'S video description
##
##  1107019037 4012365277 2316042177
##  1772334507 9243672817 7012119257
##  3141592657 1447000727 7219341807
##
##  the digits define the angles that generate scale (mod 400)
##  I added 47 after todays video 5-19-2025...
##
###=======================================
# Binaural Scalar Synthesizer 
#
# ====================
# CONFIGURATION
# ====================
sample_rate = 44100
duration = 0.2  # Seconds per tone for single note
volume = 0.5
detune_percent = 0.009 # Initial binaural detuning (±0.7%)
#======================
# Default base frequency
#
#======================
base_freq = 257#TAB TO CHANGE fREQUENCY
#X7q5a96 decoded from 9 strings of digits mod%400
angles_grad = [0, 7, 17, 37, 47, 77, 107, 177, 257, 327, ]

# ====================
# STATE
# ====================
current_index = 0
octave_shift = 0
playing = False
arpeggiating = False

# PyAudio stream setup
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32, channels=2, rate=sample_rate, output=True)

# ====================
# FUNCTIONS
# ====================

# ====================
# TURTLE WINDOW (placeholder)
# ====================       
bgcolor('black')
colormode(255)
shape('turtle')
shapesize(3)
pensize(5)
#hideturtle()
turtle.speed(0)
color('black')
pd()
turtle.degrees(400)
colors = [
    (255, 0 ,255),    # 0 - magenta
    (0, 255, 255),    # 1 - cyan
    ]

##Fibonacci function
def Fibonacci():
    global playing
    r=390
    t=0
    m=0
    n=5
    o=0
    a,b = 0,1
    while t <= 4680:
        a,b= b,a+b
        c=a%10
        if t%60==0:
            shapesize(5)
            
            pencolor(colors[t%2])
            
            stamp()
            
            lt(279)#X7q5a96 desc mod%400(279)
            
            o+=279
            
            print(f"total degrees {o}")
            print(f"total travel {m}")
            print(f"iteration {t}")
            print(f" base freq {base_freq}")
            print(f" Gradian angles {angles_grad}")
            delay(0)
        pencolor(colors[t%2])
        shapesize(2)
        fd(10)
        lt(c)
        fd(c)
        t+=1
        o+=c
        m+=(c+n)
        #print(f"play angle/freq {angles_grad[c]}/{frequencies[c]}")
        play_tone(frequencies[c])
    playing = False
    
def compute_scale(base):
    return [round(base * 2**(angle / 400), 2) for angle in angles_grad]

frequencies = compute_scale(base_freq)

def generate_binaural_wave(freq, duration, detune):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    left = volume * np.sin(2 * np.pi * freq * (1 - detune) * t)
    right = volume * np.sin(2 * np.pi * freq * (1 + detune) * t)

    # Apply fade-in and fade-out (10 ms)
    fade_len = int(0.02 * sample_rate)  # 10ms fade
    fade_in = np.linspace(0, 1, fade_len)
    fade_out = np.linspace(1, 0, fade_len)

    # Apply to both channels
    left[:fade_len] *= fade_in
    left[-fade_len:] *= fade_out
    right[:fade_len] *= fade_in
    right[-fade_len:] *= fade_out

    return np.vstack((left, right)).T.astype(np.float32).tobytes()


##def generate_binaural_wave(freq, duration, detune):
##    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
##    left = volume * np.sin(2 * np.pi * freq * (1 - detune) * t)
##    right = volume * np.sin(2 * np.pi * freq * (1 + detune) * t)
##    return np.vstack((left, right)).T.astype(np.float32).tobytes()

def play_tone(freq):
    wave = generate_binaural_wave(freq, duration, detune_percent)
    stream.write(wave)

def arpeggio_loop():
    global arpeggiating
    while arpeggiating:
        freq = frequencies[current_index % len(frequencies)] * (2 ** octave_shift)
        play_tone(freq)
        time.sleep(0.1)
def update_scale_input():
    global base_freq, frequencies

    def show_input():
        root = tk.Tk()
        root.withdraw()  # Hide main window

        try:
            new_input = simpledialog.askstring("Base Frequency", "Enter new base frequency (e.g. 333):", parent=root)
            if new_input:
                base = float(new_input)
                base_freq = base
                frequencies[:] = compute_scale(base)

                # Print the new scale
                print(f"\n🎵 Updated base frequency to {base_freq} Hz")
                print("New scale (Hz):")
                for f in frequencies:
                    print(f"  {f:.2f}")
                #draw_scale_visual(frequencies)

        except ValueError:
            print("Invalid input.")
        finally:
            root.after(100, root.destroy)

    threading.Thread(target=show_input).start()

# ====================
# MAIN LOOP
# ====================

def keyboard_listener():
    global current_index, octave_shift, detune_percent
    global playing, arpeggiating

    arpeggio_thread = None

    while True:
        if keyboard.is_pressed("tab"):
            update_scale_input()
            time.sleep(0.5)

        if keyboard.is_pressed("shift") and not playing:
            playing = True
            freq = frequencies[current_index % len(frequencies)] * (2 ** octave_shift)
            play_tone(freq)
            playing = False

        if keyboard.is_pressed("ctrl") and not arpeggiating:
            arpeggiating = True
            arpeggio_thread = threading.Thread(target=arpeggio_loop)
            arpeggio_thread.start()

        if not keyboard.is_pressed("ctrl") and arpeggiating:
            arpeggiating = False
            if arpeggio_thread:
                arpeggio_thread.join()

        if keyboard.is_pressed("up"):
            current_index = (current_index + 1) % len(frequencies)
            time.sleep(0.15)

        if keyboard.is_pressed("down"):
            current_index = (current_index - 1) % len(frequencies)
            time.sleep(0.15)

        if keyboard.is_pressed("page up"):
            octave_shift += 1
            time.sleep(0.2)

        if keyboard.is_pressed("page down"):
            octave_shift -= 1
            time.sleep(0.2)

        if keyboard.is_pressed("left"):
            detune_percent = max(0.0001, detune_percent - 0.001)
            print(f"Binaural gap decreased: {round(detune_percent * 100, 2)}%")
            time.sleep(0.1)

        if keyboard.is_pressed("right"):
            detune_percent += 0.001
            print(f"Binaural gap increased: {round(detune_percent * 100, 2)}%")
            time.sleep(0.1)

        if keyboard.is_pressed("space") and not playing:
            playing = True
            threading.Thread(target=Fibonacci).start()
            time.sleep(0.1)


        time.sleep(0.01)

# ====================
# RUN
# ====================
try:
    print("TAB=Input base freq | SHIFT=Play | CTRL=Arp | UP/DOWN=Scale step | PGUP/DN=Octave | LEFT/RIGHT=Detune gap | SPACE=Start Visualization")
    threading.Thread(target=keyboard_listener, daemon=True).start()



    turtle.done()

except KeyboardInterrupt:

    ###seperation
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("\nExited cleanly.")




