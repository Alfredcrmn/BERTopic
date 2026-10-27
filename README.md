# Tópicos de Germana con BERTopic

Actividad sobre un corpus literario en español. Se comparan tres configuraciones de BERTopic con embeddings de MiniLM y se incluye el bonus de nombrado de tópicos con Gemini.

**Código público:** [Link al repo]

**Reporte para revisión:** [reporte/reporte_bertopic_germana.md](reporte/reporte_bertopic_germana.md). Incluye metodología, tablas, cinco figuras, discusión, bonus, bibliografía, uso de IA y anexos con tres párrafos completos por tópico. La exportación a PDF queda pendiente de la revisión manual.

## Estructura

```text
BERTopic/
├── 01_germana_minilm.ipynb       # Limpieza, segmentación, tokens y embeddings
├── 02_configuraciones_bertopic.ipynb
├── 03_analisis_bertopic.ipynb    # Nombres, figuras y evaluación cualitativa
├── germana.txt                  # Original de Gutenberg, sin modificaciones
├── resultados/                 # CSV, embeddings, estadísticas y figuras
│   ├── configuraciones/        # A/B/C, stopwords y gráficos interactivos
│   └── analisis/               # Nombres y evidencia de la revisión
├── bonus_gemini/               # Prompt, datos, respuesta original y comparación
├── reporte/                    # Texto editable y figuras utilizadas
├── scripts/                    # Ejecución, verificación y generación del reporte
├── requirements.txt            # Dependencias directas fijadas
└── requirements-lock.txt       # Entorno completo registrado en macOS/Python 3.9
```

`.venv/` y `.cache/` son recursos locales ignorados; no forman parte del material que se debe subir. No contienen código necesario para revisar los resultados. Los HTML comparten una sola copia local de `plotly.min.js`: conservar la estructura de `resultados/configuraciones` al descargarlos.

## Instalación y reproducción

La ejecución de referencia se realizó con Python 3.9 en macOS ARM64, en CPU. Desde este directorio:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Para recrear las dependencias transitivas del entorno de referencia en macOS puede usarse `requirements-lock.txt` en lugar de `requirements.txt`. Algunas dependencias del lock son específicas de esa plataforma. En otros sistemas, usar las dependencias directas y registrar las versiones resultantes.

Los notebooks ya incluyen resultados y pueden leerse sin descargar el modelo. Para volver a ejecutar, seleccionar `.venv/bin/python` como intérprete o usar:

```sh
python scripts/ejecutar_notebooks.py
```

El comando ejecuta 01, 02 y 03 en orden con el Python activo y un kernel temporal. También permite ejecutar etapas concretas:

```sh
python scripts/ejecutar_notebooks.py 02 03
```

La primera ejecución de 01 requiere conexión para descargar MiniLM. Se reutiliza la revisión exacta en `resultados/modelo_revision.json`, sin actualizarla automáticamente. Si ya existen segmentos y embeddings, 02 y 03 pueden ejecutarse sin conexión. La lista exacta de stopwords está incluida y no necesita descargarse nuevamente.

Para comprobar la entrega:

```sh
python scripts/verificar_entrega.py
```

## Decisiones principales

- Un documento equivale a un párrafo: 1,177 segmentos útiles, tras excluir 139 párrafos con menos de cinco palabras. No se encontraron duplicados exactos.
- Modelo: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, vectores de 384 dimensiones. Los 256 párrafos que superan 128 tokens se codifican por fragmentos y se combinan mediante un promedio ponderado por tokens con normalización final.
- `CountVectorizer` aplica 313 stopwords de español de NLTK; se conservan acentos y ñ. UMAP usa `random_state=42` y `n_jobs=1`.

| Configuración | min_cluster_size | min_samples | ngram_range | Tópicos sin -1 | % outliers |
|---|---:|---:|---|---:|---:|
| A | 15 | 5 | (1, 1) | 16 | 19.97 |
| B | 30 | 10 | (1, 1) | 5 | 21.33 |
| C | 30 | 10 | (1, 2) | 5 | 21.33 |

A/B cambian conjuntamente dos parámetros: no separan sus efectos individuales. C actualiza las palabras de B, conservando grupos y representantes. Se selecciona A por el detalle de sus núcleos temáticos, con reservas sobre los grupos de estilo o interlocutor. Los outliers permanecen en -1.

## Bonus con Gemini

Se enviaron los 16 tópicos de A con diez términos y tres ejemplos completos cada uno. No se enviaron los nombres previos de Codex. La respuesta proporcionada por el usuario permanece intacta en `bonus_gemini/respuesta_gemini_original.json`.

Modelo reportado: Gemini 3.1 Pro; hora 18:35; thinking level `low`; suscripción Plus, según lo indicado por el usuario. La fecha de ejecución, tokens, tiempo de respuesta y costo adicional no se documentaron. No se utilizó una API.

```sh
python bonus_gemini/comparar_respuesta.py
```

El script valida estructura e identificadores y regenera la comparación. `preparar_entrada.py` permite reconstruir el prompt y los datos a partir de los resultados originales de A. Ninguno de estos scripts llama a una API. Las etiquetas editoriales revisadas se guardan aparte de las propuestas originales.

## Reporte editable

El Markdown entregado es el archivo que se debe revisar. Sus imágenes están en `reporte/figuras/`. Si se modifica a mano, no ejecutar el generador sin guardar una copia: el comando sobrescribe el Markdown con el contenido definido en `scripts/generar_reporte.py`.

Para regenerar las figuras y el texto desde el código:

```sh
python scripts/figuras_reporte.py
python scripts/generar_reporte.py
```

Por defecto no se crea ningún PDF. El parámetro `--pdf` es una exportación futura y sólo debe utilizarse una vez incorporadas las correcciones al generador. El placeholder `[Link al repo]` está en el reporte y este README, listo para reemplazarse cuando exista el repositorio.

## Fuente y uso de IA

Corpus: [Germana, Project Gutenberg, eBook 29640](https://www.gutenberg.org/ebooks/29640), Edmond About, traducción de Tomás Orts-Ramos. El archivo original conserva sus créditos y licencia. Las notas y textos descartados para el modelado permanecen en ese archivo.

Codex asistió en implementación, decisiones, nombrado inicial, discusión y redacción. Gemini se usó únicamente en el bonus de nombrado. La revisión de sus propuestas también fue asistida por Codex y no constituye una anotación humana independiente. La bibliografía y el alcance de estas ayudas se detallan en el reporte.
