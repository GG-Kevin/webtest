from PIL import Image
import sys
def bands(path):
    img=Image.open(path).convert("RGB"); px=img.load(); w,h=img.size; bg=px[2,2]
    rows=[]
    for y in range(h):
        c=0
        for x in range(0,w,2):
            p=px[x,y]
            if abs(p[0]-bg[0])+abs(p[1]-bg[1])+abs(p[2]-bg[2])>40: c+=1
        rows.append(c>2)
    out=[];y=0
    while y<h:
        if rows[y]:
            s=y
            while y<h and rows[y]: y+=1
            out.append((s,y-1,y-s))
        else: y+=1
    return out
for p in sys.argv[1:]:
    print(p)
    for b in bands(p): print("   y%4d-%4d  h=%3d"%b)
