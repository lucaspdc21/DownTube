import os
import sys
import subprocess
from pytubefix import YouTube
FFMPEG = 'ffmpeg'
def list_resolutions(yt):
    # List all available video resolutions and allows the user to choose one.
    streams = yt.streams.filter(progressive=False, only_video=True).order_by('resolution').desc()
    unique_resolutions = []
    # Use a set to track seen resolutions
    seen = set()

    for stream in streams:
        # Create a label for the stream (resolution, mime_type, itag)
        label = f"{stream.resolution} - {stream.mime_type} - itag={stream.itag}"
        if stream.resolution not in seen:
            unique_resolutions.append((label, stream.itag))
            seen.add(stream.resolution)
    return unique_resolutions

def download_selected_stream(yt, itag, output_dir="downloads"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"🔽 Baixando vídeo: {yt.title}...")

    # Download vídeo (apenas vídeo)
    video_stream = yt.streams.get_by_itag(itag)
    video_path = os.path.join(output_dir, "video.mp4")
    video_stream.download(output_path=output_dir, filename="video.mp4")

    # Baixar melhor áudio disponível (sem itag fixo)
    print("🔊 Baixando áudio de melhor qualidade...")
    audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
    audio_path = os.path.join(output_dir, "audio.mp4")
    audio_stream.download(output_path=output_dir, filename="audio.mp4")

    # Saída final
    safe_title = yt.title.replace(" ", "_").replace("/", "_")
    output_path = os.path.join(output_dir, f"{safe_title}_final.mp4")

    # Combinar usando ffmpeg
    print("🎬 Combinando vídeo e áudio com ffmpeg...")
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

    # Remover arquivos temporários
    #os.remove(video_path)
    #os.remove(audio_path)
    print(f"✅ Download finalizado: {output_path}")

def main():
    if len(sys.argv) < 2:
        print("Comando correto para a execução: python main.py <URL do vídeo>")
        return

    url = sys.argv[1]

    try:
        # Create a YouTube object with the URL
        yt = YouTube(url)
    except Exception as e:
        print(f"Erro ao carregar o vídeo: {e}")
        return

    print(f"\nTítulo: {yt.title}")
    print(f"Duração: {yt.length // 60}:{yt.length % 60:02d}\n")

    resolutions = list_resolutions(yt)
    if not resolutions:
        print("Nenhuma resolução disponível para download.")
        return

    print("Qualidades disponíveis:")
    for i, (desc, _) in enumerate(resolutions):
        print(f"{i + 1}. {desc}")

    choice = input("\nDigite o número da qualidade desejada: ")

    try:
        index = int(choice) - 1
        if index < 0 or index >= len(resolutions):
            raise ValueError
        itag = resolutions[index][1]
        download_selected_stream(yt, itag)
    except ValueError:
        print("Escolha inválida.")

if __name__ == "__main__":
    main()
