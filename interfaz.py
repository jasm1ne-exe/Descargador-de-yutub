# interfaz.py
# Ventana del descargador hecha con tkinter
# Usa las funciones de descargador.py

import tkinter as tk
from tkinter import ttk, filedialog
from descargador import obtener_info, CARPETA_POR_DEFECTO


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


# ----- ventana principal -----
ventana = tk.Tk()
ventana.title("Descargador de YouTube")
ventana.geometry("620x480")
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

ventana.mainloop()
