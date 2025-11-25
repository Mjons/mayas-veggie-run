"""
Generate simple synthesized sound effects for Maya's Veggie Run
Run this script to create basic WAV files for the game
"""
import numpy as np
import wave
import struct

SAMPLE_RATE = 44100

def generate_sine_wave(frequency, duration, volume=0.5):
    """Generate a sine wave at the given frequency"""
    samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, samples)
    wave_data = np.sin(2 * np.pi * frequency * t) * volume
    return wave_data

def generate_sweep(start_freq, end_freq, duration, volume=0.5):
    """Generate a frequency sweep (pitch change)"""
    samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, samples)
    # Linear frequency sweep
    freq = np.linspace(start_freq, end_freq, samples)
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    wave_data = np.sin(phase) * volume
    return wave_data

def apply_envelope(wave_data, attack=0.01, decay=0.1, sustain=0.7, release=0.2):
    """Apply ADSR envelope to smooth the sound"""
    samples = len(wave_data)
    envelope = np.ones(samples)

    attack_samples = int(attack * SAMPLE_RATE)
    release_samples = int(release * SAMPLE_RATE)

    # Attack
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    # Release
    if release_samples > 0:
        envelope[-release_samples:] = np.linspace(1, 0, release_samples)

    return wave_data * envelope

def save_wav(filename, wave_data):
    """Save wave data as a WAV file"""
    # Normalize and convert to 16-bit integers
    wave_data = np.int16(wave_data * 32767)

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes (16-bit)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(wave_data.tobytes())

    print(f"[OK] Created {filename}")

def create_jump_sound():
    """Create a jump sound - rising pitch"""
    sound = generate_sweep(200, 600, 0.15, volume=0.4)
    sound = apply_envelope(sound, attack=0.01, release=0.08)
    save_wav("assets/sounds/jump.wav", sound)

def create_collect_sound():
    """Create a collect sound - pleasant chime"""
    # Two quick tones
    tone1 = generate_sine_wave(800, 0.08, volume=0.3)
    tone2 = generate_sine_wave(1200, 0.08, volume=0.3)
    sound = np.concatenate([tone1, tone2])
    sound = apply_envelope(sound, attack=0.005, release=0.05)
    save_wav("assets/sounds/collect.wav", sound)

def create_hit_sound():
    """Create a hit sound - harsh low thud"""
    # Mix of low frequencies for impact
    sound1 = generate_sine_wave(100, 0.15, volume=0.4)
    sound2 = generate_sine_wave(150, 0.15, volume=0.3)
    sound = sound1 + sound2
    sound = apply_envelope(sound, attack=0.001, release=0.1)
    save_wav("assets/sounds/hit.wav", sound)

def create_love_sound():
    """Create a love sound - happy ascending tones"""
    # Happy ascending melody
    tones = [
        generate_sine_wave(523, 0.1, volume=0.25),  # C
        generate_sine_wave(659, 0.1, volume=0.25),  # E
        generate_sine_wave(784, 0.15, volume=0.3),  # G
    ]
    sound = np.concatenate(tones)
    sound = apply_envelope(sound, attack=0.01, release=0.1)
    save_wav("assets/sounds/love.wav", sound)

def create_game_over_sound():
    """Create a game over sound - descending sad tones"""
    # Sad descending melody
    tones = [
        generate_sine_wave(392, 0.2, volume=0.3),   # G
        generate_sine_wave(349, 0.2, volume=0.3),   # F
        generate_sine_wave(294, 0.3, volume=0.35),  # D
    ]
    sound = np.concatenate(tones)
    sound = apply_envelope(sound, attack=0.02, release=0.2)
    save_wav("assets/sounds/game_over.wav", sound)

if __name__ == "__main__":
    print("Generating sound effects for Maya's Veggie Run...")
    print()

    create_jump_sound()
    create_collect_sound()
    create_hit_sound()
    create_love_sound()
    create_game_over_sound()

    print()
    print("SUCCESS! All sound effects generated successfully!")
    print("The sounds are simple synthesized effects.")
    print("Feel free to replace them with better quality sounds later!")
