# main.py
# Menu en consola para probar el descargador antes de hacer la interfaz grafica

from descargador import descargar, obtener_info, CARPETA_POR_DEFECTO

print("===== DESCARGADOR DE YOUTUBE =====")

while True:
    url = input("\nPega el link (o escribe 'salir'): ").strip()
    if url.lower() == "salir":
        break
    if url == "":
        print("No pusiste ningun link")
        continue

    # mostramos que es lo que se va a bajar
    info = obtener_info(url)
    if info == None:
        continue
    print("Titulo: " + info["titulo"])

    es_playlist = False
    if info["es_playlist"]:
        print("Es una playlist con " + str(info["cantidad"]) + " videos")
        es_playlist = True
    elif "list=" in url:
        # el link es de un video que esta dentro de una playlist
        resp = input("Este video es parte de una playlist. Bajar toda la playlist? (s/n): ")
        if resp.lower() == "s":
            es_playlist = True

    print("\nQue quieres descargar?")
    print("1. Solo audio (mp3)")
    print("2. Video con audio (mp4)")
    print("3. Solo video, sin audio (mp4)")
    opcion = input("Opcion: ").strip()

    calidad = "192"
    if opcion == "1":
        modo = "audio"
        c = input("Calidad del mp3 (128 / 192 / 320) [192]: ").strip()
        if c in ["128", "192", "320"]:
            calidad = c
    elif opcion == "2":
        modo = "video"
    elif opcion == "3":
        modo = "solo_video"
    else:
        print("Opcion no valida")
        continue

    carpeta = input("Carpeta donde guardar (Enter = " + CARPETA_POR_DEFECTO + "): ").strip()
    carpeta = carpeta.strip('"')  # por si la pegas con comillas desde el explorador

    descargar(url, modo, carpeta, es_playlist, calidad)

print("Adios!")
