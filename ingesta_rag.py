import os
from pypdf import PdfReader
import chromadb

# 1. Inicializar el cliente de ChromaDB local (No requiere API key para embeddings)
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Crear o recuperar la colección. Chroma usará su modelo embedding local por defecto
coleccion = chroma_client.get_or_create_collection(name="reporte_financiero")

def extraer_texto_pdf(ruta_pdf: str) -> list:
    """Lee el PDF y devuelve una lista de tuplas (texto_pagina, numero_pagina)."""
    reader = PdfReader(ruta_pdf)
    paginas_texto = []
    for num_pag, pagina in enumerate(reader.pages):
        texto = pagina.extract_text()
        if texto:
            paginas_texto.append((texto, num_pag + 1))
    return paginas_texto

def crear_chunks(paginas_texto: list, chunk_size=1000, chunk_overlap=200) -> list:
    """Fragmenta el texto respetando el tamaño y el solapamiento requerido."""
    chunks = []
    for texto, num_pag in paginas_texto:
        inicio = 0
        while inicio < len(texto):
            fin = inicio + chunk_size
            fragmento = texto[inicio:fin]
            
            chunks.append({
                "texto": fragmento,
                "metadata": {"pagina": num_pag}
            })
            inicio += (chunk_size - chunk_overlap)
    return chunks

def main():
    ruta_pdf = 'reporte_financiero.pdf'
    
    if not os.path.exists(ruta_pdf):
        raise FileNotFoundError(f"No se encontró el archivo '{ruta_pdf}' en la raíz del proyecto.")

    print(f"Procesando '{ruta_pdf}'...")
    paginas = extraer_texto_pdf(ruta_pdf)
    
    fragmentos = crear_chunks(paginas)
    print(f"Total fragmentos generados: {len(fragmentos)}")
    
    print("Generando embeddings e indexando localmente con ChromaDB...")
    
    ids = []
    documentos = []
    metadatos = []

    for idx, frag in enumerate(fragmentos):
        ids.append(f"id_{idx}")
        documentos.append(frag["texto"])
        metadatos.append(frag["metadata"])

    # Guardar en la base de datos. Chroma se encarga de vectorizar automáticamente cada documento
    if documentos:
        coleccion.add(
            ids=ids,
            documents=documentos,
            metadatas=metadatos
        )
        print("✅ Pipeline ejecutado con éxito. Carpeta './chroma_db' creada con embeddings locales.")
    else:
        print("[Error] No se generó texto para indexar.")

if __name__ == '__main__':
    main()