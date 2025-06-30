from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel, BatchedInferencePipeline
import os
import tempfile
from huggingface_hub import InferenceApi,InferenceClient
import time
import io
import uvicorn
import torch

app = FastAPI(title="speech_to_text")
CUDA=torch.cuda.is_available()
device= "cuda" if CUDA else "cpu"
model = WhisperModel("tiny", device=device, compute_type="int8")
batched_model = BatchedInferencePipeline(model=model)

#inference sample
HF_TOKEN = "YOUR_KEY"
client = InferenceClient(
    provider="hf-inference",
    api_key=HF_TOKEN,
)

ID = 0
history = {}
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
    segments, info = batched_model.transcribe(buf,batch_size=16)
    text = "".join(seg.text for seg in segments)
    prompt = (
            f"*PRE PROMPT HERE*\n Prompt:\n{text}\n\n:")
    t22=time.time() # time for transcription
    print("time for STT transcription: ", t22-t21)
    t31=time.time()

    if ID==0:

        completion = client.chat.completions.create(
        model="google/gemma-3-27b-it",
        messages=[
            {
                "role": "user",
                "content": f"{pre_prompt+prompt}"
            }
        ],
        )
    else:
        completion = client.chat.completions.create(
        model="google/gemma-3-27b-it",
        messages=[
            {
                "role": "user",
                "content": f"Here is some history of your conversation:{history[ID-1]}. Do not repeat yourself too much. Remember to answer the prompt short and consise. Remember You are acting as 'Pepper' NOT Gemma. {prompt}"
            }
        ],
        )
    answer= completion.choices[0].message
    history[ID]=f"prompt: {text}, answer:{answer}"
    ID+=1
    t32 = time.time() #time for llm answer
    print(answer)
    return JSONResponse({
        "answer": answer,
        "text": text,
        "times": [round(t12-t11,10), round(t22-t21,3), round(t32-t31,3)]
    })

if __name__ == "__main__":
    # listen on all interfaces
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
