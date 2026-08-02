import torch
import soundfile as sf
import wave
from silero_vad import load_silero_vad, read_audio, get_speech_timestamps
from src.textgrid_allignment import create_split_textgrids, read_transcript, align_speech_text

vad_model = load_silero_vad()

wav_path = "data/test/test_P01/P01_first.wav"

# Load audio with soundfile (normalized float32 [-1.0, 1.0])
data, sample_rate = sf.read(wav_path, dtype='float32')

# Convert to PyTorch tensor
wav = torch.from_numpy(data)

# 3. If the audio is stereo, convert to mono
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


# (Example segment list representing (start, end, text, language)):
print(len(speech_timestamps))
lines = read_transcript("data/test/test_P01_txts/P01_4.25.txt")
print(len(lines))

segments = align_speech_text(speech_timestamps, lines)

#print(segments)


create_split_textgrids("P01_first", segments, audio_duration)
