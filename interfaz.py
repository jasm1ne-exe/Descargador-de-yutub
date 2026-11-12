# interfaz.py
# Ventana del descargador hecha con tkinter
# Usa las funciones de descargador.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from descargador import obtener_info, descargar, CARPETA_POR_DEFECTO


# Aqui el hilo de la descarga va dejando como va todo.
# La ventana lo revisa cada rato con revisar_progreso().
# (tkinter se puede trabar si lo tocas desde otro hilo, por eso lo hacemos asi)
estado = {
    "descargando": False,
    "porcentaje": 0,
    "texto": "",
    "terminado": False,
    "resultado": False,
    "mensaje": "",
    "modo": "audio",
    "video_id": "",  # para saber cuando empieza un video nuevo
    "parte": 1,      # en "video con audio" se baja el video (parte 1) y luego el audio (parte 2)
}


def ver_info():
    url = entrada_url.get().strip()
    if url == "":
        etiqueta_info.config(text="Primero pega un link", fg="red")
        return

    # mostramos "buscando" y forzamos a la ventana a dibujarlo
    # (si no, se queda congelada sin mostrar nada mientras busca)
    etiqueta_info.config(text="Buscando...", fg="black")
    ventana.update()

    info = obtener_info(url)
    if info == None:
        etiqueta_info.config(text="No se pudo leer el link, revisa que este bien", fg="red")
        return

    texto = "Titulo: " + info["titulo"]
    if info["es_playlist"]:
        texto = texto + "\nEs una playlist con " + str(info["cantidad"]) + " videos"
        # si es playlist marcamos la casilla solita
        var_playlist.set(True)
    else:
        texto = texto + "\nEs un solo video"
        var_playlist.set(False)
    etiqueta_info.config(text=texto, fg="green")


def cambio_modo():
    # la calidad del mp3 solo tiene sentido si se baja audio
    if var_modo.get() == "audio":
        combo_calidad.config(state="readonly")
    else:
        combo_calidad.config(state="disabled")


def elegir_carpeta():
    # abre la ventanita de windows para escoger carpeta
    carpeta = filedialog.askdirectory(initialdir=var_carpeta.get(), title="Elige donde guardar")
    # si le das a cancelar devuelve "" y no cambiamos nada
    if carpeta != "":
        var_carpeta.set(carpeta)


def progreso(d):
    # yt-dlp llama a esta funcion mientras descarga (desde el hilo, no desde la ventana)
    # solo guardamos los datos en "estado", no tocamos la ventana
    info = d.get("info_dict", {})

    # si cambio el id es que empezo otro video, volvemos a la parte 1
    if info.get("id") != estado["video_id"]:
        estado["video_id"] = info.get("id")
        estado["parte"] = 1

    # armamos el comienzo del texto: "Video 3 de 10 - Parte 1 de 2 - "
    inicio = ""
    numero = info.get("playlist_index")
    total_videos = info.get("n_entries")
    if numero != None and total_videos != None:
        inicio = inicio + "Video " + str(numero) + " de " + str(total_videos) + "  -  "
    if estado["modo"] == "video":
        inicio = inicio + "Parte " + str(min(estado["parte"], 2)) + " de 2  -  "

    if d["status"] == "downloading":
        bajado = d.get("downloaded_bytes", 0)
        total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
        if total > 0:
            estado["porcentaje"] = bajado * 100 / total
        velocidad = d.get("speed") or 0
        mb_s = round(velocidad / 1024 / 1024, 2)
        estado["texto"] = inicio + str(round(estado["porcentaje"], 1)) + "%  (" + str(mb_s) + " MB/s)"
    elif d["status"] == "finished":
        estado["porcentaje"] = 100
        if estado["modo"] == "video" and estado["parte"] == 1:
            estado["texto"] = inicio + "lista, sigue el audio..."
        else:
            estado["texto"] = inicio + "Procesando con ffmpeg..."
        estado["parte"] = estado["parte"] + 1


def hilo_descarga(url, modo, carpeta, es_playlist, calidad):
    # esto corre en otro hilo para que la ventana no se congele
    ok, mensaje = descargar(url, modo, carpeta, es_playlist, calidad, progreso)
    estado["resultado"] = ok
    estado["mensaje"] = mensaje
    estado["terminado"] = True


