from pypdf import PdfReader

def leer_pdf(ruta: str) -> list[dict]:
    lector = PdfReader(ruta)
    paginas = []
    for i, pagina in enumerate(lector.pages, start=1):
        texto = pagina.extract_text() or ''
        if texto.strip():
            paginas.append({'pagina': i, 'texto': texto})
    return paginas

def trocear(texto: str, tam=1000, solape=150) -> list[str]:
    trozos = []
    inicio = 0
    while inicio < len(texto):
        fin = inicio + tam
        trozos.append(texto[inicio:fin])
        inicio += tam - solape
    return trozos