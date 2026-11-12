# Descargador de YT

Descargador de videos y audio de YouTube hecho en Python con **yt-dlp** y **ffmpeg**. Para uso personal :)

Tiene una ventana hecha con **tkinter** y también un menú para usarlo desde la consola.

## Funciones
- Descargar solo audio (mp3, calidad 128 / 192 / 320 kbps)
- Descargar video con audio (mp4)
- Descargar solo video, sin audio (mp4)
- Descargar playlists completas (cada una en su propia carpeta, con los archivos numerados)
- Elegir en qué carpeta guardar (por defecto, Descargas) y abrirla con un botón
- Recuerda la última carpeta que usaste
- Barra de progreso con velocidad, "Video 3 de 10" en playlists y "Parte 1 de 2" en video con audio
- Mensajes de error en español (video privado, no disponible, sin internet, link inválido...)

## Requisitos
- Python 3
- yt-dlp: `pip install yt-dlp`
- [ffmpeg](https://ffmpeg.org/download.html) instalado (en el PATH o en `C:\ffmpeg\bin`)
- (Recomendado) [deno](https://deno.com/) y yt-dlp-ejs: yt-dlp los usa para resolver los retos de YouTube
  - `winget install DenoLand.Deno`
  - `pip install yt-dlp-ejs`

## Uso

### Con la ventana
```
python interfaz.py
```
1. Pega el link y dale a **Ver info** para ver el título y si es una playlist.
2. Elige qué descargar y, si es audio, la calidad.
3. Elige la carpeta con **Examinar...**
4. Dale a **DESCARGAR**.

### Desde la consola
```
python main.py
```

## Crear el .exe
Para tener el programa en un solo archivo y abrirlo con doble clic:
```
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name "Descargador de YT" --collect-all yt_dlp_ejs --noconfirm interfaz.py
```
El .exe queda en la carpeta `dist`. Igual necesita ffmpeg (y deno, recomendado) instalados en la computadora.

## Archivos
- `descargador.py`: la lógica de descarga (yt-dlp + ffmpeg)
- `interfaz.py`: la ventana con tkinter
- `main.py`: el menú de consola
