import speechbrain as sb
from speechbrain.dataio.dataio import read_audio
from IPython.display import Audio
from ipywebrtc import AudioRecorder, CameraStream
from IPython.display import Audio
from speechbrain.pretrained import EncoderDecoderASR
import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv
  

homePath = '/Users/petr/Documents/fun_stuff/wordsmith/wordsmith/data/user_audio/'

# Sampling frequency
freq = 16000 # NEEDS TO BE THIS AS THIS IS WHAT THE MODEL WAS TRAINED ON
  
# Recording duration
duration = 5

def recognise_word():
    # Start recorder with the given values 
    # of duration and sample frequency
    recording = sd.rec(int(duration * freq), 
                    samplerate=freq, channels=1)
    
    # Record audio for the given number of seconds
    sd.wait()
    
    # This will convert the NumPy array to an audio
    # file with the given sampling frequency
    # write(homePath+"latest_recording.wav", freq, recording)
    
    # Convert the NumPy array to audio file
    wv.write(homePath+"latest_recording.wav", recording, freq, sampwidth=2)


    asr_model = EncoderDecoderASR.from_hparams(source="speechbrain/asr-crdnn-rnnlm-librispeech", savedir="data/pretrained_models/asr-crdnn-rnnlm-librispeech")
    heard_word = asr_model.transcribe_file(homePath+'latest_recording.wav')
    return heard_word
