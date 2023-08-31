import os
import whisper

def transcribe_wisper(output_directory, path_to_audio_file):
    model = whisper.load_model("base")
    result = model.transcribe(path_to_audio_file, verbose=True)
    with open(os.path.join(output_directory, "transcription.txt"), "w", encoding="utf-8") as txt:
        txt.write(result["text"])
