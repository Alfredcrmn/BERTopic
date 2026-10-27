"""Valida la respuesta preservada y genera una comparación crítica, sin llamadas a API."""
from pathlib import Path
from collections import Counter
import ast
import csv
import hashlib
import json

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
# Revisión cualitativa asistida por Codex. No es anotación humana independiente.
REVISION = {
0: ('Con reservas', 'Identifica cortesía y conflicto, pero coherencia alta confunde unidad de estilo con unidad temática. Tres discursos largos no representan necesariamente los 331 documentos.', 'Diálogos de afecto, reproche y negociación'),
1: ('Útil con ajuste', 'Reconoce el conflicto afectivo, pero el triángulo amoroso deja en segundo plano la legitimidad del hijo y la herencia, centrales en los ejemplos 0134 y 0282.', 'Chermidy, maternidad y legitimidad de los Villanera'),
2: ('Revisar', 'El nombre atribuye ruina moral a ambos cónyuges. Los ejemplos contraponen las privaciones de la duquesa y el derroche del duque; no sustentan igual juicio moral sobre ella.', 'Pobreza familiar y derroche del duque'),
3: ('Útil con reservas', 'Describe correctamente un tratamiento protocolario. La coherencia de esa fórmula no demuestra un tema homogéneo; debe distinguirse de coherencia argumental.', 'Fórmulas de cortesía dirigidas al duque'),
4: ('Útil', 'El nombre especifica enfermedad pulmonar y tratamiento, apoyados en los ejemplos. Se refiere al contenido de ficción, sin validar la medicina descrita.', 'Enfermedad pulmonar de Germana y cuidados médicos'),
5: ('Útil con ajuste', 'Identifica al interlocutor y la diversidad de asuntos. El ejemplo 0096 es narración de una reacción al doctor, no una intervención directa citada.', 'Conversaciones y reacciones ante el doctor'),
6: ('Útil', 'El nombre económico es fiel y advierte correctamente los ejemplos casi duplicados 0160 y 0075. Esa redundancia limita la evaluación, no invalida por sí sola el tópico.', 'Dinero, rentas y especulación'),
7: ('Útil con reservas', 'Vincula alcobas y estados alterados sin ocultar que son episodios diferentes. Expresiones como letargo místico resultan más interpretativas que el sueño descrito.', 'Escenas de alcoba, angustia y muerte'),
8: ('Útil con reservas', 'Los representantes muestran tres figuras femeninas, pero el grupo completo también incluye reacciones de don Diego, como 0971. No conviene limitar todo el tópico a mujeres.', 'Retratos psicológicos y vida afectiva'),
9: ('Revisar justificación', 'La duquesa aparece pobremente vestida, pero 0048 no afirma que mendigue. En 0708 se describen regimientos escoceses y oficiales ingleses; guarniciones griegas es una atribución imprecisa.', 'Descripciones de indumentaria y entornos urbanos'),
10: ('Útil con reservas', 'Reconoce una función narrativa real. Coherencia alta aquí es estructural y no temática; algunas comillas de sus ejemplos sintéticos no son citas literales de las expresiones originales.', 'Gestos y acotaciones previos al diálogo'),
11: ('Revisar', '0683 invita al médico a volver a París cuando termine su tarea y habla de su clientela. No contiene una prescripción médica ni planes de convalecencia forzosa. La etiqueta geográfica sí es compatible con los datos.', 'París: residencia y desplazamientos'),
12: ('Útil con ajuste', 'Identifica venenos e intriga. El arsénico es importante, pero los ejemplos incluyen otros tóxicos; no conviene reducir el tema a una sustancia ni tratar como hechos extraliterarios los intentos narrados.', 'Venenos e intriga de envenenamiento'),
13: ('Útil con ajuste', 'El episodio naval está sustentado, pero llamarlo histórico puede sugerir verificación externa que no se hizo. La hipótesis de un solo capítulo no describe todos los documentos: A13 aparece en capítulos 6, 7, 9, 10 y 14.', 'Cartas de China y conflicto de la Náyade'),
14: ('Útil con reservas', 'El nombre reconoce la intriga, pero alta coherencia contrasta con la limitación unidos sólo por nombres propios. 0242 es reflexión de Chermidy y no una coordinación explícita con Mantoux.', 'Intrigas de Chermidy, Mantoux y le Tas'),
15: ('Útil con ajuste', 'Los ejemplos sostienen paisajes y Pompeya. Viajes marítimos puede dar excesivo peso al bote de 0696, y escalofriante no corresponde al tono dulce y solemne de 0357.', 'Paisajes mediterráneos, paseos y ruinas de Pompeya'),
}

