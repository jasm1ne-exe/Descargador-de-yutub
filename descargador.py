# descargador.py
# Aqui va toda la logica de descarga con yt-dlp y ffmpeg.
# La idea es que despues la interfaz grafica (tkinter) solo llame a estas funciones.

import os
import shutil
import yt_dlp


# carpeta por defecto: la carpeta "Downloads" del usuario
CARPETA_POR_DEFECTO = os.path.join(os.path.expanduser("~"), "Downloads")


def buscar_ffmpeg():
    # primero buscamos si ffmpeg esta en el PATH
    ruta = shutil.which("ffmpeg")
    if ruta != None:
        return os.path.dirname(ruta)
    # si no, probamos la ruta donde lo tengo instalado
    if os.path.exists("C:\\ffmpeg\\bin\\ffmpeg.exe"):
        return "C:\\ffmpeg\\bin"
    return None


def mostrar_progreso(d):
    # yt-dlp llama a esta funcion muchas veces mientras descarga
    # d es un diccionario con informacion del progreso
    if d["status"] == "downloading":
        porcentaje = d.get("_percent_str", "").strip()
        velocidad = d.get("_speed_str", "").strip()
        print("\rDescargando... " + porcentaje + " a " + velocidad + "      ", end="")
    elif d["status"] == "finished":
        print("\nDescarga terminada, procesando con ffmpeg...")


def traducir_error(error):
    # los errores de yt-dlp vienen en ingles y muy largos
    # aqui buscamos palabras clave para dar un mensaje entendible
    texto = str(error)
    t = texto.lower()  # en minusculas para que no importen las mayusculas
    if "unsupported url" in t or "not a valid url" in t:
        return "Ese link no es valido o no es de una pagina compatible."
    if "private video" in t:
        return "El video es privado."
    if "unavailable" in t or "not available" in t:
        return "El video no esta disponible (puede que lo hayan borrado o este bloqueado)."
    if "404" in t:
        return "No se encontro la pagina, revisa el link."
    if "confirm your age" in t:
        return "El video tiene restriccion de edad y pide iniciar sesion."
    if "getaddrinfo" in t or "failed to resolve" in t or "timed out" in t:
        return "No hay conexion a internet o la pagina no responde."
    if "ffmpeg" in t:
        return "Hubo un problema con ffmpeg. Revisa que este instalado."
    # si no es ninguno conocido, devolvemos el error original
    return texto.replace("ERROR: ", "")


def descargar(url, modo="video", carpeta=None, es_playlist=False, calidad_audio="192", funcion_progreso=None):
    # url: el link del video o playlist
    # modo: "audio" (solo mp3), "video" (mp4 con audio) o "solo_video" (mp4 sin audio)
    # carpeta: donde se guarda. Si es None usa Descargas
    # es_playlist: True para bajar toda la playlist, False para solo un video
    # calidad_audio: kbps del mp3 ("128", "192", "320")
    # funcion_progreso: funcion que recibe el progreso (la usaremos en la interfaz)
    #
    # devuelve dos cosas: (True o False, mensaje)
    # ejemplo: ok, mensaje = descargar(...)

    if carpeta == None or carpeta == "":
        carpeta = CARPETA_POR_DEFECTO

    # si la carpeta no existe la creamos
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    if funcion_progreso == None:
        funcion_progreso = mostrar_progreso

    # al solo video le ponemos "(sin audio)" para que no choque con el mp4 normal
    extra = ""
    if modo == "solo_video":
        extra = " (sin audio)"

    # nombre de los archivos que se guardan
    if es_playlist:
        # en playlist se crea una subcarpeta con el nombre de la playlist
        # y los archivos se numeran: 01 - titulo.mp3
        plantilla = os.path.join(carpeta, "%(playlist_title)s", "%(playlist_index)02d - %(title)s" + extra + ".%(ext)s")
    else:
        plantilla = os.path.join(carpeta, "%(title)s" + extra + ".%(ext)s")

    # opciones basicas que se usan siempre
    opciones = {
        "outtmpl": plantilla,
        "noplaylist": not es_playlist,
        "progress_hooks": [funcion_progreso],
        "ignoreerrors": es_playlist,  # en playlist si un video falla, sigue con los demas
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,  # que yt-dlp no imprima su barra, usamos la nuestra
    }

    ruta_ffmpeg = buscar_ffmpeg()
    if ruta_ffmpeg != None:
        opciones["ffmpeg_location"] = ruta_ffmpeg
    else:
        print("OJO: no se encontro ffmpeg, puede que no funcione convertir a mp3 o unir video+audio")

    # opciones segun el modo
    if modo == "audio":
        opciones["format"] = "bestaudio/best"
        # ffmpeg convierte el audio a mp3
        opciones["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": calidad_audio,
        }]
    elif modo == "video":
        # mejor video + mejor audio, y ffmpeg los une en un mp4
        opciones["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
        opciones["merge_output_format"] = "mp4"
    elif modo == "solo_video":
        # solo la imagen, sin sonido
        opciones["format"] = "bestvideo[ext=mp4]/bestvideo"
    else:
        print("Modo no valido: " + str(modo))
        return False, "Modo no valido: " + str(modo)

    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            codigo = ydl.download([url])
        # en playlist los errores no paran la descarga, pero download() devuelve 1 si alguno fallo
        if codigo != 0:
            mensaje = "Se descargo, pero algunos videos fallaron (pueden ser privados o borrados)."
        else:
            mensaje = "Guardado en: " + carpeta
        print("Listo! " + mensaje)
        return True, mensaje
    except Exception as e:
        mensaje = traducir_error(e)
        print("\nError al descargar: " + mensaje)
        return False, mensaje


def obtener_info(url):
    # saca el titulo y si es playlist sin descargar nada
    # sirve para mostrar info en la interfaz antes de descargar
    opciones = {"quiet": True, "extract_flat": True, "no_warnings": True}
    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(url, download=False)
        titulo = info.get("title", "Sin titulo")
        if info.get("_type") == "playlist":
            cantidad = len(info.get("entries", []))
            return {"titulo": titulo, "es_playlist": True, "cantidad": cantidad}
        else:
            return {"titulo": titulo, "es_playlist": False, "cantidad": 1}
    except Exception as e:
        print("No se pudo obtener la info: " + str(e))
        return None
