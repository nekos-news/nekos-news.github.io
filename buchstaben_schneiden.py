#!/usr/bin/env python3
"""Schneidet bilder/logo_buchstaben.png in neun Einzelbuchstaben (bilder/buchstaben/0-8.png + lage.json).
Nähte per Kantenerkennung im Überlappungsbereich, schmale Reste per Öffnen entfernt. Braucht numpy (~/NekoTools/venv)."""
import os, subprocess, json, numpy as np
HIER=os.path.dirname(os.path.abspath(__file__)); B=os.path.join(HIER,'bilder')
W,H=330,280
img=np.frombuffer(subprocess.run(['ffmpeg','-loglevel','error','-i',os.path.join(B,'logo_buchstaben.png'),'-f','rawvideo','-pix_fmt','rgba','-'],capture_output=True).stdout,np.uint8).reshape(H,W,4).astype(float)
rgb=img[...,:3]; al=img[...,3]; mid=130; band=10
reihen=[(0,mid,[85,141,206,269]),(mid,H,[85,157,247])]
labels=-np.ones((H,W),int); idx=0
for (y0,y1,grenzen) in reihen:
    n=len(grenzen)+1; seams=[]
    for g in grenzen:
        xs=np.arange(g-band,g+band+1); best=[]
        for y in range(y0,y1):
            if al[y,g-band:g+band].max()<40: best.append(g); continue
            d=np.abs(rgb[y,xs+1]-rgb[y,xs-1]).sum(1); d=np.convolve(d,np.ones(3)/3,'same'); best.append(int(xs[np.argmax(d)]))
        best=np.array(best); seams.append(np.array([int(np.median(best[max(0,i-5):i+6])) for i in range(len(best))]))
    for k in range(n):
        for yi,y in enumerate(range(y0,y1)):
            xl=0 if k==0 else seams[k-1][yi]; xr=W if k==n-1 else seams[k][yi]; labels[y,xl:xr]=idx+k
    idx+=n
def morph(M,r,op):
    P=np.pad(M,r); out=np.ones_like(M,bool) if op=='min' else np.zeros_like(M,bool)
    for dy in range(2*r+1):
        for dx in range(2*r+1):
            s=P[dy:dy+M.shape[0],dx:dx+M.shape[1]]; out = out&s if op=='min' else out|s
    return out
info=[]
for i in range(9):
    m=(labels==i)&(al>40); o=morph(morph(m,5,'min'),5,'max')
    ys,xs=np.where(o); keep=np.zeros_like(o); st=[(ys[len(ys)//2],xs[len(xs)//2])]
    while st:
        y,x=st.pop()
        if 0<=y<H and 0<=x<W and o[y,x] and not keep[y,x]: keep[y,x]=True; st+=[(y+1,x),(y-1,x),(y,x+1),(y,x-1)]
    a2=np.where(keep&(labels==i),al,0); ys,xs=np.where(a2>8); x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
    out=img.copy(); out[...,3]=a2
    subprocess.run(['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgba','-s',f'{x1-x0}x{y1-y0}','-i','-',os.path.join(B,'buchstaben',f'{i}.png')],input=out[y0:y1,x0:x1].astype(np.uint8).tobytes(),check=True)
    info.append({'i':i,'x':int(x0),'y':int(y0),'w':int(x1-x0),'h':int(y1-y0)})
json.dump(info,open(os.path.join(B,'buchstaben','lage.json'),'w')); print(info)
