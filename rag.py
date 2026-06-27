from indexar import recuperar, cliente
from google.genai import types

SYSTEM = (
    'Eres un analista financiero. Responde la pregunta USANDO SOLO el contexto entregado. '
    'Si la respuesta no está en el contexto, di: "No encuentro ese dato en el documento." '
    'Cita siempre la página de donde sacaste la información.'
)

def responder(pregunta: str) -> str:
    trozos = recuperar(pregunta)
    contexto = '\n\n'.join(
        f"[Página {m['pagina']}] {doc}" for doc, m in trozos
    )
    prompt = f'CONTEXTO:\n{contexto}\n\nPREGUNTA: {pregunta}'
    resp = cliente.models.generate_content(
        model='gemini-2.5-flash',
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM, temperature=0.1),
        contents=prompt,
    )
    return resp.text

if __name__ == '__main__':
    print("🤖 Sistema RAG Oficial — Conectado a Gemini API")
    while True:
        q = input('\nPregunta sobre el reporte (o "salir"): ')
        if q.lower() == 'salir':
            break
        if not q.strip():
            continue
        try:
            print(responder(q))
        except Exception as e:
            print(f'Error: {e}')