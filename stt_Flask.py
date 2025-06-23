from flask import Flask, request, jsonify
from faster_whisper import WhisperModel
import os
import tempfile
from huggingface_hub import InferenceApi,InferenceClient
import time


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
    t11 = time.time()
    print(f"Transcribing file from {request.remote_addr}")
    f = request.files.get("audio")
    if not f or not f.mimetype.startswith("audio/"):
        return jsonify({"error": "no valid audio file"}), 400
    t12 = time.time()
    # time to recieve file
    # create a unique temp file
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        tmp_path = tmp.name
        f.save(tmp_path)

    try:
        t21=time.time()
        segments, info = model.transcribe(tmp_path)
        text = "".join(seg.text for seg in segments)
        prompt = (
                f"*PRE PROMPT HERE*\n Prompt:\n{text}\n\n:")
        t22=time.time() # time for transcription
        print("time for STT transcription: ", t22-t21)
        t31=time.time()
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
        t32 = time.time() #time for llm answer
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
    print(answer)
    return jsonify({"answer": answer,"times": f'{t12-t11},{t22-t21},{t32-t31}'})

if __name__ == "__main__":
    # listen on all interfaces
    app.run(host="0.0.0.0", port=5000, debug=True)