from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel
import os
import tempfile
from huggingface_hub import InferenceApi,InferenceClient
import time
import io
import uvicorn

app = FastAPI(title="speech_to_text")
model = WhisperModel("small", device="cpu", compute_type="int8")

#inference sample
HF_TOKEN = "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"
client = InferenceClient(
    provider="hf-inference",
    api_key=HF_TOKEN,
)


@app.post("/transcribe")

async def transcribe(request: Request, audio: UploadFile):
    print(f"Transcribing file")

    if not audio.content_type.startswith("audio/"):
        raise HTTPException(400, "Not an audio file")
    t11 = time.time()
    audio_bytes = await audio.read()
    buf = io.BytesIO(audio_bytes)
    t12 = time.time()


    t21=time.time()
    segments, info = model.transcribe(buf)
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
    print(answer)
    return JSONResponse({
        "answer": answer,
        "times": [round(t12-t11,3), round(t22-t21,3), round(t32-t31,3)]
    })
if __name__ == "__main__":
    # listen on all interfaces
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
