# Bonus: nombrado de tópicos de BERTopic con Gemini

## Procedimiento y alcance

Se utilizó Gemini 3.1 Pro, según el modelo reportado por el usuario, mediante un chat y sin API. Se enviaron los 16 grupos de A con diez términos por grupo y tres representantes completos: 48 párrafos. No se revelaron los nombres interpretativos previos. Se excluyeron los 235 outliers, que conservan la etiqueta -1. Gemini no agrupó ni reasignó documentos.

La respuesta proporcionada por el usuario se conserva en [respuesta_gemini_original.json](respuesta_gemini_original.json); se retira únicamente la envoltura Markdown del mensaje, conservando el contenido del JSON. El prompt y todos los datos están en [entrada_completa_gemini.txt](entrada_completa_gemini.txt). No se ha verificado desde este entorno la configuración de la conversación externa ni su historial.

## Validación de formato

Se recibieron exactamente los tópicos 0–15, sin duplicados; los 16 nombres tienen entre 3 y 10 palabras. Las 48 referencias corresponden a los ejemplos del tópico indicado. La estructura JSON cumple el esquema solicitado. Esto comprueba trazabilidad y formato, no corrección de las interpretaciones.

Gemini declaró coherencia alta en 10 grupos, media en 5 y baja en 1. Es una valoración del propio modelo sobre tres representantes; no es una métrica de coherencia independiente ni una precisión del sistema.

## Comparación de etiquetas

Las etiquetas automáticas concatenan palabras de c-TF-IDF. Gemini las transforma en frases y explicaciones. Para valorar ese cambio se revisó fidelidad a los ejemplos, especificidad, reconocimiento de heterogeneidad y afirmaciones sin evidencia. No se asignaron puntuaciones numéricas de calidad ni se trataron los nombres anteriores de Codex como verdad de referencia.

| ID | Etiqueta automática BERTopic | Nombre original de Gemini | Revisión cualitativa asistida |
|---|---|---|---|
| 0 | 0_usted_si_bien_señora | Fórmula de cortesía en intensos conflictos familiares y morales | Con reservas |
| 1 | 1_chermidy_señora_mujer_hijo | Triángulo amoroso entre Don Diego, Germana y señora Chermidy | Útil con ajuste |
| 2 | 2_duquesa_duque_casa_años | Miseria y ruina moral del duque y la duquesa | Revisar |
| 3 | 3_duque_señor_usted_duquesa | Fórmulas protocolarias breves dirigidas al señor duque | Útil con reservas |
| 4 | 4_bris_doctor_señor_germana | Tratamiento médico clínico para la enfermedad pulmonar de Germana | Útil |
| 5 | 5_doctor_usted_dijo_médico | Diálogos e interacciones directas con el personaje del doctor | Útil con ajuste |
| 6 | 6_francos_mil_dinero_usted | Discusiones financieras sobre grandes rentas, francos y especulación | Útil |
| 7 | 7_cama_balcón_paso_duque | Escenas espaciales nocturnas y febriles en habitaciones y balcones | Útil con reservas |
| 8 | 8_germana_corazón_alegría_vida | Descripciones psicológicas y estados emocionales íntimos de las mujeres | Útil con reservas |
| 9 | 9_jardín_cabeza_casa_gran | Estilo descriptivo costumbrista sobre indumentaria y entornos urbanos | Revisar justificación |
| 10 | 10_dijo_levantó_lágrimas_oculta | Verbos de movimiento y dicción previos a intervenciones directas | Útil con reservas |
| 11 | 11_parís_usted_pase_prohibida | Menciones geográficas y restricciones de residencia asociadas a París | Revisar |
| 12 | 12_veneno_venenos_pulmón_arsénico | Complot de asesinato y disertaciones toxicológicas sobre el arsénico | Útil con ajuste |
| 13 | 13_ly_gu_misioneros_tcheou | Relato histórico retrospectivo sobre el conflicto diplomático en China | Útil con ajuste |
| 14 | 14_chermidy_señora_doctor_mantoux | Intrigas y complots entre la señora Chermidy y Mateo Mantoux | Útil con reservas |
| 15 | 15_mar_ciudad_noche_allí | Descripciones paisajísticas de viajes marítimos y ruinas en Pompeya | Útil con ajuste |

## Evidencia y correcciones por tópico

Las propuestas siguientes son una revisión editorial separada. No reemplazan ni alteran el resultado original de Gemini.

### T0

Identifica cortesía y conflicto, pero coherencia alta confunde unidad de estilo con unidad temática. Tres discursos largos no representan necesariamente los 331 documentos.

**Etiqueta revisada propuesta:** Diálogos de afecto, reproche y negociación.

**Ejemplos disponibles para contrastar:** germana_0886 | germana_0980 | germana_0752.

### T1

Reconoce el conflicto afectivo, pero el triángulo amoroso deja en segundo plano la legitimidad del hijo y la herencia, centrales en los ejemplos 0134 y 0282.

