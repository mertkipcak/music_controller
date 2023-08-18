import subprocess
import os


def set_volume(level: int):
    if 0 <= level <= 100:
        os.system(f"osascript -e 'set volume output volume {level} --100%'")
    else:
        print("Volume level must be between 0 and 100.")


def get_volume():
    volume = subprocess.getoutput("osascript -e 'output volume of (get volume settings)'")
    return int(volume)


def toggle_play_pause_spotify():
    os.system("osascript -e 'tell application \"Spotify\" to playpause'")


def next_track_spotify():
    os.system("osascript -e 'tell application \"Spotify\" to next track'")


def previous_track_spotify():
    os.system("osascript -e 'tell application \"Spotify\" to previous track'")