def read_csv(path):
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))

def write_csv(path, rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)

response_path=HERE/'respuesta_gemini_original.json'
response=json.loads(response_path.read_text())
payload=json.loads((HERE/'datos_topicos_A.json').read_text())['topicos_bertopic']
source={t['topic_id']:t for t in payload}
automatic={int(r['Topic']):r for r in read_csv(BASE/'resultados/configuraciones/A/topic_info.csv')}
prior={int(r['Topic']):r for r in read_csv(BASE/'resultados/analisis/topicos_A_nombrados.csv')}
assert set(response)=={'topicos','observaciones_generales'}
assert [t['topic_id'] for t in response['topicos']]==list(range(16))
required={'topic_id','nombre','justificacion','evidencia_ids','coherencia_observada','limitacion'}
rows=[]; cited=[]
for item in response['topicos']:
    assert set(item)==required
    t=item['topic_id']; data=source[t]
    assert item['coherencia_observada'] in {'alta','media','baja'}
    assert all(isinstance(item[k],str) and item[k].strip() for k in ['nombre','justificacion','limitacion'])
    assert 3<=len(item['nombre'].split())<=10
    allowed={e['segmento_id'] for e in data['ejemplos']}
    assert 1<=len(item['evidencia_ids'])<=3
    assert len(set(item['evidencia_ids']))==len(item['evidencia_ids'])
    assert set(item['evidencia_ids'])<=allowed
    cited.extend(item['evidencia_ids'])
    assessment,comment,revised=REVISION[t]
    rows.append({'topic_id':t,'numero_documentos':data['numero_documentos'],
        'etiqueta_automatica_bertopic':automatic[t]['Name'],
        'terminos_bertopic':' | '.join(data['terminos_representativos']),
        'nombre_gemini_original':item['nombre'],'justificacion_gemini':item['justificacion'],
        'evidencia_ids':' | '.join(item['evidencia_ids']),
        'coherencia_declarada_gemini':item['coherencia_observada'],
        'limitacion_declarada_gemini':item['limitacion'],
        'revision_cualitativa_codex':assessment,'observacion_revision':comment,
        'etiqueta_editorial_revisada':revised,
        'nombre_previo_asistido_codex':prior[t]['Nombre_propio']})
write_csv(HERE/'comparacion_etiquetas.csv',rows)
write_csv(HERE/'etiquetas_revisadas.csv',[{'topic_id':r['topic_id'],
    'numero_documentos':r['numero_documentos'], 'nombre_revisado':r['etiqueta_editorial_revisada'],
    'procedencia':'Revisión editorial asistida por Codex de propuestas Gemini; no evaluación humana independiente'} for r in rows])
counts=Counter(t['coherencia_observada'] for t in response['topicos'])
validation={'estado':'validación estructural superada', 'topicos':len(rows),
    'referencias_de_evidencia_validas':len(cited),'referencias_unicas':len(set(cited)),
    'nombres_entre_3_y_10_palabras':True,'coherencia_declarada_por_gemini':dict(counts),
    'modelo_reportado_por_usuario':'Gemini 3.1 Pro',
    'version_interna':'no disponible','fecha_ejecucion':'no proporcionada',
    'hora_ejecucion_reportada':'18:35', 'zona_horaria_contexto':'America/Mexico_City',
    'thinking_level_reportado':'low',
    'tipo_acceso':'Suscripción Plus, según lo reportado por el usuario', 'tokens_reales':'no disponibles',
    'costo_observado':'no proporcionado',
    'cambios_a_asignaciones':False,'respuesta_sha256':hashlib.sha256(response_path.read_bytes()).hexdigest(),
    'alcance':'El formato y los IDs válidos no prueban fidelidad semántica ni coherencia de los grupos.'}