**Etiqueta revisada propuesta:** Chermidy, maternidad y legitimidad de los Villanera.

**Ejemplos disponibles para contrastar:** germana_0134 | germana_0649 | germana_0282.

### T2

El nombre atribuye ruina moral a ambos cónyuges. Los ejemplos contraponen las privaciones de la duquesa y el derroche del duque; no sustentan igual juicio moral sobre ella.

**Etiqueta revisada propuesta:** Pobreza familiar y derroche del duque.

**Ejemplos disponibles para contrastar:** germana_0385 | germana_0061 | germana_0291.

### T3

Describe correctamente un tratamiento protocolario. La coherencia de esa fórmula no demuestra un tema homogéneo; debe distinguirse de coherencia argumental.

**Etiqueta revisada propuesta:** Fórmulas de cortesía dirigidas al duque.

**Ejemplos disponibles para contrastar:** germana_0279 | germana_0151 | germana_0308.

### T4

El nombre especifica enfermedad pulmonar y tratamiento, apoyados en los ejemplos. Se refiere al contenido de ficción, sin validar la medicina descrita.

**Etiqueta revisada propuesta:** Enfermedad pulmonar de Germana y cuidados médicos.

**Ejemplos disponibles para contrastar:** germana_0763 | germana_0705 | germana_0707.

### T5

Identifica al interlocutor y la diversidad de asuntos. El ejemplo 0096 es narración de una reacción al doctor, no una intervención directa citada.

**Etiqueta revisada propuesta:** Conversaciones y reacciones ante el doctor.

**Ejemplos disponibles para contrastar:** germana_0260 | germana_0084 | germana_0096.

### T6

El nombre económico es fiel y advierte correctamente los ejemplos casi duplicados 0160 y 0075. Esa redundancia limita la evaluación, no invalida por sí sola el tópico.

**Etiqueta revisada propuesta:** Dinero, rentas y especulación.

**Ejemplos disponibles para contrastar:** germana_0160 | germana_0075 | germana_0443.

### T7

Vincula alcobas y estados alterados sin ocultar que son episodios diferentes. Expresiones como letargo místico resultan más interpretativas que el sueño descrito.

**Etiqueta revisada propuesta:** Escenas de alcoba, angustia y muerte.

**Ejemplos disponibles para contrastar:** germana_1118 | germana_1119 | germana_0331.

### T8

Los representantes muestran tres figuras femeninas, pero el grupo completo también incluye reacciones de don Diego, como 0971. No conviene limitar todo el tópico a mujeres.

**Etiqueta revisada propuesta:** Retratos psicológicos y vida afectiva.

**Ejemplos disponibles para contrastar:** germana_0380 | germana_0695 | germana_0200.

### T9

La duquesa aparece pobremente vestida, pero 0048 no afirma que mendigue. En 0708 se describen regimientos escoceses y oficiales ingleses; guarniciones griegas es una atribución imprecisa.

**Etiqueta revisada propuesta:** Descripciones de indumentaria y entornos urbanos.

**Ejemplos disponibles para contrastar:** germana_0708 | germana_0462 | germana_0048.

### T10

Reconoce una función narrativa real. Coherencia alta aquí es estructural y no temática; algunas comillas de sus ejemplos sintéticos no son citas literales de las expresiones originales.

**Etiqueta revisada propuesta:** Gestos y acotaciones previos al diálogo.

**Ejemplos disponibles para contrastar:** germana_0393 | germana_0405 | germana_0325.

### T11

0683 invita al médico a volver a París cuando termine su tarea y habla de su clientela. No contiene una prescripción médica ni planes de convalecencia forzosa. La etiqueta geográfica sí es compatible con los datos.

**Etiqueta revisada propuesta:** París: residencia y desplazamientos.

**Ejemplos disponibles para contrastar:** germana_0553 | germana_0001 | germana_0683.

### T12

Identifica venenos e intriga. El arsénico es importante, pero los ejemplos incluyen otros tóxicos; no conviene reducir el tema a una sustancia ni tratar como hechos extraliterarios los intentos narrados.

**Etiqueta revisada propuesta:** Venenos e intriga de envenenamiento.

**Ejemplos disponibles para contrastar:** germana_0598 | germana_0702 | germana_0600.

### T13

El episodio naval está sustentado, pero llamarlo histórico puede sugerir verificación externa que no se hizo. La hipótesis de un solo capítulo no describe todos los documentos: A13 aparece en capítulos 6, 7, 9, 10 y 14.

**Etiqueta revisada propuesta:** Cartas de China y conflicto de la Náyade.

**Ejemplos disponibles para contrastar:** germana_0674 | germana_0692 | germana_0673.

### T14

El nombre reconoce la intriga, pero alta coherencia contrasta con la limitación unidos sólo por nombres propios. 0242 es reflexión de Chermidy y no una coordinación explícita con Mantoux.

**Etiqueta revisada propuesta:** Intrigas de Chermidy, Mantoux y le Tas.

**Ejemplos disponibles para contrastar:** germana_0242 | germana_1051 | germana_0596.

