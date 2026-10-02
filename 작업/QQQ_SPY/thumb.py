from PIL import Image,ImageDraw,ImageFont
F='/home/user/webtest/자산/폰트/Pretendard-'
f=lambda w,s:ImageFont.truetype(F+w+'.otf',s)
W=800;im=Image.new('RGB',(W,W),'#F3EEE3');d=ImageDraw.Draw(im)
L=64
d.text((L,70),'QQQ  vs  SPY',font=f('Bold',34),fill='#5B5346')
d.text((L,118),'매달 같은 돈을 넣었다면',font=f('Bold',44),fill='#1F2A24')
d.text((L,210),'QQQ',font=f('Bold',40),fill='#1E6B4F')
d.text((L-6,250),'12.50배',font=f('ExtraBold',168),fill='#1E6B4F')
# bars
y=470;full=W-2*L
d.rounded_rectangle((L,y,L+full,y+38),radius=6,fill='#1E6B4F')
d.rounded_rectangle((L,y+62,L+int(full*6.18/12.50),y+100),radius=6,fill='#B9AE98')
d.text((L+int(full*6.18/12.50)+18,y+60),'SPY 6.18배',font=f('Bold',36),fill='#5B5346')
d.line((L,640,W-L,640),fill='#CFC6B4',width=2)
d.text((L,662),'1999년 4월 ~ 2026년 10월 · 331회 적립',font=f('Regular',28),fill='#5B5346')
d.text((L,704),'배당 재투자 기준 · 넣은 돈 대비 배수',font=f('Regular',28),fill='#5B5346')
im.save('/home/user/webtest/발행/썸네일/26_QQQ_SPY.png')
