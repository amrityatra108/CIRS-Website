import cv2,json
from pathlib import Path
from PIL import Image,ImageDraw
p=Path('temp-home-intro/reference');p.mkdir(exist_ok=True)
v=cv2.VideoCapture(r'C:\Users\YEP15\Downloads\start sample.mp4')
fps=v.get(cv2.CAP_PROP_FPS); n=int(v.get(cv2.CAP_PROP_FRAME_COUNT))
meta=dict(fps=fps,frames=n,duration=n/fps,width=int(v.get(3)),height=int(v.get(4)),codec=''.join(chr((int(v.get(cv2.CAP_PROP_FOURCC))>>8*i)&255) for i in range(4)))
frames=[]
for idx in range(n):
 ok,f=v.read()
 if not ok:break
 if idx%max(1,round(fps*.4))==0 or idx==n-1:
  im=Image.fromarray(cv2.cvtColor(f,cv2.COLOR_BGR2RGB)); im.thumbnail((480,230));frames.append((idx,im))
w=1440;h=((len(frames)+2)//3)*270
sheet=Image.new('RGB',(w,h),'#eee9de');d=ImageDraw.Draw(sheet)
for j,(idx,im) in enumerate(frames):
 x=(j%3)*480;y=(j//3)*270;sheet.paste(im,(x,y+25));d.text((x+8,y+5),f'{idx/fps:.2f}s / frame {idx}',fill='black')
sheet.save(p/'contact-sheet.jpg');(p/'metadata.json').write_text(json.dumps(meta,indent=2));print(meta)
v.release()
