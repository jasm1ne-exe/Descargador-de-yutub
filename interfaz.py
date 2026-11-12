# interfaz.py
# Ventana del descargador hecha con tkinter
# Usa las funciones de descargador.py

import tkinter as tk
from descargador import obtener_info


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
    else:
        texto = texto + "\nEs un solo video"
    etiqueta_info.config(text=texto, fg="green")


# ----- ventana principal -----
ventana = tk.Tk()
ventana.title("Descargador de YouTube")
ventana.geometry("600x250")
ventana.resizable(False, False)

titulo = tk.Label(ventana, text="Descargador de YouTube", font=("Arial", 18, "bold"))
titulo.pack(pady=10)

# fila con el campo del link y el boton
marco_url = tk.Frame(ventana)
marco_url.pack(pady=5)

tk.Label(marco_url, text="Link:").pack(side="left")
entrada_url = tk.Entry(marco_url, width=55)
entrada_url.pack(side="left", padx=5)
boton_info = tk.Button(marco_url, text="Ver info", command=ver_info)
boton_info.pack(side="left")

# aqui se muestra el titulo y si es playlist
etiqueta_info = tk.Label(ventana, text="", font=("Arial", 10), wraplength=550, justify="left")
etiqueta_info.pack(pady=15)

ventana.mainloop()