(HERE/'validacion_respuesta.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')

lines=['# Bonus: nombrado de tópicos de BERTopic con Gemini','',
'## Procedimiento y alcance','',
'Se utilizó Gemini 3.1 Pro, según el modelo reportado por el usuario, mediante un chat y sin API. Se enviaron los 16 grupos de A con diez términos por grupo y tres representantes completos: 48 párrafos. No se revelaron los nombres interpretativos previos. Se excluyeron los 235 outliers, que conservan la etiqueta -1. Gemini no agrupó ni reasignó documentos.', '',
'La respuesta proporcionada por el usuario se conserva en [respuesta_gemini_original.json](respuesta_gemini_original.json); se retira únicamente la envoltura Markdown del mensaje, conservando el contenido del JSON. El prompt y todos los datos están en [entrada_completa_gemini.txt](entrada_completa_gemini.txt). No se ha verificado desde este entorno la configuración de la conversación externa ni su historial.', '',
'## Validación de formato','',
'Se recibieron exactamente los tópicos 0–15, sin duplicados; los 16 nombres tienen entre 3 y 10 palabras. Las 48 referencias corresponden a los ejemplos del tópico indicado. La estructura JSON cumple el esquema solicitado. Esto comprueba trazabilidad y formato, no corrección de las interpretaciones.', '',
f'Gemini declaró coherencia alta en {counts["alta"]} grupos, media en {counts["media"]} y baja en {counts["baja"]}. Es una valoración del propio modelo sobre tres representantes; no es una métrica de coherencia independiente ni una precisión del sistema.', '',
'## Comparación de etiquetas','',
'Las etiquetas automáticas concatenan palabras de c-TF-IDF. Gemini las transforma en frases y explicaciones. Para valorar ese cambio se revisó fidelidad a los ejemplos, especificidad, reconocimiento de heterogeneidad y afirmaciones sin evidencia. No se asignaron puntuaciones numéricas de calidad ni se trataron los nombres anteriores de Codex como verdad de referencia.', '',
'| ID | Etiqueta automática BERTopic | Nombre original de Gemini | Revisión cualitativa asistida |',
'|---|---|---|---|']
for r in rows:
    lines.append(f'| {r["topic_id"]} | {r["etiqueta_automatica_bertopic"]} | {r["nombre_gemini_original"]} | {r["revision_cualitativa_codex"]} |')
lines+=['','## Evidencia y correcciones por tópico','',
'Las propuestas siguientes son una revisión editorial separada. No reemplazan ni alteran el resultado original de Gemini.']
for r in rows:
    lines+=['',f'### T{r["topic_id"]}', '',r['observacion_revision'],'',
        f'**Etiqueta revisada propuesta:** {r["etiqueta_editorial_revisada"]}.', '',
        f'**Ejemplos disponibles para contrastar:** {r["evidencia_ids"]}.']
