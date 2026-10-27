"""Genera figuras legibles a tamaño de página para el reporte, sin modificar modelos."""
from pathlib import Path
import ast
import os
BASE=Path(__file__).resolve().parent.parent
os.environ.setdefault('MPLCONFIGDIR',str(BASE/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.vectorizers import ClassTfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
OUT=BASE/'reporte/figuras'; OUT.mkdir(parents=True,exist_ok=True)
ROOT=BASE/'resultados'
a=pd.read_csv(ROOT/'configuraciones/asignaciones.csv')
d=pd.read_csv(ROOT/'segmentos.csv')
plt.rcParams.update({'font.size':9,'axes.titlesize':10,'axes.labelsize':9,'xtick.labelsize':8,'ytick.labelsize':9,'savefig.dpi':180})
joined=a.groupby('topico_A',sort=True).texto.apply(lambda x:' '.join(x)).str.replace('\n',' ',regex=False).str.replace('\t',' ',regex=False)
v=CountVectorizer(stop_words=(ROOT/'configuraciones/stopwords_es.txt').read_text().splitlines(),ngram_range=(1,1),min_df=1,strip_accents=None)
w=ClassTfidfTransformer().fit_transform(v.fit_transform(joined))
info=pd.read_csv(ROOT/'configuraciones/A/topic_info.csv').query('Topic >= 0').reset_index(drop=True)
for batch in range(2):
 fig,axes=plt.subplots(4,2,figsize=(7.0,7.5))
 for ax,(_,r) in zip(axes.flat,info.iloc[batch*8:batch*8+8].iterrows()):
  words=ast.literal_eval(r.Representation)[:5]
  weights=w[joined.index.get_loc(r.Topic)].toarray().ravel()
  ax.barh(words[::-1],[weights[v.vocabulary_[x]] for x in words[::-1]],color='#24678d')
  ax.set_title(f'T{r.Topic}  |  {r.Count} párrafos',loc='left')
  ax.tick_params(axis='y',labelsize=9)
  ax.tick_params(axis='x',labelsize=7)
  ax.set_xlabel('Peso c-TF-IDF',fontsize=8)
 fig.tight_layout(h_pad=1.2,w_pad=1.8)
 fig.savefig(OUT/f'palabras_A_{batch+1}.png');plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(7,3.0))
axes[0].hist(d.palabras,bins=30,color='#24678d',edgecolor='white')
axes[0].set(xlabel='Palabras por párrafo',ylabel='Segmentos',title='Longitud en palabras')
axes[1].hist(d.tokens_con_especiales,bins=30,color='#248675',edgecolor='white')
axes[1].axvline(128,color='#a43b42',ls='--',label='128 tokens')
axes[1].set(xlabel='Tokens con especiales',ylabel='Segmentos',title='Longitud con MiniLM');axes[1].legend(fontsize=8)
fig.tight_layout();fig.savefig(OUT/'longitudes.png');plt.close(fig)
fig,axes=plt.subplots(1,3,figsize=(7,4.5))
for ax,c in zip(axes,'ABC'):
 t=pd.read_csv(ROOT/f'configuraciones/{c}/topic_info.csv').sort_values('Topic')
 ax.barh(['-1' if i==-1 else f'T{i}' for i in t.Topic],t.Count,color=['#b55050' if i==-1 else '#24678d' for i in t.Topic])
 ax.invert_yaxis();ax.set_xlim(0,535);ax.set_title(f'Configuración {c}');ax.set_xlabel('Párrafos')
 ax.tick_params(axis='y',labelsize=8)
 for i,n in enumerate(t.Count): ax.text(n+5,i,str(n),va='center',fontsize=7)
fig.tight_layout(w_pad=1);fig.savefig(OUT/'distribucion.png');plt.close(fig)
e=np.load(ROOT/'embeddings_minilm.npy');ids=list(range(16))
sim=cosine_similarity(np.stack([e[a.topico_A.to_numpy()==i].mean(axis=0) for i in ids]))
fig,ax=plt.subplots(figsize=(6.5,5.5));im=ax.imshow(sim,vmin=0,vmax=1,cmap='YlGnBu')
ax.set_xticks(ids,[f'T{i}' for i in ids],fontsize=8);ax.set_yticks(ids,[f'T{i}' for i in ids],fontsize=8)
fig.colorbar(im,ax=ax,label='Similitud coseno',shrink=.9);fig.tight_layout();fig.savefig(OUT/'similitud.png');plt.close(fig)
print('Se generaron cinco figuras para impresión.')