### T15

Los ejemplos sostienen paisajes y Pompeya. Viajes marítimos puede dar excesivo peso al bote de 0696, y escalofriante no corresponde al tono dulce y solemne de 0357.

**Etiqueta revisada propuesta:** Paisajes mediterráneos, paseos y ruinas de Pompeya.

**Ejemplos disponibles para contrastar:** germana_0696 | germana_0357 | germana_0358.

## Resultados e interpretación

La principal mejora observable es la legibilidad de las etiquetas: una lista como francos, mil, dinero, usted se convierte en una descripción financiera comprensible (T6). T4 identifica los cuidados pulmonares y T12 la intriga de venenos. T3 y T10 explicitan que algunos grupos tienen unidad de protocolo o de función narrativa, no un asunto literario único. Gemini también reconoce la casi duplicación de dos representantes de T6.

La legibilidad no asegura fidelidad. En T2 el nombre extiende un juicio moral a la duquesa que los ejemplos no sostienen. En T9 aparecen mendicidad y guarniciones griegas como interpretaciones imprecisas. En T11 se introducen prescripción médica y convalecencia forzosa sin apoyo en 0683. Esos errores muestran por qué se debe cotejar la explicación contra el texto original.

La coherencia alta de T3/T10 puede describir similitud estilística, sin implicar unidad temática. En T14 la calificación alta contrasta con una limitación que atribuye la unión sólo a nombres propios. No se debe convertir esta autoevaluación en una medida del éxito de BERTopic. Tampoco puede inferirse qué rasgo causó el agrupamiento a partir de estas explicaciones: los grupos se calcularon con embeddings y UMAP/HDBSCAN; c-TF-IDF describe esos grupos después.

En T13, los tres representantes enviados pertenecen al episodio de China, pero el tópico completo aparece en cinco capítulos. La hipótesis de Gemini sobre un único capítulo es una inferencia limitada, no una propiedad comprobada del grupo. No es necesario que un tema sea transversal a toda la novela para ser válido.

La comparación se limita a una respuesta con un prompt y una selección de representantes. No se midió estabilidad entre ejecuciones, calidad con anotadores independientes ni desempeño de Gemini descubriendo tópicos. Ni el número de grupos, ni la cobertura, ni los outliers cambiaron: cualquier diferencia corresponde a representación e interpretación.

## Recursos, reproducibilidad y datos pendientes

| Dato | Registro |
|---|---|
| Modelo visible | Gemini 3.1 Pro, reportado por el usuario; versión interna no disponible |
| Hora de ejecución | 18:35 (6:35 p. m.), reportada por el usuario; zona del contexto: America/Mexico_City |
| Fecha de ejecución | No proporcionada explícitamente |
| Thinking level | low, reportado por el usuario |
| Acceso gratuito o suscripción | Suscripción Plus, denominación reportada por el usuario |
| Tokens reales de entrada/salida | No disponibles en la evidencia recibida |
| Costo adicional observado | No proporcionado; no se asume gratuidad ni se estima un precio por tokens |
| Límite de gasto de API | No aplica: procedimiento manual sin API |
| Tiempo de respuesta y reintentos | No proporcionados |
| Reproducibilidad | Prompt, datos, respuesta, hash y validación conservados; no se garantiza igual salida futura |

No se presenta una comparación numérica de costo o velocidad con BERTopic porque faltan mediciones comparables. No se inventa consumo de tokens. Se documenta como limitación frente al requisito de la consigna. Puede completarse el registro si el usuario conserva datos observables de la ejecución.

## Conclusión para el reporte

El uso de Gemini como apoyo al nombrado volvió más comprensibles varios grupos de BERTopic, especialmente los de contenido financiero, clínico y de intriga. También ayudó a reconocer grupos de estilo narrativo. Su utilidad fue editorial: no mejoró ni evaluó independientemente el agrupamiento. Las sobreinterpretaciones y errores detectados justifican conservar las propuestas originales y realizar una revisión textual antes de adoptar las etiquetas. En este experimento conviene usar sus nombres como propuestas revisables y no como validación automática de los tópicos.

## Declaración de uso de IA

Gemini 3.1 Pro se utilizó para proponer nombres, justificaciones y limitaciones a partir de datos preparados con Codex. Codex (OpenAI) se utilizó también para validar el JSON, contrastar sus afirmaciones y redactar esta comparación. La revisión es asistida por otro modelo, no una evaluación humana independiente; corresponde al autor de la actividad revisar y asumir las conclusiones. El prompt completo, los datos y la respuesta se conservan junto al código. El usuario reportó ejecución a las 18:35, thinking level low y suscripción Plus. La fecha de ejecución no se proporcionó explícitamente; el consumo de tokens y el costo adicional siguen sin documentarse. La denominación de la suscripción se conserva tal como fue reportada.

Fuentes del análisis: archivos locales de la configuración A, representantes enviados a Gemini y respuesta original proporcionada por el usuario. No se empleó búsqueda externa para completar la interpretación de la novela.
