"""Compone el reporte editable desde resultados guardados. Exporta PDF sólo si se indica --pdf."""
from pathlib import Path
import argparse
import ast
import csv
import json
import re
from html import unescape
from xml.sax.saxutils import escape
from reportlab import __file__ as reportlab_file
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether

BASE=Path(__file__).resolve().parent.parent
OUT=BASE/'reporte'; OUT.mkdir(parents=True,exist_ok=True)
ROOT=BASE/'resultados'
parser=argparse.ArgumentParser()
parser.add_argument('--repo-url',default='[Link al repo]')
parser.add_argument('--pdf',action='store_true',help='Exportar PDF sólo después de revisar el Markdown')
args=parser.parse_args()
fontdir=Path(reportlab_file).parent/'fonts'
for name,file in [('Vera','Vera.ttf'),('VeraBold','VeraBd.ttf'),('VeraItalic','VeraIt.ttf'),('VeraBoldItalic','VeraBI.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(fontdir/file)))
pdfmetrics.registerFontFamily('Vera',normal='Vera',bold='VeraBold',italic='VeraItalic',boldItalic='VeraBoldItalic')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleR',fontName='VeraBold',fontSize=28,leading=33,textColor=colors.HexColor('#183c58'),spaceAfter=18))
styles.add(ParagraphStyle(name='H1R',fontName='VeraBold',fontSize=17,leading=22,textColor=colors.HexColor('#183c58'),spaceBefore=6,spaceAfter=13,keepWithNext=True))
styles.add(ParagraphStyle(name='H2R',fontName='VeraBold',fontSize=11.7,leading=15,spaceBefore=12,spaceAfter=7,keepWithNext=True,textColor=colors.HexColor('#24678d')))
styles.add(ParagraphStyle(name='BodyR',fontName='Vera',fontSize=10.1,leading=14.7,spaceAfter=9))
styles.add(ParagraphStyle(name='SmallR',fontName='Vera',fontSize=8.6,leading=12,spaceAfter=7))
styles.add(ParagraphStyle(name='QuoteR',fontName='Vera',fontSize=9.1,leading=13,spaceAfter=10,leftIndent=9,borderColor=colors.HexColor('#c4d5df'),borderWidth=.5,borderPadding=7))
styles.add(ParagraphStyle(name='CellR',fontName='Vera',fontSize=8.3,leading=11,spaceAfter=0))
styles.add(ParagraphStyle(name='CellHeadR',parent=styles['CellR'],fontName='VeraBold',textColor=colors.white))
styles.add(ParagraphStyle(name='ExampleR',parent=styles['SmallR'],keepWithNext=True))
styles.add(ParagraphStyle(name='CaptionR',fontName='Vera',fontSize=8.7,leading=12,spaceAfter=10,textColor=colors.HexColor('#455968')))
story=[];md=[]

def clean(s): return s.replace('–','-').replace('—','-').replace('\u00a0',' ')
def para(s,style='BodyR',literal=False):
    s=clean(str(s)); text=escape(s) if literal else s
    story.append(Paragraph(text,styles[style]))
    if literal:
        md_text = s
    else:
        md_text = re.sub(r'<br\s*/?>', '\\n', s)
        md_text = re.sub(r'<link href="([^"]+)"[^>]*>(.*?)</link>', r'[\2](\1)', md_text)
        md_text = md_text.replace('<b>', '**').replace('</b>', '**').replace('<i>', '*').replace('</i>', '*')
        md_text = unescape(re.sub('<[^>]+>', '', md_text))
    if style == 'TitleR': md_text = '# ' + md_text.replace('\n', ' ')
    md.append(md_text+'\n')
def heading(s,level=1):
    para(s,'H1R' if level==1 else 'H2R'); md[-1]='#'*(level+1)+' '+md[-1]
def page(): story.append(PageBreak());md.append('\n---\n')
def table(headers,rows,widths):
    data=[[Paragraph(escape(str(x)),styles['CellHeadR']) for x in headers]]
    data += [[Paragraph(escape(clean(str(x))),styles['CellR']) for x in row] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#214f6d')),('VALIGN',(0,0),(-1,-1),'TOP'),
       ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f0f5f8'),colors.white]),
       ('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#214f6d')),
       ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
       ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.append(t);story.append(Spacer(1,10))
    md.append('| '+' | '.join(map(str,headers))+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+
       '\n'.join('| '+' | '.join(str(x).replace('|',' / ') for x in row)+' |' for row in rows)+'\n')
def figure(file,width,caption):
    path=OUT/'figuras'/file
    im=Image(str(path));im.drawHeight*=width/im.drawWidth;im.drawWidth=width
    story.append(im);para(caption,'CaptionR');md.append(f'![{caption}](figuras/{file})\n')
def rows(path):
    with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

summary=json.loads((ROOT/'resumen_preparacion.json').read_text())
labels=json.loads((ROOT/'analisis/nombres_y_criterios.json').read_text())
infos={c:rows(ROOT/f'configuraciones/{c}/topic_info.csv') for c in 'ABC'}
reps={c:rows(ROOT/f'configuraciones/{c}/ejemplos_representativos.csv') for c in 'AB'}
segments={r['segmento_id']:r for r in rows(ROOT/'segmentos.csv')}
comparison=rows(ROOT/'configuraciones/comparacion.csv')
bonus=rows(BASE/'bonus_gemini/comparacion_etiquetas.csv')
W=A4[0]-40*mm

para('PROCESAMIENTO DE LENGUAJE NATURAL','SmallR')
para('Tópicos de <i>Germana</i><br/>con BERTopic','TitleR')
para('Corpus en español · comparación de tres configuraciones · nombrado con Gemini','H2R')
para('Reporte de actividad individual | 25 de octubre de 2026','SmallR')
para('<b>Código y materiales reproducibles:</b> '+escape(args.repo_url))
heading('1. Introducción y descripción del corpus')
para('El objetivo es explorar qué grupos de contenido recupera BERTopic en una novela y valorar si sus palabras clave y ejemplos permiten interpretarlos como tópicos. Se analiza <i>Germana</i>, de Edmond About, en traducción de Tomás Orts-Ramos. El archivo proviene de Project Gutenberg, eBook 29640; la portada de esta edición indica Buenos Aires, 1918 [1]. El idioma del corpus es español. La fecha de la edición no se presenta como fecha de composición de la obra.')
para('La novela ofrece narración, diálogos, cartas y descripciones sobre relaciones familiares, enfermedad e intriga. Esta variedad permite contrastar temas de contenido con grupos que podrían obedecer al interlocutor o a la forma narrativa. Se utiliza el libro completo como un solo corpus, no como una colección de obras independientes.')
table(['Unidad de análisis','Documentos finales','Palabras útiles','Embeddings'],[['Un párrafo','1,177','67,601','1,177 × 384']], [W*.27,W*.22,W*.23,W*.28])
heading('Resultado principal',2)
para('La configuración A distingue 16 grupos y conserva 235 párrafos como outliers (19.97 %). B y C producen 5 grupos con 251 outliers (21.33 %). A conserva mejor temas concretos como dinero, cuidados médicos, venenos y el episodio de China; también genera grupos de diálogo o acotación que no deben interpretarse como temas homogéneos.')
para('El bonus usa Gemini únicamente para proponer nombres de los grupos de A. Aporta etiquetas legibles y explicaciones, pero también sobreinterpretaciones. No modifica las asignaciones de BERTopic ni constituye una comparación de algoritmos de agrupamiento.')
para('<b>Organización:</b> segmentación; metodología y configuraciones; resultados y visualizaciones; discusión; bonus; bibliografía y uso de IA. Los anexos incluyen tres párrafos completos por tópico de A y B/C, y el prompt completo de Gemini.','SmallR')

page();heading('2. Segmentación y estadísticas')
para('Se identifica el cuerpo mediante los marcadores de inicio y fin de Gutenberg. Se retiran portada, créditos, índice, números y títulos de capítulo, FIN y notas finales. Se segmenta por líneas en blanco: los saltos simples de maquetación se unen dentro del párrafo. Se conservan capítulo y orden de origen para rastrear los segmentos.')
para('Se eliminan llamadas de notas [A]-[F] y marcas de cursiva con guion bajo, se normalizan espacios y se excluyen párrafos con menos de cinco palabras. Después se buscan duplicados exactos del texto limpio. No se eliminan acentos, ñ, nombres de personajes ni contenido narrativo; las stopwords se aplican más adelante, sólo al vectorizador.')
table(['Indicador','Valor'],[['Párrafos narrativos antes del filtro','1,316'],['Párrafos con menos de 5 palabras','139'],['Duplicados exactos eliminados','0'],['Segmentos finales / capítulos','1,177 / 15'],['Palabras: total / promedio / mediana','67,601 / 57.44 / 28'],['Palabras: mínimo / máximo','5 / 568'],['Tokens con especiales: promedio / mediana / máximo','87.34 / 45 / 787'],['Párrafos que exceden 128 tokens','256 (21.75 %)']], [W*.68,W*.32])
figure('longitudes.png',W,'Figura 1. Distribución de longitudes. La línea roja marca los 128 tokens de MiniLM; palabras y tokens no son equivalentes.')
para('Predominan los segmentos breves, en parte por el diálogo, pero existe una cola de párrafos extensos. La segmentación cumple la unidad solicitada para libros y supera los 500 segmentos sugeridos. Eliminar duplicados exactos no elimina frases casi iguales; esta redundancia se observa posteriormente en el tópico financiero.','SmallR')

page();heading('3. Metodología')
heading('3.1 Embeddings y tratamiento de párrafos largos',2)
para('Se eligió <b>sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2</b> porque admite español y produce vectores compactos de 384 dimensiones aptos para agrupamiento. Se favoreció la eficiencia para comparar configuraciones y la continuidad con el ejemplo de clase, sin asumir superioridad sobre otros modelos [2, 3].')
para('Revisión descargada: <font size="8">e8f8c211226b894fcb81acc59f3b34ba3efd5f42</font>. Sentence Transformers limita la entrada a 128 tokens: dos especiales y hasta 126 de contenido. Es el límite operativo del modelo, no el máximo del tokenizador subyacente [3].')
para('Los 256 párrafos largos se dividen en fragmentos contiguos de hasta 126 tokens, sin solapamiento. Cada fragmento recibe sus tokens especiales, se codifica con el modelo en modo de evaluación y se obtiene su embedding. El vector de párrafo es el promedio de esos vectores ponderado por la cantidad de tokens de contenido; finalmente se normaliza a longitud uno. Los párrafos cortos tienen un solo fragmento. Se procesan 1,555 fragmentos en lotes de 32, en CPU, y se conservan 1,177 documentos.')
para('<b>Decisión y límite:</b> el promedio ponderado evita truncar contenido sin crear documentos adicionales para HDBSCAN, pero puede diluir cambios de asunto y pierde relaciones entre fragmentos. No se entrenaron capas, ajustaron pesos ni optimizó una pérdida propia. El límite de tokens, la combinación y el lote son decisiones de inferencia, no hiperparámetros de entrenamiento.')
heading('3.2 De los vectores a los tópicos',2)
para('BERTopic reduce los embeddings con UMAP, agrupa con HDBSCAN y describe cada grupo con c-TF-IDF. UMAP usa 15 vecinos, 5 componentes, min_dist=0, distancia coseno, random_state=42 y n_jobs=1. La semilla permite reproducir la ejecución en el entorno registrado, sin garantizar identidad entre cualquier hardware o versión [4, 5].')
para('HDBSCAN usa distancia euclídea, selección eom y prediction_data=True. El grupo -1 contiene documentos fuera de grupos suficientemente densos: no representa un tema ni un error de lectura. Los tamaños mínimos se comparan en la sección 4 [6].')
heading('3.3 Stopwords y representación',2)
para('CountVectorizer aplica 313 stopwords españolas de NLTK, minúsculas, min_df=1 y strip_accents=None. Las palabras funcionales se conservan para embeddings y se retiran al describir tópicos. El vectorizador se ajusta a textos concatenados por grupo: min_df=1 conserva términos presentes en un único tópico. Se mantienen nombres y tratamientos para examinar su predominio [8, 9].')
para('c-TF-IDF destaca términos frecuentes dentro de un grupo en relación con el conjunto de grupos; sus pesos no son probabilidades. Se muestran diez términos por tópico. Se usa nr_topics=None y no se fusionan tópicos posteriormente. La configuración multilingüe preserva acentos y ñ en el preprocesamiento de BERTopic [4, 7].')

page();heading('4. Configuraciones y comparación')
para('Se reutilizan los mismos segmentos y embeddings, en idéntico orden. A y B ajustan UMAP/HDBSCAN por separado con la misma semilla. C es una copia de B cuya representación se actualiza con bigramas mediante update_topics; no requiere repetir el agrupamiento.')
table(['Configuración','min_cluster_size','min_samples','ngram_range'],[['A: grupos más específicos','15','5','(1, 1)'],['B: criterio más conservador','30','10','(1, 1)'],['C: B con bigramas','30','10','(1, 2)']], [W*.38,W*.23,W*.19,W*.20])
para('min_cluster_size fija el tamaño mínimo de un grupo; min_samples influye en el criterio de densidad y ruido. Los valores 15/5 y 30/10 son puntos de partida para 1,177 párrafos, no valores óptimos conocidos. A frente a B modifica ambos: se evalúa un efecto conjunto y no se atribuye causalmente un cambio a uno solo. B frente a C aísla el efecto del vectorizador sobre las descripciones [4].')
table(['Conf.','Tópicos¹','Outliers','% outliers','Tamaño min.-máx.','Diversidad²'],[[r['configuracion'],r['topicos_sin_outliers'],r['outliers'],f"{float(r['porcentaje_outliers']):.2f}",f"{r['menor_topico']}-{r['mayor_topico']}",f"{float(r['diversidad_top10']):.4f}"] for r in comparison], [W*.11,W*.12,W*.14,W*.17,W*.24,W*.22])
para('¹ Sin contar -1. ² Proporción de términos diferentes entre las listas top-10; no es una medida de coherencia semántica. Un bigrama cuenta como un término.','SmallR')
heading('4.1 Qué cambia y qué permanece',2)
para('A genera mayor detalle: 16 grupos frente a 5 en B/C. En B, 62 de los 64 documentos de A4 (atención médica) y los 21 de A13 (China) pasan al grupo B0, junto con otros episodios. Ese grupo concentra 454 párrafos (38.57 % del corpus); B0 y B1 suman 749 (63.64 %). La reducción de grupos simplifica la salida pero mezcla contenido distinto.')
para('Los IDs son locales a cada configuración: A0 corresponde principalmente a B1, no a B0. La tabla transicion_A_B.csv permite seguir esas correspondencias. No se interpreta un cambio de número como un cambio temático por sí solo.')
para('B y C tienen exactamente las mismas asignaciones y outliers. Los bigramas incorporan expresiones como señora chermidy y señor duque, pero también doctor dijo. La diversidad sube de 0.74 a 0.78, sin evidencia concluyente de una mejora temática. La diferencia es descriptiva, no un mejor agrupamiento.')
para('Se elige A por la lectura de palabras y ejemplos, no sólo por sus conteos. Los tiempos no se presentan como benchmark: C sólo actualiza palabras y el primer ajuste puede incluir compilación.', 'SmallR')

page();heading('5. Resultados: tópicos de A')
para('Tabla elaborada a partir de get_topic_info. Los nombres son interpretativos y fueron propuestos con asistencia de Codex antes del bonus. La valoración es cualitativa y no una métrica externa. Los tres párrafos completos de cada tópico se incluyen en el anexo A.')
infoA=infos['A']
table(['ID','n','% corpus','Nombre interpretativo','Coherencia'],[[r['Topic'],r['Count'],f"{100*int(r['Count'])/1177:.2f}",labels['A'][r['Topic']][0],labels['A'][r['Topic']][1]] for r in infoA], [W*.07,W*.08,W*.13,W*.52,W*.20])
para('El grupo 0 concentra el 28.12 % del corpus y muestra un vínculo dialogal amplio. T6 (dinero), T12 (venenos) y T13 (China) son los núcleos más claros; T4 contiene un núcleo médico reconocible con algunos miembros más ambiguos. T3, T10 y T11 tienen una interpretación temática débil. Las etiquetas describen lo observado sin afirmar que los 16 grupos sean temas literarios de igual calidad.','SmallR')

page();heading('5.1 Contraste con B y C')
para('B y C comparten los siguientes grupos y conteos. La tabla conserva nombres interpretativos comunes, porque la actualización de unigramas a bigramas no cambia sus documentos. Los representantes completos están en el anexo B; para C se usan los mismos de B.')
table(['ID B/C','n','Nombre interpretativo','Lectura crítica'],[[r['Topic'],r['Count'],labels['B'][r['Topic']][0],labels['B'][r['Topic']][1]] for r in infos['B']], [W*.12,W*.10,W*.57,W*.21])
heading('Qué aporta leer los ejemplos',2)
para('La categoría B0 incluye, entre sus representantes, el derroche del duque, la evolución de la enfermedad de Germana y la crianza clandestina del niño. La coincidencia de personajes y contexto social no permite nombrarla como un asunto único. Por contraste, B4 mantiene un núcleo financiero semejante a A6.')
para('B1 mezcla declaraciones amorosas y reproches familiares. En el conjunto de sus documentos, el 94.92 % comienza por --. B2 se articula alrededor del duque y París, y B3 alrededor del doctor: identifican referencias e interlocutores, más que temas necesariamente independientes.')
heading('Alcance de la inspección',2)
para('Se revisaron tres representantes automáticos por tópico de A/B, los mismos para C, dos documentos adicionales por tópico de A elegidos con semilla 17 y diez outliers de A con semilla 42. Se guardan 42 casos adicionales en muestra_revision.csv. No se afirma haber validado individualmente cada uno de los 1,177 párrafos. Un representante automático puede destacar rasgos dominantes y ocultar heterogeneidad.')
para('En A6 los dos primeros representantes repiten casi la misma frase sobre cincuenta mil francos de renta. Fueron conservados porque son documentos distintos y pertenecen a la selección automática; se informa su redundancia en vez de reemplazarlos silenciosamente. Los CSV identifican cada ejemplo, su capítulo y su posición, facilitando su contraste con el corpus.')

page();heading('5.2 Palabras representativas: T0-T7')
figure('palabras_A_1.png',W,'Figura 2. Cinco términos de mayor peso c-TF-IDF por tópico de A (primera mitad). Cada panel tiene su propia escala horizontal; las barras no son probabilidades.')
para('T6 se reconoce por francos, mil, dinero y renta, en concordancia con los ejemplos financieros. T4 reúne Le Bris, doctor y Delviniotis y se relaciona con la atención médica. En T0 y T3 predominan usted, señora o duque: su lectura depende de revisar los párrafos y no sólo sus términos.','SmallR')

page();heading('5.3 Palabras representativas: T8-T15')
figure('palabras_A_2.png',W,'Figura 3. Cinco términos de mayor peso c-TF-IDF por tópico de A (segunda mitad). Se conserva el grupo -1 en el cálculo de c-TF-IDF, aunque no se presenta como tópico.')
para('T12 destaca por veneno, venenos y arsénico; T13 por nombres propios, misioneros y Náyade. Los ejemplos confirman dos núcleos de contenido. T10, con dijo y levantó, capta acotaciones; T11, con París, reúne usos de una localización sin un único asunto. Los términos específicos ayudan a nombrar, pero no demuestran por sí solos coherencia de todo el grupo.','SmallR')

page();heading('5.4 Tamaños y outliers')
figure('distribucion.png',W,'Figura 4. Documentos por grupo en las tres configuraciones. El rojo identifica -1. Las escalas horizontales son comunes y los números de tópico no son equivalentes entre modelos.')
para('A distribuye los documentos en más grupos y mantiene algunos episodios pequeños, como China. B/C concentran gran parte del corpus en dos grupos extensos. Esta figura respalda la selección de A por detalle, pero no prueba que todos sus grupos pequeños sean válidos.')
heading('Qué se hizo con los documentos sin asignación',2)
para('Se conservan como -1: 235/1177 en A (19.97 %) y 251/1177 en B/C (21.33 %). No se eliminan del corpus ni se ejecuta reduce_outliers. Forzar una pertenencia impediría distinguir los casos ambiguos de la comparación inicial.')
para('En la muestra de outliers hay conversaciones, transiciones y descripciones comprensibles. Por ejemplo, germana_0036 habla de deudas de la duquesa y germana_0617 de la convalecencia de Germana. Que exista contenido reconocible no implica que forme un grupo denso en la representación utilizada.')
para('La mediana de longitud es 32 palabras para los outliers de A frente a 27 para los asignados. Por tanto, el ruido no se explica solamente por textos demasiado breves. Tampoco un menor porcentaje de -1 constituye por sí mismo una mejora de calidad.')

page();heading('5.5 Proximidad semántica entre grupos')
figure('similitud.png',W*.91,'Figura 5. Similitud coseno entre centroides de los tópicos de A, calculados con los embeddings originales de 384 dimensiones; no es un mapa UMAP ni una matriz de probabilidades.')
para('Se promedian los vectores de los documentos de cada tópico y se compara la dirección de los centroides. La mayor similitud entre grupos distintos aparece en T7-T8 (0.845), seguida de T1-T8 (0.832). Las escenas de alcoba, la vida afectiva y los conflictos familiares comparten personajes y situaciones; la proximidad es compatible con ese solapamiento.')
para('Un centroide próximo no prueba homogeneidad interna ni equivalencia entre tópicos. No se usa un umbral de fusión y no se modifica el modelo a partir de la figura. El resultado ayuda a explicar por qué una novela puede presentar fronteras temáticas menos nítidas que un corpus de artículos independientes.')

page();heading('6. Discusión y conclusiones')
heading('6.1 Tópicos que tienen sentido',2)
para('Dinero, rentas y especulación (T6) muestra concordancia entre vocabulario y ejemplos. Venenos e intriga de envenenamiento (T12) reúne un mecanismo narrativo concreto. El conflicto de la Náyade y los misioneros en China (T13) recupera un episodio distintivo. El núcleo de enfermedad y tratamiento (T4) también es interpretable, aunque no todos sus documentos describen procedimientos clínicos.')
para('La legitimidad y maternidad de los Villanera (T1) y la decadencia económica del duque (T2) son lecturas razonables con solapamiento entre personajes y asuntos. La especificidad se debe contrastar con la narración: que un nombre propio tenga mucho peso no convierte el grupo en un tema independiente.')
heading('6.2 Grupos débiles y posibles causas',2)
para('T0 mezcla amor, reproche y negociación; el 93.66 % de sus documentos comienza con -- y su mediana es 15 palabras. T3 agrupa fórmulas dirigidas al duque; T5 conversaciones con el doctor; T10 gestos y entradas que introducen intervenciones; T11 referencias a París. Estos grupos tienen un vínculo de interlocutor, lugar o función discursiva, pero una identidad temática más débil.')
para('El indicador de diálogo es sólo el inicio literal -- y no detecta todas las intervenciones. Aun así, su distribución sugiere que el modelo captura estilo además de contenido. Los párrafos dialogados cortos dependen del contexto de sus vecinos; la unidad de análisis elegida impide recuperar siempre ese contexto. El promedio de fragmentos de párrafos largos introduce otro posible factor de mezcla.')
heading('6.3 Límites de la comparación',2)
para('Se estudia una sola obra, un modelo de embeddings y una semilla de UMAP. No se midió estabilidad entre semillas, ni coherencia con anotadores externos, ni se optimizó una pérdida o métrica supervisada. Las valoraciones alta, media o baja son interpretaciones asistidas, no puntuaciones calculadas. La diversidad léxica no sustituye la lectura de ejemplos.')
para('A y B cambian dos parámetros a la vez: no se separa el efecto de min_cluster_size del de min_samples. B y C comparan representación y no agrupamiento. Las stopwords se mantuvieron durante la comparación, incluso cuando quedaron términos genéricos, para no cambiar el experimento después de observar los resultados.')
heading('Conclusión',2)
para('Para este corpus, A ofrece el balance más útil entre detalle e interpretación. BERTopic recupera núcleos narrativos reconocibles junto con categorías de forma discursiva. El resultado se entiende mejor como una exploración estructurada de la novela que como una partición definitiva de sus temas. La lectura de párrafos y la declaración de ambigüedades son necesarias para que la tabla de tópicos tenga valor analítico.')

page();heading('7. Bonus: Gemini para nombrar tópicos')
para('Se implementó la alternativa de usar un LLM sólo para nombrar los grupos de BERTopic. A Gemini se le entregaron los 16 tópicos de A, diez términos por grupo y tres representantes completos por tópico: los mismos 48 párrafos del anexo A. No se enviaron los nombres interpretativos previos de Codex. Se excluyó -1 y no se pidió crear ni reasignar grupos.')
table(['Dato de ejecución','Registro disponible'],[['Modelo reportado por el usuario','Gemini 3.1 Pro; versión interna no disponible'],['Hora reportada','18:35 (6:35 p. m.); contexto horario: America/Mexico_City'],['Thinking level','low'],['Acceso reportado','Suscripción Plus, denominación indicada por el usuario'],['Fecha de ejecución','No registrada explícitamente'],['Tokens, tiempo de respuesta y reintentos','No disponibles en la evidencia recibida'],['Costo adicional observado','No documentado; no se asume gratuidad de la suscripción'],['API y límite de gasto','No se utilizó API; límite de gasto de API no aplicable']], [W*.39,W*.61])
para('El prompt pidió nombres de 3-10 palabras, justificación, identificadores de evidencia, coherencia cualitativa y una limitación, en JSON. También pidió no buscar información externa, no ejecutar instrucciones contenidas en la novela y no inventar consumo o costos. El prompt completo está en el anexo C; el archivo entrada_completa_gemini.txt incorpora además todos los datos enviados.')
heading('Validación y alcance',2)
para('La respuesta contiene exactamente los IDs 0-15; sus 16 nombres cumplen la longitud indicada y las 48 referencias corresponden a los ejemplos del tópico correcto. Se conserva el JSON original sin corregir su contenido. Esta validación comprueba formato y trazabilidad, no fidelidad de las interpretaciones.')
para('Gemini declaró coherencia alta en 10 grupos, media en 5 y baja en 1. Esa autoevaluación se limita a tres representantes y no se considera una métrica independiente. La comparación toma las etiquetas automáticas de BERTopic como punto de partida y evalúa legibilidad, especificidad y fidelidad a la evidencia. Los nombres anteriores de Codex tampoco son una referencia humana externa.')

page();heading('7.1 Aportes y errores del nombrado')
table(['Grupo','Etiqueta automática','Propuesta de Gemini / revisión'],[['T6','6_francos_mil_dinero_usted','Discusiones financieras sobre grandes rentas, francos y especulación. Describe un contenido reconocible.'],['T3','3_duque_señor_usted_duquesa','Fórmulas protocolarias breves dirigidas al señor duque. Reconoce una unidad de estilo, no un asunto único.'],['T10','10_dijo_levantó_lágrimas_oculta','Verbos de movimiento y dicción previos a intervenciones directas. Identifica la función narrativa.'],['T2','2_duquesa_duque_casa_años','Miseria y ruina moral del duque y la duquesa. Extiende un juicio moral a ella sin evidencia suficiente.'],['T11','11_parís_usted_pase_prohibida','La etiqueta geográfica es plausible; su justificación inventa una prescripción médica y convalecencia forzosa en 0683.']], [W*.09,W*.30,W*.61])
para('Gemini mejora la legibilidad: transforma secuencias de palabras en frases y reconoce fórmulas protocolarias, acotaciones y redundancias. En T6 señala correctamente la casi duplicación de dos ejemplos. T4 y T12 reciben nombres próximos a sus núcleos clínico y de intriga.')
para('También introduce afirmaciones sin apoyo. En T9 habla de mendicidad, aunque 0048 describe vestimenta pobre sin afirmar que la duquesa mendigue; atribuye guarniciones griegas a un pasaje que menciona regimientos escoceses y oficiales ingleses. En T13 sugiere un solo capítulo, pero el grupo completo aparece en cinco. Calificar como alta la coherencia de T3/T10 describe una unidad formal y no necesariamente temática.')
para('Las explicaciones no permiten identificar la causa del agrupamiento: BERTopic agrupa embeddings mediante UMAP/HDBSCAN y usa c-TF-IDF para describir después. Compartir nombres propios o vocabulario en los ejemplos no prueba que ese rasgo haya causado la asignación.')
heading('Conclusión del bonus',2)
para('La utilidad de Gemini fue editorial. No cambió grupos, cobertura ni outliers, y no se evaluó su capacidad de descubrir tópicos. Sus nombres son propuestas revisables: una frase más clara puede incluir una interpretación equivocada. Se mantienen por separado el resultado original, la comparación por tópico y las etiquetas editoriales revisadas en bonus_gemini.')
para('No se compara costo o velocidad con cifras inventadas: faltan consumo real y mediciones equivalentes. El uso manual sin API permite ejecutar la alternativa, pero no satisface literalmente el registro de tokens cuando la interfaz no lo proporciona. El prompt y la respuesta permiten auditar el caso, sin garantizar que otro envío produzca el mismo resultado.')

page();heading('8. Bibliografía y uso de IA')
refs=[
('1','About, E. (1918). Germana (T. Orts-Ramos, trad.). Biblioteca de La Nación. Edición digital de Project Gutenberg, eBook 29640 (publicación digital: 2009).','https://www.gutenberg.org/ebooks/29640'),
('2','Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. EMNLP-IJCNLP, 3982-3992.','https://doi.org/10.18653/v1/D19-1410'),
('3','Sentence Transformers. (s. f.). paraphrase-multilingual-MiniLM-L12-v2 [Ficha de modelo; revisión registrada en el proyecto].','https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'),
('4','Grootendorst, M. (s. f.). Hyperparameter tuning. Documentación de BERTopic.','https://maartengr.github.io/BERTopic/getting_started/parameter%20tuning/parametertuning.html'),
('5','UMAP developers. (s. f.). UMAP reproducibility. Documentación de umap-learn.','https://umap-learn.readthedocs.io/en/latest/reproducibility.html'),
('6','McInnes, L., Healy, J., & Astels, S. (2017). hdbscan: Hierarchical density based clustering. Journal of Open Source Software, 2(11), 205.','https://doi.org/10.21105/joss.00205'),
('7','Grootendorst, M. (2022). BERTopic: Neural topic modeling with a class-based TF-IDF procedure. arXiv.','https://doi.org/10.48550/arXiv.2203.05794'),
('8','Grootendorst, M. (s. f.). Vectorizers. Documentación de BERTopic. Lista española de stopwords: corpus de NLTK, copia exacta conservada en el proyecto.','https://maartengr.github.io/BERTopic/getting_started/vectorizers/vectorizers.html'),
('9','NLTK Project. (s. f.). Corpus readers y datos de stopwords.','https://www.nltk.org/howto/corpus.html'),
('10','Alvarez, R. (s. f.). BERT y BERTopic [Presentación de clase]. Diapositivas 45-54. Material proporcionado en la actividad.','')]
for n,ref,url in refs:
 text=f'[{n}] '+escape(ref)
 if url:text+=' <link href="'+escape(url)+'" color="#24678d">'+escape(url)+'</link>'
 para(text,'SmallR')
para('Fuentes web consultadas el 25 de octubre de 2026. Los valores numéricos del reporte se calculan a partir de los resultados locales, no de resúmenes de las fuentes.','SmallR')
heading('Declaración de uso de IA',2)
para('Se utilizó Codex (OpenAI) para discutir decisiones técnicas, implementar y depurar notebooks, proponer nombres iniciales, inspeccionar ejemplos, generar figuras y redactar el reporte. La versión exacta del modelo de Codex no quedó registrada. Se utilizó Gemini 3.1 Pro, según el modelo informado por el usuario, para proponer nombres y limitaciones a partir de términos y representantes. Su configuración y datos disponibles se documentan en la sección 7.','SmallR')
para('Codex también revisó la respuesta de Gemini: la revisión no es una anotación humana independiente ni una verdad de referencia. Se conservaron resultados originales, propuestas revisadas y evidencia de los cambios. Las decisiones y conclusiones deben ser comprendidas y asumidas por quien presenta la actividad. El código incluye revisiones del modelo, versiones y verificaciones de integridad. No se atribuye a una persona una validación que no se realizó.','SmallR')

page();heading('Anexo A. Representantes completos de A')
para('Tres documentos por tópico, devueltos por get_representative_docs. Se conserva su texto limpio completo, sin recortes; el corpus original permanece en germana.txt. El identificador remite a segmentos.csv. Las etiquetas son las del análisis principal anterior al bonus.','SmallR')
def add_examples(config):
    grouped={}
    for r in reps[config]:grouped.setdefault(int(r['topico']),[]).append(r)
    for topic,group in sorted(grouped.items()):
        heading(f'{config}{topic}. '+labels[config][str(topic)][0],2)
        for r in sorted(group,key=lambda r:int(r['orden'])):
            seg=segments[r['segmento_id']]
            story.append(Paragraph(escape(f"Ejemplo {r['orden']} · {r['segmento_id']} · capítulo {seg['capitulo']} · {seg['palabras']} palabras"),styles['ExampleR']))
            md.append(f"**Ejemplo {r['orden']} · {r['segmento_id']} · capítulo {seg['capitulo']} · {seg['palabras']} palabras**\n")
            para(r['texto'],'QuoteR',literal=True)
add_examples('A')
page();heading('Anexo B. Representantes de B y C')
para('B y C tienen las mismas asignaciones. C actualiza la representación con bigramas y conserva estos tres ejemplos por tópico de B; no se los presenta como una nueva selección independiente.','SmallR')
add_examples('B')
page();heading('Anexo C. Prompt completo para Gemini')
para('Se transcribe la instrucción utilizada. A continuación de este prompt se adjuntaron los términos y los 48 párrafos de A; esos párrafos están íntegros en el anexo A. El JSON exacto y la entrada combinada se conservan en bonus_gemini.','SmallR')
prompt=(BASE/'bonus_gemini/prompt_gemini.txt').read_text()
for block in prompt.strip().split('\n\n'):
    if block.startswith('FORMATO DE SALIDA'):
        page(); heading('Anexo C. Formato solicitado (continuación)')
    para(escape(block).replace('\n','<br/>'),'SmallR')
para('Archivos de auditoría: entrada_completa_gemini.txt, datos_topicos_A.json, respuesta_gemini_original.json, manifiesto_entrada.json, validacion_respuesta.json y comparacion_etiquetas.csv. La respuesta original completa se incluye en el proyecto; la sección 7 analiza sus aciertos y errores.','SmallR')

# Control de navegación y paginación.
class ReportDoc(SimpleDocTemplate):
    def afterFlowable(self,flowable):
        if isinstance(flowable,Paragraph) and flowable.style.name=='H1R':
            title=flowable.getPlainText();key='section_'+str(self.page)+'_'+str(len(title))
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(title,key,level=0,closed=False)

def footer(canvas,doc):
    canvas.saveState();canvas.setStrokeColor(colors.HexColor('#b8cbd8'));canvas.setLineWidth(.5)
    canvas.line(20*mm,17*mm,A4[0]-20*mm,17*mm)
    canvas.setFont('Vera',7.5);canvas.setFillColor(colors.HexColor('#455968'))
    canvas.drawString(20*mm,12*mm,'Germana | BERTopic | Actividad individual')
    canvas.drawRightString(A4[0]-20*mm,12*mm,str(doc.page))
    canvas.restoreState()

pdf=OUT/'reporte_bertopic_germana.pdf'
doc=ReportDoc(str(pdf),pagesize=A4,rightMargin=20*mm,leftMargin=20*mm,topMargin=19*mm,bottomMargin=23*mm,
 title='Tópicos de Germana con BERTopic',author='Actividad individual de procesamiento de lenguaje natural',
 subject='Corpus español, configuraciones, análisis y nombrado con Gemini',pageCompression=1)
if args.pdf:
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
md_text = '\n'.join(md)
md_text = md_text.split('## Anexo C.', 1)[0] + '## Anexo C. Prompt completo para Gemini\n\n' + \
    'La instrucción se conserva íntegra. Los datos enviados están en el anexo A y en `bonus_gemini/entrada_completa_gemini.txt`.\n\n```text\n' + prompt.rstrip() + '\n```\n'
(OUT/'reporte_bertopic_germana.md').write_text(md_text,encoding='utf-8')
print('Reporte editable generado: reporte_bertopic_germana.md')
if args.pdf:
    print(f'PDF exportado: {pdf.name}')
