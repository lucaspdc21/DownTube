import os
import subprocess
from pytubefix import YouTube

FFMPEG = 'ffmpeg'  # ou caminho completo para seu ffmpeg, ex: 'resources/ffmpeg'

def baixar_video_alta_qualidade(url, pasta_saida="downloads"):
    yt = YouTube(url)
    print(f"Título: {yt.title}")

    video_stream = yt.streams.filter(only_video=True, file_extension="mp4").order_by("resolution").desc().first()
    audio_stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()

    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)

    video_path = os.path.join(pasta_saida, "video.mp4")
    audio_path = os.path.join(pasta_saida, "audio.mp4")
    output_path = os.path.join(pasta_saida, f"{yt.title}.mp4".replace("/", "_"))

    print("Baixando vídeo (sem áudio)...")
    video_stream.download(output_path=pasta_saida, filename="video.mp4")

    print("Baixando áudio...")
    audio_stream.download(output_path=pasta_saida, filename="audio.mp4")

    print("Combinando vídeo e áudio com ffmpeg...")
    comando = [
        FFMPEG, '-y',
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-strict', 'experimental',
        output_path
    ]
    subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    os.remove(video_path)
    os.remove(audio_path)

    print(f"Download finalizado: {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python main.py <URL>")
    else:
        baixar_video_alta_qualidade(sys.argv[1])
