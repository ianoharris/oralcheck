"""
Word-level timing for a voiceover whose script is already known.

The TTS returns audio only, so captions that light up word by word need the
timing recovered from the audio. faster-whisper transcribes with word
timestamps (local, free, a few seconds on CPU), and the heard words are then
matched back onto the script with difflib. Display always uses the script's
own words, so "60,480" or "89%" keep their exact spelling whatever the
transcription made of them.

Any script word the match misses gets a time interpolated between its matched
neighbours, weighted by length. If transcription is unavailable entirely, every
word is interpolated across its beat's speech window, which is coarser but
still keeps captions inside the right sentence.
"""
from __future__ import annotations

import difflib
import logging
import re

log = logging.getLogger("oralcheck.align")

_MODEL = None
MODEL_NAME = "base.en"


def _model():
    global _MODEL
    if _MODEL is None:
        from faster_whisper import WhisperModel
        _MODEL = WhisperModel(MODEL_NAME, device="cpu", compute_type="int8")
    return _MODEL


def norm(word: str) -> str:
    return re.sub(r"[^a-z0-9]", "", word.lower())


def _heard(audio_path: str) -> list[tuple[float, float, str]]:
    try:
        segments, _ = _model().transcribe(audio_path, word_timestamps=True, beam_size=1,
                                          vad_filter=False, language="en")
        return [(w.start, w.end, norm(w.word)) for s in segments for w in (s.words or [])]
    except Exception as exc:  # noqa: BLE001
        log.warning("Word alignment unavailable (%s); interpolating caption timing.", exc)
        return []


def _weight(word: str) -> float:
    return len(norm(word)) + 2.0


def _fill(words: list[str], times: list, start: float, end: float) -> list[dict]:
    """Interpolate any missing word times between known anchors."""
    n = len(words)
    out = [None] * n
    i = 0
    while i < n:
        if times[i] is not None:
            out[i] = times[i]
            i += 1
            continue
        j = i
        while j < n and times[j] is None:
            j += 1
        left = out[i - 1][1] if i > 0 else start
        right = times[j][0] if j < n else end
        right = max(right, left + 0.05)
        weights = [_weight(w) for w in words[i:j]]
        total = sum(weights)
        t = left
        for k, wt in enumerate(weights):
            dur = (right - left) * wt / total
            out[i + k] = (t, t + dur)
            t += dur
        i = j
    result, last = [], start
    for w, (a, b) in zip(words, out):
        a = max(a, last)
        b = max(b, a + 0.04)
        result.append({"text": w, "start": round(a, 3), "end": round(b, 3)})
        last = a
    return result


def align(audio_path: str, windows: list[tuple[float, float, str]]) -> list[list[dict]]:
    """Per-beat word timings.

    windows: one (speech_start, speech_end, script_text) per beat, in seconds
             on the full voice track.
    Returns, per beat, [{"text", "start", "end"}] for every whitespace word of
    that beat's script.
    """
    heard = _heard(audio_path)
    result = []
    for start, end, text in windows:
        words = text.split()
        times = [None] * len(words)
        local = [h for h in heard if start - 0.2 <= h[0] < end + 0.1]
        if local and words:
            matcher = difflib.SequenceMatcher(a=[norm(w) for w in words],
                                              b=[h[2] for h in local], autojunk=False)
            for block in matcher.get_matching_blocks():
                for k in range(block.size):
                    h = local[block.b + k]
                    times[block.a + k] = (h[0], h[1])
        result.append(_fill(words, times, start, end))
    return result
