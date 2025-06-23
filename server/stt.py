from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")

segments, info = model.transcribe(r"C:\Users\ehceirs\Downloads\test_record.ogg")

text = "".join([segment.text for segment in segments])
print(text)