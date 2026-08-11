import torch
import soundfile as sf
from silero_vad import load_silero_vad, read_audio, get_speech_timestamps
from src.textgrid_allignment import create_split_textgrids, read_transcript, align_speech_text, match_files
from collections import defaultdict
import time

def generate_textgrid(wav_file, txt_file, file_id, output_path):
    vad_model = load_silero_vad()

    wav_path = wav_file
    # Load audio with soundfile (normalized float32 [-1.0, 1.0])
    data, sample_rate = sf.read(wav_path, dtype='float32')

    # Convert to PyTorch tensor
    wav = torch.from_numpy(data)

    #If the audio is stereo, convert to mono
    if wav.ndim > 1:
        wav = wav.mean(dim=1)

    audio_duration = len(data) / float(sample_rate)

    speech_timestamps = get_speech_timestamps(
        wav, 
        vad_model, 
        sampling_rate=sample_rate, 
        return_seconds=True,
        min_silence_duration_ms=700
    )
    ms = 700
    count = 0
    # binary search (retry of 350 ms max)
    while len(speech_timestamps) != 82 and count <= 35:
        
        count += 1
        if len(speech_timestamps) < 82:
            ms -= 10
        else:
            ms += 10
        print(f"retrying Silero VAD. {file_id} # of timestamps {len(speech_timestamps)}. New ms of {ms}")
        speech_timestamps = get_speech_timestamps(
                wav, 
                vad_model, 
                sampling_rate=sample_rate, 
                return_seconds=True,
                min_silence_duration_ms=ms
            )


    # (Example segment list representing (start, end, text, language)):
    lines = read_transcript(txt_file)
    if len(lines) != len(speech_timestamps):
        print(f"Lines do not match between transcript and Silero. Try again with different parameters. Skipping {file_id}...")
        print(f"Transcirpt lines {len(lines)}")
        print(f"Silero lines {len(speech_timestamps)}")
        return
    segments = align_speech_text(speech_timestamps, lines)
    #print(segments)
    create_split_textgrids(output_path, file_id, segments, audio_duration)
    print(f"created {file_id}")

start_time = time.perf_counter()

# BATCH OUTPUT
files = match_files("data/drift_project/(4)Data/(1)First/wavs", "data/drift_project/(4)Data/(1)First/txts")
for file_id, files in files.items():
    output_name = (files[0].name)[:-4] + ".TextGrid"
    generate_textgrid(str(files[0]), str(files[1]), output_name, "data/drift_project/(4)Data/(1)First/wavs")
'''
# INDIVIDUAL OUTPUT
generate_textgrid("data/drift_project/(4)Data/(1)First/wavs/P14_5.2.wav","data/drift_project/(4)Data/(1)First/txts/P14_5.2.txt", "P14_5.2.TextGrid", "data/drift_project/(4)Data/(1)First/wavs")
'''
elapsed_time = time.perf_counter() - start_time
print(f"Execution time: {elapsed_time:.4f} seconds")




