"""Ejecuta notebooks con nbclient y el Python activo; no requiere registrar un kernel global."""
import argparse
import os
from pathlib import Path
import sys
import tempfile
import nbformat
from nbclient import NotebookClient

BASE = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument('etapas', nargs='*', choices=['01', '02', '03'])
args = parser.parse_args()
cache=BASE/'.cache'
for env,sub in [('MPLCONFIGDIR','matplotlib'),('HF_HOME','huggingface'),('NUMBA_CACHE_DIR','numba'),('IPYTHONDIR','ipython')]:
    os.environ.setdefault(env,str(cache/sub))
with tempfile.TemporaryDirectory() as tmp:
    kernels=Path(tmp)/'kernels'/'bertopic-local'
    kernels.mkdir(parents=True)
    import json
    (kernels/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],
                'display_name':'BERTopic local','language':'python'}))
    os.environ['JUPYTER_PATH']=tmp+os.pathsep+os.environ.get('JUPYTER_PATH','')
    for stage in args.etapas or ['01','02','03']:
        path=next(BASE.glob(stage+'_*.ipynb'))
        print(f'Ejecutando {path.name}',flush=True)
        nb=nbformat.read(path,as_version=4)
        client=NotebookClient(nb,timeout=1800,kernel_name='bertopic-local',resources={'metadata':{'path':str(BASE)}})
        client.execute()
        nbformat.write(nb,path)
        print('Completado',flush=True)
