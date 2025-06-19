from flask import Flask, request, jsonify
from faster_whisper import WhisperModel
import os
import tempfile


app = Flask("speech_to_text")
model = WhisperModel("base", device="cpu", compute_type="int8")



@app.route("/transcribe", methods=["POST"])


def transcribe():
    print(f"Transcribing file from {request.remote_addr}")
    f = request.files.get("audio")
    if not f or not f.mimetype.startswith("audio/"):
        return jsonify({"error": "no valid audio file"}), 400

    # create a unique temp file
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        tmp_path = tmp.name
        f.save(tmp_path)

    try:
        segments, info = model.transcribe(tmp_path)
        text = "".join(seg.text for seg in segments)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    return jsonify({"text": text})


if __name__ == "__main__":
    # listen on all interfaces
    app.run(host="0.0.0.0", port=5000)
