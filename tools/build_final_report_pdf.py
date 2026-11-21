from pathlib import Path
import re, html
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted, PageBreak, KeepTogether, CondPageBreak

root=Path(__file__).resolve().parents[1]
source=root/'docs/FINAL_PROJECT_REPORT.md'
out=root/'output/pdf/FINAL_PROJECT_REPORT.pdf'
out.parent.mkdir(parents=True,exist_ok=True)
lines=source.read_text(encoding='utf-8').splitlines()
NAVY=colors.HexColor('#184369'); BLUE=colors.HexColor('#2D6EA3'); TEXT=colors.HexColor('#26313D'); PALE=colors.HexColor('#EAF1F6'); GRID=colors.HexColor('#C5D2DE')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='ReportTitle',parent=styles['Title'],fontName='Helvetica-Bold',fontSize=21,leading=25,textColor=NAVY,alignment=TA_LEFT,spaceAfter=16))
styles.add(ParagraphStyle(name='Section',parent=styles['Heading1'],fontName='Helvetica-Bold',fontSize=15,leading=18,textColor=NAVY,spaceBefore=12,spaceAfter=6,keepWithNext=True))
styles.add(ParagraphStyle(name='Subsection',parent=styles['Heading2'],fontName='Helvetica-Bold',fontSize=11.5,leading=14,textColor=BLUE,spaceBefore=8,spaceAfter=4,keepWithNext=True))
styles.add(ParagraphStyle(name='BodyReport',parent=styles['BodyText'],fontName='Helvetica',fontSize=9.3,leading=13,textColor=TEXT,spaceAfter=6,alignment=TA_LEFT))
styles.add(ParagraphStyle(name='BulletReport',parent=styles['BodyReport'],leftIndent=15,firstLineIndent=-8,bulletIndent=0,spaceAfter=3))
styles.add(ParagraphStyle(name='SmallCode',fontName='Courier',fontSize=8,leading=10,textColor=TEXT,leftIndent=8,rightIndent=8,spaceBefore=4,spaceAfter=7,backColor=PALE,borderPadding=6))
styles.add(ParagraphStyle(name='TableCell',fontName='Helvetica',fontSize=7.5,leading=9.3,textColor=TEXT,spaceAfter=0))
styles.add(ParagraphStyle(name='TableHead',fontName='Helvetica-Bold',fontSize=7.6,leading=9.3,textColor=colors.white,spaceAfter=0))

def inline(text):
    text=text.strip()
    # Replace markdown links before escaping other text.
    links=[]
    def save_link(m):
        links.append((m.group(1),m.group(2)))
        return f'@@LINK{len(links)-1}@@'
    text=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',save_link,text)
    text=html.escape(text,quote=False)
    text=re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',text)
    text=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',text)
    text=re.sub(r'\*([^*]+)\*',r'<i>\1</i>',text)
    text=re.sub(r'(https?://[^\s]+)',r'<link href="\1" color="#2D6EA3">\1</link>',text)
    for i,(label,url) in enumerate(links):
        lab=html.escape(label,quote=False); u=html.escape(url,quote=True)
        text=text.replace(f'@@LINK{i}@@',f'<link href="{u}" color="#2D6EA3">{lab}</link>')
    return text

def footer(canvas,doc):
    canvas.saveState(); w,h=A4
    canvas.setStrokeColor(GRID); canvas.setLineWidth(.5); canvas.line(doc.leftMargin,36,w-doc.rightMargin,36)
    canvas.setFont('Helvetica',8); canvas.setFillColor(colors.HexColor('#657789'))
    canvas.drawString(doc.leftMargin,23,'Wildfire Helicopter Project | Simulation-first report')
    canvas.drawRightString(w-doc.rightMargin,23,f'{doc.page}')
    canvas.restoreState()

story=[]; i=0; in_code=False; code=[]; table=[]
def flush_table():
    global table
    if not table:return
    data=[]
    for ri,row in enumerate(table):
        style=styles['TableHead'] if ri==0 else styles['TableCell']
        data.append([Paragraph(inline(cell),style) for cell in row])
    cols=len(data[0]); available=A4[0]-1.35*inch
    if cols==4: widths=[available*.19,available*.20,available*.34,available*.27]
    elif cols==3: widths=[available*.31,available*.16,available*.53]
    elif cols==2: widths=[available*.38,available*.62]
    else: widths=[available/cols]*cols
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT',splitByRow=1)
    t.setStyle(TableStyle([
      ('BACKGROUND',(0,0),(-1,0),NAVY),('TEXTCOLOR',(0,0),(-1,0),colors.white),
      ('GRID',(0,0),(-1,-1),.35,GRID),('VALIGN',(0,0),(-1,-1),'TOP'),
      ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
      ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
      ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F4F7FA')])
    ]))
    story.append(Spacer(1,4)); story.append(t); story.append(Spacer(1,8)); table=[]
while i<len(lines):
    line=lines[i]
    if line.strip().startswith('```'):
        if in_code:
            story.append(Preformatted('\n'.join(code),styles['SmallCode'],maxLineLength=92)); in_code=False; code=[]
        else:
            flush_table(); in_code=True; code=[]
        i+=1; continue
    if in_code: code.append(line); i+=1; continue
    if line.startswith('|'):
        vals=[v.strip() for v in line.strip().strip('|').split('|')]
        if not all(re.fullmatch(r':?-{3,}:?',v.replace(' ','')) for v in vals): table.append(vals)
        i+=1; continue
    flush_table()
    if not line.strip(): i+=1; continue
    if line.startswith('# '): story.append(Paragraph(inline(line[2:]),styles['ReportTitle'])); i+=1; continue
    if line.startswith('## '): story.append(CondPageBreak(.55*inch)); story.append(Paragraph(inline(line[3:]),styles['Section'])); i+=1; continue
    if line.startswith('### '): story.append(CondPageBreak(.4*inch)); story.append(Paragraph(inline(line[4:]),styles['Subsection'])); i+=1; continue
    if line.startswith('- '): story.append(Paragraph('• '+inline(line[2:]),styles['BulletReport'])); i+=1; continue
    m=re.match(r'^\d+\.\s+(.*)$',line)
    if m: story.append(Paragraph(inline(line),styles['BulletReport'])); i+=1; continue
    parts=[line.strip()]; i+=1
    while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','- ','```')) and not re.match(r'^\d+\.\s+',lines[i]):
        parts.append(lines[i].strip()); i+=1
    story.append(KeepTogether([Paragraph(inline(' '.join(parts)),styles['BodyReport'])]))
flush_table()
doc=SimpleDocTemplate(str(out),pagesize=A4,rightMargin=.68*inch,leftMargin=.68*inch,topMargin=.62*inch,bottomMargin=.62*inch,title='Autonomous Helicopter Wildfire Project Report',author='Wildfire Helicopter Project Team',subject='Simulation results and preliminary design study')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(out)
