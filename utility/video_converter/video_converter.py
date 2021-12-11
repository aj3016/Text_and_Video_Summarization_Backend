import moviepy.editor as mp
from pydub import AudioSegment
import os
from google.cloud import speech
import wave
from google.cloud import storage

dir_name = os.path.join(os.getcwd(),'static/Video')
filepath =  os.path.join(dir_name + '/middle/')
output_filepath =  os.path.join(dir_name + '/output/')

def frame_rate_channel(audio_file_name):
    with wave.open(audio_file_name, "rb") as wave_file:
        frame_rate = wave_file.getframerate()
        channels = wave_file.getnchannels()
        return frame_rate,channels

def stereo_to_mono(audio_file_name):
    sound = AudioSegment.from_wav(audio_file_name)
    sound = sound.set_channels(1)
    sound.export(audio_file_name, format="wav")


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)


def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.delete()


def google_transcribe(audio_file_name):
    
    file_name = filepath + audio_file_name
    # mp3_to_wav(file_name)

    # The name of the audio file to transcribe
    frame_rate, channels = frame_rate_channel(file_name)
    if channels > 1:
        stereo_to_mono(file_name)
    
    bucket_name = 's-2-t'
    source_file_name = filepath + audio_file_name
    destination_blob_name = audio_file_name
    
    upload_blob(bucket_name, source_file_name, destination_blob_name)
    
    gcs_uri = 'gs://s-2-t/' + audio_file_name
    transcript = ''
    
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(uri=gcs_uri)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=frame_rate,
        language_code='en-US',
        enable_automatic_punctuation=True,
    )

    # Detects speech in the audio file
    operation = client.long_running_recognize(request={"config": config, "audio": audio})
    response = operation.result(timeout=10000)

    for result in response.results:
        transcript += result.alternatives[0].transcript
    
    delete_blob(bucket_name, destination_blob_name)
    return transcript

def write_transcripts(transcript_filename,transcript):
    f= open(output_filepath + transcript_filename,"w+")
    f.write(transcript)
    f.close() 

def video_convertor(filename):
    clip = mp.VideoFileClip(dir_name + r'/input/' + filename)
    clip.audio.write_audiofile(dir_name + r'\middle\result.wav')
    clip.close()
    for audio_file_name in os.listdir(filepath):
        transcript = google_transcribe(audio_file_name)
        transcript_filename = audio_file_name.split('.')[0] + '.txt'
        write_transcripts(transcript_filename,transcript)
