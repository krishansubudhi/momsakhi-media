"""Gemini TTS over the Gemini API (urllib only). The key never leaves this process."""
import base64
import json
import os
import urllib.error
import urllib.request
import wave

MODEL = "gemini-2.5-flash-preview-tts"
BASE = "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % MODEL


def key() -> str:
    return os.environ["GEMINI_API_KEY"]  # only the voiced variant needs it; never commit a key


def synth_once(text: str, voice: str, out_wav: str) -> None:
    k = key()
    body = json.dumps({
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {"responseModalities": ["AUDIO"],
                             "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}},
    }).encode()
    last = ""
    for url, hdr in [(BASE, {"x-goog-api-key": k})]:
        req = urllib.request.Request(url, body, {"Content-Type": "application/json", **hdr})
        try:
            d = json.load(urllib.request.urlopen(req, timeout=180))
        except urllib.error.HTTPError as e:
            last = "%s %s" % (e.code, e.read()[:400].decode().replace(k, "<key>"))
            continue
        cand = d["candidates"][0]
        if "content" not in cand:
            last = "no audio, finishReason=%s" % cand.get("finishReason")
            raise RuntimeError(last)
        pcm = base64.b64decode(cand["content"]["parts"][0]["inlineData"]["data"])
        with wave.open(out_wav, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(24000)
            w.writeframes(pcm)
        return
    raise RuntimeError("Gemini TTS rejected: " + last)


def synth(text: str, voice: str, out_wav: str, tries: int = 1) -> None:
    """The key's auth is intermittent (401 now and then), so a rejected call is retried."""
    import time
    for i in range(tries):
        try:
            return synth_once(text, voice, out_wav)
        except RuntimeError as e:
            if "finishReason" in str(e) or i == tries - 1:
                raise
            time.sleep(2 + i)


if __name__ == "__main__":
    synth("Say warmly and conversationally: hello there, friend.", "Kore", "probe.wav")
    print("ok")
