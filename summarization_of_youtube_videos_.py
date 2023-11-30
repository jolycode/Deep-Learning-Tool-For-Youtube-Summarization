# -*- coding: utf-8 -*-
"""Summarization of YouTube videos .ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VKgW35o-lv33gufoBoXzeg9h6u07CIKY
"""

!pip install pydub
!pip install SpeechRecognition
!pip install pytube

"""Youtube section:"""

from pytube import YouTube

# Replace 'VIDEO_URL' with the actual URL of the YouTube video
video_url = 'https://www.youtube.com/watch?v=GwT6gGMRr9s&ab_channel=FryingPan'
youtube = YouTube(video_url)
video_stream = youtube.streams.filter(only_audio=True).first()
downloaded_file_path = video_stream.download('/content/videos')

import os

# Get the name of the file
downloaded_file_name = os.path.basename(downloaded_file_path)

# Specify the new filename (without extension)
new_filename = 'video.mp4'

# Download the video and rename it
downloaded_file_path = video_stream.download(output_path='/content/videos', filename=new_filename)

from pydub import AudioSegment

video_path = "/content/videos/video.mp4"
audio = AudioSegment.from_file(video_path, format="mp4")
audio.export("/content/videos/video.wav", format="wav")

!pip install SpeechRecognition pydub

import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence

# Initialize recognizer class (for recognizing the speech)
r = sr.Recognizer()

def transcribe_audio(file_path):
    # load audio to pydub
    audio = AudioSegment.from_wav(file_path)
    # split audio sound where silence is 700 miliseconds or more and get chunks
    chunks = split_on_silence(audio,
        # experiment with this value for your target audio file
        min_silence_len = 500,
        # adjust this per requirement
        silence_thresh = audio.dBFS-14,
        # keep the silence for 1 second, adjustable as well
        keep_silence=500,
    )
    text = ''
    for i, chunk in enumerate(chunks):
        # Process each chunk
        try:
            # using google speech recognition
            print(f"Processing chunk {i+1}/{len(chunks)}")
            # create a new file "chunk_i.wav" to save that chunk
            chunk.export("./chunk{0}.wav".format(i), bitrate ='192k', format ="wav")
            # recognize the chunk
            with sr.AudioFile("./chunk{0}.wav".format(i)) as source:
                audio_listened = r.record(source)
                # try converting it to text
                chunk_text = r.recognize_google(audio_listened)
                text += ' ' + chunk_text
        except sr.UnknownValueError as e:
            print("Error:", str(e))
        except Exception as e:
            print("Error:", str(e))
    return text

print(transcribe_audio('/content/videos/video.wav'))

# Save the transcribed text to a .txt file
with open('transcribed_text.txt', 'w') as f:
    f.write(transcribe_audio('/content/videos/video.wav'))

"""Summarization section:"""

!pip install transformers

from transformers import BartTokenizer, BartForConditionalGeneration

tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-xsum')
model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-xsum')

with open('/content/transcribed_text.txt', 'r') as file:
    text = file.read()

inputs = tokenizer([text], max_length=2048, return_tensors='pt')
summary_ids = model.generate(inputs['input_ids'], num_beams=4, max_length=100, early_stopping=True)
summary = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summary_ids]

print(text)

print(summary)