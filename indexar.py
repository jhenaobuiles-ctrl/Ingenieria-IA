import chromadb
from ingesta import leer_pdf, trocear
from embeddings import embeber, cliente

db = chromadb.PersistentClient(path='./chroma_db')
coleccion = db.get_or_create_collection('reporte_financiero')

def ejecutar_indexacion():
    paginas = leer_pdf('reporte_financiero.pdf')
    ids, docs, metas = [], [], []
    for p in paginas:
        for j, trozo in enumerate(trocear(p['texto'])):
            ids.append(f"p{p['pagina']}_t{j}")
            docs.append(trozo)
            metas.append({'pagina': p['pagina']})

    vectores = []
    # Indexar por lotes de 50 para evitar Error 429
    for i in range(0, len(docs), 50):
        vectores += embeber(docs[i:i+50], tipo='RETRIEVAL_DOCUMENT')

    coleccion.add(ids=ids, embeddings=vectores, documents=docs, metadatas=metas)
    print(f'✅ Indexados con éxito {len(docs)} fragmentos en ChromaDB.')

def recuperar(pregunta: str, k=4):
    vec = embeber([pregunta], tipo='RETRIEVAL_QUERY')[0]
    res = coleccion.query(query_embeddings=[vec], n_results=k)
    return list(zip(res['documents'][0], res['metadatas'][0]))

if __name__ == '__main__':
    ejecutar_indexacion()