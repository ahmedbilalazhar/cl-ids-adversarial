"""Export and render the research report with tables, captions and source links."""
from pathlib import Path
import re,html
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,Table,TableStyle,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from PIL import Image as PILImage
import pymupdf
R=Path(__file__).resolve().parents[1];O=R/"submissions/phase3-report"
styles=getSampleStyleSheet()
styles["BodyText"].fontSize=9.2;styles["BodyText"].leading=13;styles["BodyText"].spaceAfter=5
styles["Title"].fontSize=19;styles["Title"].leading=23;styles["Title"].textColor=colors.HexColor("#153b4c")
for key in ("Heading2","Heading3"):
 styles[key].textColor=colors.HexColor("#153b4c");styles[key].keepWithNext=True
styles.add(ParagraphStyle("Cell",fontName="Helvetica",fontSize=8,leading=10,spaceAfter=0))
styles.add(ParagraphStyle("Caption",fontName="Helvetica-Oblique",fontSize=8,leading=10,spaceAfter=10))
styles.add(ParagraphStyle("Reference",parent=styles["BodyText"],fontSize=8,leading=11))
def safe(text):
 text=html.escape(text)
 return re.sub(r"(https?://[^ &]+)",lambda m:'<link href="'+m.group(1)+'" color="#175f8a">'+m.group(1)+'</link>',text)
story=[];source=(O/"report.md").read_text(encoding="utf-8")
for block in re.sub(r"(?<=\|)\n\n(?=\|)","\n",source).split("\n\n"):
 if not block.strip():continue
 if block.startswith("!["):
  match=re.match(r"!\[(.*?)\]\((.*?)\)",block);caption,path=match.groups();path=O/path
  with PILImage.open(path) as im:w,h=im.size
  width=470;height=width*h/w
  if height>430:height=430;width=height*w/h
  story.append(KeepTogether([Image(str(path),width=width,height=height),Spacer(1,5),Paragraph(safe(caption),styles["Caption"])]));continue
 if block.startswith("|"):
  data=[]
  for line in block.splitlines():
   if re.match(r"^\|[-: |]+\|$",line):continue
   cells=[x.strip() for x in line.strip("|").split("|")]
   data.append([Paragraph(safe(c),styles["Cell"]) for c in cells])
  count=len(data[0])
  widths={2:[125,345],3:[110,175,185],4:[150,107,107,106],5:[190,70,70,70,70],6:[145,65,65,65,65,65]}.get(count,[470/count]*count)
  t=Table(data,colWidths=widths,repeatRows=1,hAlign="LEFT")
  t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e5eef2")),("LINEBELOW",(0,0),(-1,0),.6,colors.HexColor("#8aa3b0")),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f6f8fa")]),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
  story.extend([t,Spacer(1,10)]);continue
 level=len(block)-len(block.lstrip("#"))
 style=styles["Title" if level==1 else "Heading2" if level==2 else "Heading3"] if level else styles["Reference" if block.startswith("[") else "BodyText"]
 story.extend([Paragraph(safe(block.lstrip("# ")),style),Spacer(1,4)])
def footer(c,d):
 c.setStrokeColor(colors.HexColor("#b7c9d0"));c.line(42,34,550,34)
 c.setFont("Helvetica",7.5);c.setFillColor(colors.HexColor("#48616c"))
 c.drawString(42,22,"Computer Networks | Phase 3 | Development-bank evaluation");c.drawRightString(550,22,str(d.page))
pdf=O/"phase3-report.pdf"
SimpleDocTemplate(str(pdf),rightMargin=42,leftMargin=42,topMargin=38,bottomMargin=45,
 title="Poisoning persistence and legitimate adaptation in federated continual IDS",
 author="Saneedullah; Ahmed Bilal").build(story,onFirstPage=footer,onLaterPages=footer)
preview=R/"tmp/pdfs/phase3-report";preview.mkdir(parents=True,exist_ok=True)
doc=pymupdf.open(pdf)
checks=[]
for i,page in enumerate(doc):
 text=page.get_text();assert text.strip()
 page.get_pixmap(matrix=pymupdf.Matrix(1,1)).save(str(preview/f"page-{i+1:02}.png"))
 checks.append(dict(page=i+1,characters=len(text),width=page.rect.width,height=page.rect.height))
import json
(O/"pdf-validation.json").write_text(json.dumps(dict(pages=len(doc),page_checks=checks),indent=2))
import shutil
final_dir=R/"output/pdf";final_dir.mkdir(parents=True,exist_ok=True)
shutil.copy2(pdf,final_dir/"phase3-report.pdf")
print("Rendered",len(doc),"pages to",preview)
