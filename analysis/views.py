from django.shortcuts import render
from .forms import AudioFileForm
from .models import AudioFile
import pickle
import numpy as np
import librosa
import soundfile

# Load trained model
MODEL_PATH = "analysis/modelForPrediction1.sav"
loaded_model = pickle.load(open(MODEL_PATH, 'rb'))

# Function to extract features from an audio file
def extract_feature(file_path, mfcc=True, chroma=True, mel=True):
    with soundfile.SoundFile(file_path) as sound_file:
        X = sound_file.read(dtype="float32")
        sample_rate = sound_file.samplerate
        result = np.array([])

        if mfcc:
            mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T, axis=0)
            result = np.hstack((result, mfccs))
        if chroma:
            stft = np.abs(librosa.stft(X))
            chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T, axis=0)
            result = np.hstack((result, chroma))
        if mel:
            mel = np.mean(librosa.feature.melspectrogram(y=X, sr=sample_rate).T, axis=0)
            result = np.hstack((result, mel))

    return result

# View function for file upload and prediction
def upload_audio(request):
    if request.method == "POST":
        form = AudioFileForm(request.POST, request.FILES)
        if form.is_valid():
            audio_file = form.save()
            file_path = audio_file.file.path
            
            # Extract features and predict emotion
            features = extract_feature(file_path, mfcc=True, chroma=True, mel=True)
            features = features.reshape(1, -1)
            prediction = loaded_model.predict(features)[0]
            probabilities = loaded_model.predict_proba(features)[0]
            emotions = loaded_model.classes_

            emotion_probabilities = {emotions[i]: round(probabilities[i] * 100, 2) for i in range(len(emotions))}

            return render(request, "analysis/result.html", {
                "emotion": prediction,
                "probabilities": emotion_probabilities,
                "audio_url": audio_file.file.url
            })

    else:
        form = AudioFileForm()
    return render(request, "analysis/upload.html", {"form": form})
