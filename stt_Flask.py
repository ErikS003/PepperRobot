from flask import Flask, request, jsonify
from faster_whisper import WhisperModel
import os
import tempfile
from huggingface_hub import InferenceApi,InferenceClient

app = Flask("speech_to_text")
model = WhisperModel("base", device="cpu", compute_type="int8")



#inference sample
HF_TOKEN = "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"
client = InferenceClient(
    provider="hf-inference",
    api_key=HF_TOKEN,
)


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
        prompt = (
                f"*PRE PROMPT HERE*\n Prompt:\n{text}\n\n:")
        
        completion = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=[
            {
                "role": "user",
                "content": f"{prompt}"
            }
        ],
        )
        answer= completion.choices[0].message
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
    print(answer)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    # listen on all interfaces
    app.run(host="0.0.0.0", port=5000, debug=True)