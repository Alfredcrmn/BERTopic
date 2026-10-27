"""Verifica integridad del material entregable; no entrena modelos ni genera PDF."""
from pathlib import Path
import csv
import hashlib
import json
import re
import nbformat
import numpy as np
import pandas as pd
BASE=Path(__file__).resolve().parent.parent
R=BASE/'resultados'
s=pd.read_csv(R/'segmentos.csv')
a=pd.read_csv(R/'configuraciones/asignaciones.csv')
e=np.load(R/'embeddings_minilm.npy')
assert len(s)==len(a)==1177 and s.segmento_id.is_unique
assert s.segmento_id.tolist()==a.segmento_id.tolist()
assert e.shape==(1177,384) and np.isfinite(e).all()
assert np.allclose(np.linalg.norm(e,axis=1),1,atol=1e-5)
assert a.topico_B.equals(a.topico_C)
expected={'A':(16,235),'B':(5,251),'C':(5,251)}
for c,(n,outliers) in expected.items():
    t=pd.read_csv(R/f'configuraciones/{c}/topic_info.csv')
    assert t.Count.sum()==1177 and (t.Topic>=0).sum()==n
    assert int(t.loc[t.Topic==-1,'Count'].iloc[0])==outliers
    reps=pd.read_csv(R/f'configuraciones/{c}/ejemplos_representativos.csv')
    assert (reps.groupby('topico').size()==3).all()
    check=reps.merge(a[['segmento_id',f'topico_{c}']],on='segmento_id',validate='many_to_one')
    assert len(check)==3*n and (check.topico==check[f'topico_{c}']).all()
for p in BASE.glob('*.ipynb'):
    nb=nbformat.read(p,as_version=4);nbformat.validate(nb)
    assert all(c.execution_count is not None for c in nb.cells if c.cell_type=='code')
meta=json.loads((R/'resumen_preparacion.json').read_text())
assert hashlib.sha256((BASE/'germana.txt').read_text(encoding='utf-8-sig').encode()).hexdigest()==meta['corpus_sha256']
manifest=json.loads((BASE/'bonus_gemini/manifiesto_entrada.json').read_text())
for path,expected_hash in manifest['archivos_fuente'].items():
    assert hashlib.sha256((BASE/path).read_bytes()).hexdigest()==expected_hash
source=json.loads((BASE/'bonus_gemini/datos_topicos_A.json').read_text())['topicos_bertopic']
response=json.loads((BASE/'bonus_gemini/respuesta_gemini_original.json').read_text())['topicos']
assert [x['topic_id'] for x in response]==list(range(16))
for sent,received in zip(source,response):
    assert set(received['evidencia_ids'])<={e['segmento_id'] for e in sent['ejemplos']}
report=BASE/'reporte/reporte_bertopic_germana.md'
text=report.read_text()
assert '[Link al repo]' in text
assert (BASE/'bonus_gemini/prompt_gemini.txt').read_text().strip() in text
for path in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',text):
    assert (report.parent/path).is_file(),path
assert len(re.findall(r'!\[',text))==5
for c in 'ABC':
    for name in ['barchart','jerarquia']:
        p=R/f'configuraciones/{c}/{name}.html'
        assert '../plotly.min.js' in p.read_text()
        assert (p.parent/'../plotly.min.js').resolve().is_file()
print('Entrega verificada: corpus, embeddings, tres configuraciones, notebooks, bonus, cinco figuras y reporte editable.')
print('Exportación a PDF pendiente de revisión manual.')
