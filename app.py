import streamlit as st
from pytube import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip
import os

# Función para descargar video
def download_video(url, itag):
    try:
        yt = YouTube(url)
        video_stream = yt.streams.get_by_itag(itag)

        if video_stream is None:
            return None, "Error: No se encontró la stream de video con el itag especificado."

        # Ruta donde se guardará el archivo descargado
        download_path = os.path.join(os.getcwd(), 'downloads')
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        # Descargar el archivo de video
        video_filename = f"{yt.title}_video.mp4"
        video_file = os.path.join(download_path, video_filename)
        video_stream.download(output_path=download_path, filename=video_filename)

        # Verificar que el archivo se descargó correctamente
        if os.path.exists(video_file):
            return video_file, None
        else:
            return None, "Error: El archivo de video no se descargó correctamente."
    except Exception as e:
        return None, str(e)

# Función para descargar audio
def download_audio(url, itag):
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.get_by_itag(itag)

        if audio_stream is None:
            return None, "Error: No se encontró la stream de audio con el itag especificado."

        # Ruta donde se guardará el archivo descargado
        download_path = os.path.join(os.getcwd(), 'downloads')
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        # Descargar el archivo de audio
        audio_filename = f"{yt.title}_audio.mp4"
        audio_file = os.path.join(download_path, audio_filename)
        audio_stream.download(output_path=download_path, filename=audio_filename)

        # Verificar que el archivo se descargó correctamente
        if os.path.exists(audio_file):
            return audio_file, None
        else:
            return None, "Error: El archivo de audio no se descargó correctamente."
    except Exception as e:
        return None, str(e)

# Función para combinar video y audio usando moviepy
def combine_video_audio(video_file, audio_file, output_filename):
    try:
        video_clip = VideoFileClip(video_file)
        audio_clip = AudioFileClip(audio_file)
        final_clip = video_clip.set_audio(audio_clip)

        # Ruta donde se guardará el archivo combinado
        download_path = os.path.join(os.getcwd(), 'downloads')
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        output_file = os.path.join(download_path, output_filename)
        final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')

        # Eliminar archivos temporales de video y audio
        os.remove(video_file)
        os.remove(audio_file)

        return output_file, None
    except Exception as e:
        return None, str(e)

# Configuración de la aplicación Streamlit
st.title('YouTube Video Downloader')

url = st.text_input('Enter YouTube video URL')

if url:
    try:
        yt = YouTube(url)
        st.write(f"**Title:** {yt.title}")
        st.write(f"**Author:** {yt.author}")

        # Obtener todas las streams de video y audio
        video_streams = yt.streams.filter(file_extension='mp4', only_video=True)
        audio_streams = yt.streams.filter(file_extension='mp4', only_audio=True)

        # Crear selectbox para video y audio
        video_options = [f"{stream.resolution} - {stream.fps}fps - {(stream.filesize / (1024 * 1024)):.2f}MB" for stream in video_streams]
        audio_options = [f"{stream.abr} - {(stream.filesize / (1024 * 1024)):.2f}MB" for stream in audio_streams]

        video_itag = st.selectbox('Select Video Stream', options=video_options, format_func=lambda x: x.split(' ')[0])
        audio_itag = st.selectbox('Select Audio Stream', options=audio_options, format_func=lambda x: x.split(' ')[0])

        if st.button('Download'):
            video_itag_selected = video_streams[video_options.index(video_itag)].itag
            audio_itag_selected = audio_streams[audio_options.index(audio_itag)].itag

            with st.spinner('Downloading video...'):
                video_file, error_video = download_video(url, video_itag_selected)
                if error_video:
                    st.error(f"Error downloading video: {error_video}")
                    st.stop()  # Detener aquí si hay un error en la descarga del video

            with st.spinner('Downloading audio...'):
                if not error_video:  # Continuar solo si no hubo error al descargar el video
                    audio_file, error_audio = download_audio(url, audio_itag_selected)
                    if error_audio:
                        st.error(f"Error downloading audio: {error_audio}")
                        st.stop()  # Detener aquí si hay un error en la descarga del audio

            if not error_video and not error_audio:  # Continuar solo si no hubo errores en la descarga
                with st.spinner('Combining video and audio...'):
                    output_file, error_combine = combine_video_audio(video_file, audio_file, f"{yt.title}.mp4")
                    if error_combine:
                        st.error(f"Error combining video and audio: {error_combine}")
                    else:
                        st.success(f'Download completed! File saved at: {output_file}')
                        st.video(output_file)

    except Exception as e:
        st.error(f"Error: {e}")
