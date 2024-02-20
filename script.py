import json

def migrar_contenido_web(dialogo):
    
    nuevo_contenido = []
    output = dialogo

    # Ejemplo de transformación para diálogos "Normal"
    if "json_response" in output:
        for item in output["json_response"]:
            tipo = item.get("type")
            if tipo == "Normal":
                for mensaje in item.get("messages", []):
                    nuevo_contenido.append({
                        "cuerpo": [{"cuerpo": m, "etiqueta": "span"} for m in mensaje.get("text", [])],
                        "contenedor": "Normal"
                    })
            elif tipo == "Carousel" or tipo == "CardList":
                # Aquí se asume una estructura similar para Carousel y CardList convertida a Carrusel en 2.0
                slides = item.get("slides", []) if tipo == "Carousel" else item.get("list", [])
                for slide in slides:
                    content = slide.get("content", [])
                    title = slide.get("title", "")
                    if isinstance(content, str):  # Si content es una cadena, conviértelo en una lista
                        content = [content]
                    if content:  # Verifica si la lista tiene elementos
                        nuevo_contenido.append({
                            "cuerpo": [
                                {"cuerpo": slide.get("titulo", ""), "etiqueta": "h4"},
                                {"cuerpo": content[0]}  # Ahora es seguro acceder al primer elemento
                            ],
                            "contenedor": "carrusel"
                        })
            elif tipo == "Images":
                for url in item.get("images", []):
                    nuevo_contenido.append({
                        "cuerpo": [{"etiqueta": "img", "atributos": {"src": url}}],
                        "contenedor": "normal"
                    })
            elif tipo == "Youtube":
                for url in item.get("videos", []):
                    # Asumiendo que la URL ya está en formato adecuado para ser embebida
                    nuevo_contenido.append({
                        "cuerpo": [{"etiqueta": "iframe", "atributos": {"src": url, "frameborder": "0", "allowfullscreen": "true"}}],
                        "contenedor": "normal"
                    })

    return nuevo_contenido

def migrar_botones(botones):
    if not botones:
        return []
    if isinstance(botones[0], dict):  # Estructura con 'text' y 'message'
        return [{"cuerpo": boton["message"],  "titulo": boton["text"]} for boton in botones]
    elif isinstance(botones[0], str):  # Estructura con solo texto
        return [{"cuerpo": boton, "titulo": boton} for boton in botones]

def migrar_dialogo(nodo):
    if nodo.get('type') != 'standard':
        return nodo
    output = nodo.get('output', {})
    contenidoWeb = migrar_contenido_web(output)
    
    if 'buttons' in output:
        botones_migrados = migrar_botones(output['buttons'])
        contenidoWeb.append({"cuerpo": botones_migrados, "contenedor": "opciones"})
    
    nodo['output'] = {"contenidoWeb": contenidoWeb}
    return nodo

def migrar_archivo_json(ruta_archivo_original, ruta_archivo_destino):
    with open(ruta_archivo_original, 'r', encoding='utf-8') as archivo:
        datos = json.load(archivo)
    
    dialog_nodes_migrados = [migrar_dialogo(nodo) for nodo in datos['dialog_nodes']]
    datos['dialog_nodes'] = dialog_nodes_migrados
    
    with open(ruta_archivo_destino, 'w', encoding='utf-8') as archivo_destino:
        json.dump(datos, archivo_destino, ensure_ascii=False, indent=4)

# Definir las rutas de los archivos
ruta_archivo_original = 'pruebaCarrusel.json'
ruta_archivo_destino = 'resultadoCarrusel.json'

# Ejecutar la migración
migrar_archivo_json(ruta_archivo_original, ruta_archivo_destino)
