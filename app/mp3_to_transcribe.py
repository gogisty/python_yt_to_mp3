import os
import whisper
from transformers import pipeline

def summarize_text(text):
    summarizer = pipeline("summarization")
    summary_text = summarizer(text, min_length=5, max_length=200)[0]['summary_text']
    return summary_text

def transcribe_whisper(output_directory, path_to_audio_file, summary_format):
    model = whisper.load_model("base")
    result = model.transcribe(path_to_audio_file, verbose=True)
    transcription_text = result["text"]

    # Summarize the transcription
    summary_text = summarize_text(transcription_text)

    # Save the transcription
    with open(os.path.join(output_directory, "transcription.txt"), "w", encoding="utf-8") as txt:
        txt.write(transcription_text)

    # Save the summary
    if summary_format == "txt":
        with open(os.path.join(output_directory, "summary.txt"), "w", encoding="utf-8") as txt:
            txt.write(summary_text)
    elif summary_format == "json":
        import json
        with open(os.path.join(output_directory, "summary.json"), "w", encoding="utf-8") as json_file:
            json.dump({"summary": summary_text}, json_file)
    else:
        print("Unsupported summary format. Please choose 'txt' or 'json'.")