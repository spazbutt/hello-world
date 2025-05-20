import numpy as np
import pyaudio
import threading
import time
import keyboard
import turtle
import tkinter as tk
from tkinter import simpledialog

#=====================
# Binaural Scalar Synthesizer 
#
# ====================
# CONFIGURATION
# ====================
sample_rate = 44100
duration = 0.3  # Seconds per tone for single note
volume = 0.5
detune_percent = 0.0014 # Initial binaural detuning (±0.7%)
#======================
# Default base frequency
#
#======================
base_freq = 316#TAB TO CHANGE fREQUENCY
#X7q5a96 decoded from 9 strings of digits mod%400
angles_grad = [7, 17, 37, 77, 107, 177, 257, 327, 47]

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

def compute_scale(base):
    return [round(base * 2**(angle / 400), 2) for angle in angles_grad]

frequencies = compute_scale(base_freq)

def generate_binaural_wave(freq, duration, detune):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    left = volume * np.sin(2 * np.pi * freq * (1 - detune) * t)
    right = volume * np.sin(2 * np.pi * freq * (1 + detune) * t)
    return np.vstack((left, right)).T.astype(np.float32).tobytes()

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
                draw_scale_visual(frequencies)

        except ValueError:
            print("Invalid input.")
        finally:
            root.after(100, root.destroy)

    threading.Thread(target=show_input).start()
        
# ====================
# TURTLE WINDOW (placeholder)
# ====================
turtle.bgcolor("black")
turtle.title("Binaural Synth Harmonics")
def pulse_circle(index):
    if index < 0 or index >= len(frequencies):
        return

    angle = angles_grad[index]
    radius = (index + 1) * (200 / len(frequencies))
    angle_deg = angle * 0.9  # grad → degrees
    x = radius * np.cos(np.radians(angle_deg))
    y = radius * np.sin(np.radians(angle_deg))

    # Pulse animation (grow/shrink)
    for r in [radius + 10, radius]:
        turtle.pu()
        turtle.goto(0, -r)
        turtle.pd()
        turtle.color("white")
        turtle.circle(r)
        turtle.pu()
        turtle.clear()  # remove the pulse after draw
        draw_scale_visual(frequencies)

def draw_scale_visual(frequencies, angles=angles_grad):
    turtle.reset()
    turtle.bgcolor("black")
    turtle.hideturtle()
    turtle.speed(0)
    turtle.colormode(255)

    max_radius = 200
    step = max_radius / len(frequencies)

    for i, (angle, freq) in enumerate(zip(angles, frequencies)):
        radius = (i + 1) * step
        angle_deg = angle * 0.9  # convert grad to degrees (400g = 360°)
        x = radius * np.cos(np.radians(angle_deg))
        y = radius * np.sin(np.radians(angle_deg))

        # Set color and draw
        turtle.pu()
        turtle.goto(0, -radius)
        turtle.pd()
        turtle.color(100 + i*15, 255 - i*20, 255)
        turtle.circle(radius)

        turtle.pu()
        turtle.goto(x, y)
        turtle.dot(10, "white")
        turtle.pu()

        turtle.goto(x + 10, y + 10)
        turtle.write(f"{freq:.1f} Hz", font=("Arial", 8, "normal"), align="left")

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
            detune_percent = max(0.0001, detune_percent - 0.0005)
            print(f"Binaural gap decreased: {round(detune_percent * 100, 2)}%")
            time.sleep(0.15)

        if keyboard.is_pressed("right"):
            detune_percent += 0.0005
            print(f"Binaural gap increased: {round(detune_percent * 100, 2)}%")
            time.sleep(0.15)

        time.sleep(0.01)

# ====================
# RUN
# ====================
try:
    print("TAB=Input base freq | SHIFT=Play | CTRL=Arp | UP/DOWN=Scale step | PGUP/DN=Octave | LEFT/RIGHT=Detune gap")
    threading.Thread(target=keyboard_listener, daemon=True).start()
    turtle.done()

except KeyboardInterrupt:
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("\nExited cleanly.")

