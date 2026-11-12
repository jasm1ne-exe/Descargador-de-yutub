# Descargador de YT

Descargador de videos y audio de YouTube hecho en Python con **yt-dlp** y **ffmpeg**. Para uso personal :)

## Funciones
- Descargar solo audio (mp3, calidad 128 / 192 / 320 kbps)
- Descargar video con audio (mp4)
- Descargar solo video, sin audio (mp4)
- Descargar playlists completas (cada una en su propia carpeta, con los archivos numerados)
- Elegir en qué carpeta guardar (por defecto, Descargas)

Próximamente: interfaz gráfica con tkinter.

## Requisitos
- Python 3
- yt-dlp: `pip install yt-dlp`
- [ffmpeg](https://ffmpeg.org/download.html) instalado (en el PATH o en `C:\ffmpeg\bin`)

## Uso
```
python main.py
```