lines+=['','## Resultados e interpretación','',
'La principal mejora observable es la legibilidad de las etiquetas: una lista como francos, mil, dinero, usted se convierte en una descripción financiera comprensible (T6). T4 identifica los cuidados pulmonares y T12 la intriga de venenos. T3 y T10 explicitan que algunos grupos tienen unidad de protocolo o de función narrativa, no un asunto literario único. Gemini también reconoce la casi duplicación de dos representantes de T6.', '',
'La legibilidad no asegura fidelidad. En T2 el nombre extiende un juicio moral a la duquesa que los ejemplos no sostienen. En T9 aparecen mendicidad y guarniciones griegas como interpretaciones imprecisas. En T11 se introducen prescripción médica y convalecencia forzosa sin apoyo en 0683. Esos errores muestran por qué se debe cotejar la explicación contra el texto original.', '',
'La coherencia alta de T3/T10 puede describir similitud estilística, sin implicar unidad temática. En T14 la calificación alta contrasta con una limitación que atribuye la unión sólo a nombres propios. No se debe convertir esta autoevaluación en una medida del éxito de BERTopic. Tampoco puede inferirse qué rasgo causó el agrupamiento a partir de estas explicaciones: los grupos se calcularon con embeddings y UMAP/HDBSCAN; c-TF-IDF describe esos grupos después.', '',
'En T13, los tres representantes enviados pertenecen al episodio de China, pero el tópico completo aparece en cinco capítulos. La hipótesis de Gemini sobre un único capítulo es una inferencia limitada, no una propiedad comprobada del grupo. No es necesario que un tema sea transversal a toda la novela para ser válido.', '',
'La comparación se limita a una respuesta con un prompt y una selección de representantes. No se midió estabilidad entre ejecuciones, calidad con anotadores independientes ni desempeño de Gemini descubriendo tópicos. Ni el número de grupos, ni la cobertura, ni los outliers cambiaron: cualquier diferencia corresponde a representación e interpretación.', '',
'## Recursos, reproducibilidad y datos pendientes','',
'| Dato | Registro |','|---|---|',
'| Modelo visible | Gemini 3.1 Pro, reportado por el usuario; versión interna no disponible |',
'| Hora de ejecución | 18:35 (6:35 p. m.), reportada por el usuario; zona del contexto: America/Mexico_City |',
'| Fecha de ejecución | No proporcionada explícitamente |',
'| Thinking level | low, reportado por el usuario |',
'| Acceso gratuito o suscripción | Suscripción Plus, denominación reportada por el usuario |',
'| Tokens reales de entrada/salida | No disponibles en la evidencia recibida |',
'| Costo adicional observado | No proporcionado; no se asume gratuidad ni se estima un precio por tokens |',
'| Límite de gasto de API | No aplica: procedimiento manual sin API |',
'| Tiempo de respuesta y reintentos | No proporcionados |',
'| Reproducibilidad | Prompt, datos, respuesta, hash y validación conservados; no se garantiza igual salida futura |', '',
'No se presenta una comparación numérica de costo o velocidad con BERTopic porque faltan mediciones comparables. No se inventa consumo de tokens. Se documenta como limitación frente al requisito de la consigna. Puede completarse el registro si el usuario conserva datos observables de la ejecución.', '',
'## Conclusión para el reporte','',
'El uso de Gemini como apoyo al nombrado volvió más comprensibles varios grupos de BERTopic, especialmente los de contenido financiero, clínico y de intriga. También ayudó a reconocer grupos de estilo narrativo. Su utilidad fue editorial: no mejoró ni evaluó independientemente el agrupamiento. Las sobreinterpretaciones y errores detectados justifican conservar las propuestas originales y realizar una revisión textual antes de adoptar las etiquetas. En este experimento conviene usar sus nombres como propuestas revisables y no como validación automática de los tópicos.', '',
'## Declaración de uso de IA','',
'Gemini 3.1 Pro se utilizó para proponer nombres, justificaciones y limitaciones a partir de datos preparados con Codex. Codex (OpenAI) se utilizó también para validar el JSON, contrastar sus afirmaciones y redactar esta comparación. La revisión es asistida por otro modelo, no una evaluación humana independiente; corresponde al autor de la actividad revisar y asumir las conclusiones. El prompt completo, los datos y la respuesta se conservan junto al código. El usuario reportó ejecución a las 18:35, thinking level low y suscripción Plus. La fecha de ejecución no se proporcionó explícitamente; el consumo de tokens y el costo adicional siguen sin documentarse. La denominación de la suscripción se conserva tal como fue reportada.', '',
'Fuentes del análisis: archivos locales de la configuración A, representantes enviados a Gemini y respuesta original proporcionada por el usuario. No se empleó búsqueda externa para completar la interpretación de la novela.']
(HERE/'analisis_bonus.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(validation,ensure_ascii=False,indent=2))
print('Comparación y revisión guardadas; respuesta original preservada.')
