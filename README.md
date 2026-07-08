# 📊 Dashboard Financiero - Motor RAG Automatizado

Este proyecto es un motor de Recuperación Aumentada por Generación (RAG) especializado en el análisis de reportes y estados financieros. Permite cargar documentos PDF de gran tamaño en memoria, indexar su contenido y realizar consultas conversacionales sin riesgo de alucinación de datos.

## 🛠️ Arquitectura y Tecnologías
- **Interfaz Web:** [Streamlit](https://streamlit.io/) para el despliegue del panel interactivo y la gestión del historial del chat.
- **Orquestación e IA:** SDK oficial moderno `google-genai` conectado al modelo `gemini-2.5-flash`.
- **Procesamiento de Documentos:** Extracción eficiente de texto en memoria con `pypdf`.
- **Persistencia:** Configuración nativa de `st.session_state` para mantener la memoria conversacional (historial user-model).

## 🚀 Instalación y Uso Local

1. Clonar el repositorio:
   ```bash
   git clone [https://github.com/jhenaobuiles-ctrl/Ingenieria-IA.git](https://github.com/jhenaobuiles-ctrl/Ingenieria-IA.git)
   cd Ingenieria-IA