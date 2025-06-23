from naoqi import ALProxy
import time
import sys

def record_audio(robot_ip, port, file_path, duration_s=5):
    """
    Records `duration_s` seconds of audio on Pepper and saves it to `file_p
ath`.
    """
    # Connect to the audio recorder proxy
    recorder = ALProxy("ALAudioRecorder", robot_ip, port)
    try:
        recorder.stopMicrophonesRecording()
    except RuntimeError:
        pass
    # Start recording:
    #  - file_path: where on Pepper to save (must be absolute)
    #  - format: "wav" or "ogg"
    #  - sampleRate: e.g. 16000 Hz
    #  - channels: 4-tuple selecting Peppers mics; (0,0,1,0) uses the third
 mic only
    recorder.startMicrophonesRecording(file_path, "ogg", 16000, (0, 0, 1, 0
))
    print("Recording for {} seconds...".format(duration_s))
    time.sleep(duration_s)

    # Stop and finalize the file
    recorder.stopMicrophonesRecording()
    print("Saved recording to {}".format(file_path))


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: {} <pepper_ip> <output_path_on_pepper> <duration_s>".
format(sys.argv[0]))
        sys.exit(1)

    ip      = sys.argv[1]
    outpath = sys.argv[2]
    dur     = float(sys.argv[3])
    while True:
        record_audio(ip, 9559, outpath, dur)
        import time
        import requests

        start_time = time.time()
        url = "http://1516-192-176-1-79.ngrok-free.app/transcribe"

        files = {
            "audio": (
                "test_record.ogg",
                open("/home/nao/recordings/test_record.ogg", "rb"),
                "audio/ogg"
            )
        }

        try:
            resp = requests.post(url, files=files, timeout=100)
            data = resp.json() 
            print(resp.status_code, resp.json())
            content = data['answer']['content']
            content = str(content)
            tts = ALProxy("ALTextToSpeech", "127.0.0.1", 9559)
            tts.say(content)
        except Exception as e:
            print("Request failed:", e)
        
        end_time = time.time()
        print("elapsed time:", end_time-start_time)
