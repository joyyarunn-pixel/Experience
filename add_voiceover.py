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
DURATION = 30.0

# (start seconds, text)
CUES = [
    (0.3, "Why is a plus b, squared, equal to this?"),
    (4.3, "A square with side a plus b has area a plus b, squared."),
    (8.3, "Now, cut it into four pieces."),
    (10.6, "The top left is a by a. That's a squared."),
    (13.6, "The bottom right is b by b. That's b squared."),
    (16.6, "And two rectangles, each a by b. That's a b, twice."),
    (21.5, "Add up the pieces:"),
    (23.3, "a squared, plus two a b, plus b squared!"),
    (26.9, "Check: nine plus twelve plus four is twenty five!"),
]


def synth(voice, text, path, length_scale):
    with wave.open(str(path), "wb") as wf:
        voice.synthesize_wav(text, wf, syn_config=SynthesisConfig(length_scale=length_scale))
    with wave.open(str(path)) as wf:
        return wf.getnframes() / wf.getframerate()


def main(model):
    voice = PiperVoice.load(model)
    tmp = Path(tempfile.mkdtemp())
    clips = []
    for i, (start, text) in enumerate(CUES):
        end = CUES[i + 1][0] if i + 1 < len(CUES) else DURATION
        window = end - start - 0.15
        path = tmp / f"cue{i}.wav"
        scale = 1.0
        length = synth(voice, text, path, scale)
        while length > window and scale > 0.85:
            scale -= 0.05
            length = synth(voice, text, path, scale)
        if length > window:
            sys.exit(f"cue {i} is {length:.2f}s, window is {window:.2f}s: {text!r}")
        print(f"{start:5.1f}s  {length:4.2f}s/{window:4.2f}s  x{scale:.2f}  {text}")
        clips.append((start, path))

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
