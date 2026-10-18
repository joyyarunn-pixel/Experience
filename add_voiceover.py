"""Add a spoken narration to binomial_square.mp4 using Piper text-to-speech.

Usage: python3 add_voiceover.py path/to/voice.onnx
  ->  writes binomial_square_narrated.mp4

Each cue starts at a time matching the animation in make_video.py and must
finish before the next cue begins; lines that run long are sped up slightly.
"""
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

from piper import PiperVoice, SynthesisConfig

VIDEO = "binomial_square.mp4"
OUT = "binomial_square_narrated.mp4"
DURATION = 80.0

# (start seconds, text)
CUES = [
    (0.5, "Here's a famous identity: a plus b, squared, equals a squared, "
          "plus two a b, plus b squared."),
    (7.3, "But why is it true? Let's see it with a picture."),
    (11.5, "Start with a square. Each side is made of two parts: "
           "a length a, and a length b."),
    (18.0, "So each side is a plus b, and the area of the whole square "
           "is a plus b, squared."),
    (24.0, "Now, let's cut the square along those marks, into four pieces."),
    (30.5, "The top left piece is a by a. Its area is a squared."),
    (38.5, "The bottom right piece is b by b. Its area is b squared."),
    (46.5, "The top right piece is b wide and a tall, so its area is a times b."),
    (52.5, "And the bottom left piece is also a by b. "
           "So the a b rectangle appears twice."),
    (59.0, "The four pieces fill the whole square. Adding them up: "
           "a squared, plus a b, plus a b, plus b squared."),
    (66.5, "The two a b's combine into two a b. And that's the identity!"),
    (71.5, "Let's check: if a is three and b is two, five squared is twenty five."),
    (76.0, "And nine plus six plus six plus four? Twenty five!"),
]


def synth(voice, text, path, length_scale):
    with wave.open(str(path), "wb") as wf:
        voice.synthesize_wav(text, wf, syn_config=SynthesisConfig(length_scale=length_scale))
    with wave.open(str(path)) as wf:
        return wf.getnframes() / wf.getframerate()


def main(model):
    voice = PiperVoice.load(model)
    tmp = Path(tempfile.mkdtemp())
    clips, too_long = [], False
    for i, (start, text) in enumerate(CUES):
        end = CUES[i + 1][0] if i + 1 < len(CUES) else DURATION
        window = end - start - 0.15
        path = tmp / f"cue{i}.wav"
        scale = 1.0
        length = synth(voice, text, path, scale)
        while length > window and scale > 0.85:
            scale -= 0.05
            length = synth(voice, text, path, scale)
        flag = "  <-- TOO LONG" if length > window else ""
        too_long = too_long or bool(flag)
        print(f"{start:5.1f}s  {length:4.2f}s/{window:4.2f}s  x{scale:.2f}  {text}{flag}")
        clips.append((start, path))
    if too_long:
        sys.exit("some cues overrun their window; shorten them or move cue times")

    inputs, filters = ["-i", VIDEO], []
    for n, (start, path) in enumerate(clips, start=1):
        inputs += ["-i", str(path)]
        ms = int(start * 1000)
        filters.append(f"[{n}:a]adelay={ms}|{ms}[a{n}]")
    mix = "".join(f"[a{n}]" for n in range(1, len(clips) + 1))
    filters.append(f"{mix}amix=inputs={len(clips)}:normalize=0,volume=0.8,apad[aout]")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filters),
         "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
         "-t", str(DURATION), OUT],
        check=True,
    )
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main(sys.argv[1])