def empezar_descarga():
    url = entrada_url.get().strip()
    if url == "":
        messagebox.showwarning("Falta el link", "Primero pega el link del video o playlist.")
        return
    if not url.startswith("http"):
        messagebox.showwarning("Link raro", "El link debe empezar con http:// o https://")
        return
    if var_carpeta.get().strip() == "":
        messagebox.showwarning("Falta la carpeta", "Elige una carpeta donde guardar.")
        return

    # reiniciamos el estado
    estado["descargando"] = True
    estado["porcentaje"] = 0
    estado["texto"] = "Empezando..."
    estado["terminado"] = False
    estado["resultado"] = False
    estado["mensaje"] = ""
    estado["modo"] = var_modo.get()
    estado["video_id"] = ""
    estado["parte"] = 1

    # desactivamos el boton para que no le den dos veces
    boton_descargar.config(state="disabled")
    etiqueta_estado.config(fg="black")

    # creamos el hilo y lo arrancamos
    # daemon=True hace que el hilo se cierre si cierras la ventana
    hilo = threading.Thread(
        target=hilo_descarga,
        args=(url, var_modo.get(), var_carpeta.get(), var_playlist.get(), var_calidad.get()),
        daemon=True,
    )
    hilo.start()

    revisar_progreso()


def revisar_progreso():
    # se llama a si misma cada 100 milisegundos mientras haya descarga
    barra["value"] = estado["porcentaje"]
    etiqueta_estado.config(text=estado["texto"])

    if estado["terminado"]:
        estado["descargando"] = False
        boton_descargar.config(state="normal")
        if estado["resultado"]:
            barra["value"] = 100
            etiqueta_estado.config(text="Listo!", fg="green")
            messagebox.showinfo("Descarga terminada", "Listo!\n" + estado["mensaje"])
        else:
            barra["value"] = 0
            etiqueta_estado.config(text="Hubo un error", fg="red")
            messagebox.showerror("Error", "No se pudo descargar:\n" + estado["mensaje"])
    else:
        ventana.after(100, revisar_progreso)


# ----- ventana principal -----
ventana = tk.Tk()
ventana.title("Descargador de YouTube")
ventana.geometry("620x560")
ventana.resizable(False, False)

# variables que guardan lo que elige el usuario
var_modo = tk.StringVar(value="audio")
var_calidad = tk.StringVar(value="192")
var_playlist = tk.BooleanVar(value=False)
var_carpeta = tk.StringVar(value=CARPETA_POR_DEFECTO)

titulo = tk.Label(ventana, text="Descargador de YouTube", font=("Arial", 18, "bold"))
titulo.pack(pady=10)

# ----- link -----
marco_url = tk.Frame(ventana)
marco_url.pack(pady=5)

tk.Label(marco_url, text="Link:").pack(side="left")
entrada_url = tk.Entry(marco_url, width=55)
entrada_url.pack(side="left", padx=5)
boton_info = tk.Button(marco_url, text="Ver info", command=ver_info)
boton_info.pack(side="left")

# aqui se muestra el titulo y si es playlist
etiqueta_info = tk.Label(ventana, text="", font=("Arial", 10), wraplength=550, justify="left")
etiqueta_info.pack(pady=10)

# ----- que descargar -----
marco_modo = tk.LabelFrame(ventana, text="Que quieres descargar?", padx=10, pady=5)
marco_modo.pack(fill="x", padx=20, pady=5)

tk.Radiobutton(marco_modo, text="Solo audio (mp3)", variable=var_modo, value="audio", command=cambio_modo).grid(row=0, column=0, sticky="w")
tk.Radiobutton(marco_modo, text="Video con audio (mp4)", variable=var_modo, value="video", command=cambio_modo).grid(row=1, column=0, sticky="w")
tk.Radiobutton(marco_modo, text="Solo video, sin audio (mp4)", variable=var_modo, value="solo_video", command=cambio_modo).grid(row=2, column=0, sticky="w")

tk.Label(marco_modo, text="Calidad mp3 (kbps):").grid(row=0, column=1, padx=(40, 5))
combo_calidad = ttk.Combobox(marco_modo, textvariable=var_calidad, values=["128", "192", "320"], width=6, state="readonly")
combo_calidad.grid(row=0, column=2)

tk.Checkbutton(marco_modo, text="Descargar playlist completa", variable=var_playlist).grid(row=3, column=0, sticky="w", pady=(8, 0))

# ----- carpeta -----
marco_carpeta = tk.LabelFrame(ventana, text="Carpeta donde guardar", padx=10, pady=8)
marco_carpeta.pack(fill="x", padx=20, pady=5)

entrada_carpeta = tk.Entry(marco_carpeta, textvariable=var_carpeta, width=70)
entrada_carpeta.pack(side="left", padx=(0, 5))
tk.Button(marco_carpeta, text="Examinar...", command=elegir_carpeta).pack(side="left")

# ----- descargar y progreso -----
boton_descargar = tk.Button(ventana, text="DESCARGAR", font=("Arial", 12, "bold"), bg="#d32f2f", fg="white", width=20, command=empezar_descarga)
boton_descargar.pack(pady=10)

barra = ttk.Progressbar(ventana, length=560, maximum=100)
barra.pack()

etiqueta_estado = tk.Label(ventana, text="", font=("Arial", 10))
etiqueta_estado.pack(pady=5)

ventana.mainloop()
