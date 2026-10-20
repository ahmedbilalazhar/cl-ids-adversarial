"""Generate matched SVG, PDF, PNG and inline TikZ figures from one vector model.
Run using the bundled Codex Python runtime from the project root.
All figures describe proposed experiments, never completed implementation.
"""
from pathlib import Path
import math, json, re, html, sys
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.pdfmetrics import stringWidth
import pymupdf as fitz

HERE=Path(__file__).resolve().parent
INK='#263746'; BLUE='#DCE7F2'; GREEN='#E4EEDD'; GOLD='#F5EBD7'; PURPLE='#EAE2F1'
class Figure:
    def __init__(self,name,w,h):self.name=name;self.w=w;self.h=h;self.ops=[]
    def rect(self,x,y,w,h,fill='#FFFFFF',stroke='#667789',radius=5):
        self.ops.append(('rect',x,y,w,h,fill,stroke,radius))
    def text(self,x,y,s,size=12,bold=False,color=INK,anchor='left'):
        self.ops.append(('text',x,y,s,size,bold,color,anchor))
    def lines(self,x,y,lines,size=12,gap=17,bold=False):
        for i,s in enumerate(lines):self.text(x,y+i*gap,s,size,bold)
    def arrow(self,pts,dashed=False,color='#506576',head=True):
        self.ops.append(('arrow',pts,dashed,color,head))
    def panel(self,x,y,w,h,title,lines,fill,size=12):
        self.rect(x,y,w,h);self.rect(x,y,w,49,fill,radius=5)
        self.lines(x+10,y+20,title,15,18,True)
        self.lines(x+10,y+68,lines,size,18)
    def save(self):
        svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}pt" height="{self.h}pt" viewBox="0 0 {self.w} {self.h}" role="img" aria-labelledby="title desc">',f'<title id="title">{html.escape(self.name.replace("-"," "))}</title><desc id="desc">Proposed Phase 2 research methodology. Experimental arms are alternatives, not merged components.</desc>', '<rect width="100%" height="100%" fill="white"/>']
        pdf=canvas.Canvas(str(HERE/(self.name+'.pdf')),pagesize=(self.w,self.h))
        pdf.setTitle(self.name.replace('-',' '));pdf.setAuthor('Phase 2 research proposal')
        tikz=[r'\begin{tikzpicture}[x=1bp,y=-1bp]',f'\\path[use as bounding box] (0,0) rectangle ({self.w},{self.h});']
        def tc(c):return '{rgb,255:red,'+str(int(c[1:3],16))+';green,'+str(int(c[3:5],16))+';blue,'+str(int(c[5:7],16))+'}'
        def esc(s):
            s=s.replace('→',r'$\to$').replace('–','--').replace('•',r'$\bullet$')
            return ''.join({'&':r'\&','%':r'\%','_':r'\_','#':r'\#'}.get(c,c) for c in s)
        for op in self.ops:
            if op[0]=='rect':
                _,x,y,w,h,fill,stroke,r=op
                svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')
                pdf.setFillColor(HexColor(fill));pdf.setStrokeColor(HexColor(stroke));pdf.setLineWidth(1);pdf.roundRect(x,self.h-y-h,w,h,r,fill=1,stroke=1)
                tikz.append(f'\\path[draw={tc(stroke)},fill={tc(fill)},line width=1bp,rounded corners={r}bp] ({x},{y}) rectangle ({x+w},{y+h});')
            elif op[0]=='text':
                _,x,y,s,size,bold,color,anchor=op
                weight='bold' if bold else 'normal';sa={'left':'start','center':'middle','right':'end'}[anchor]
                svg.append(f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{sa}" fill="{color}">{html.escape(s)}</text>')
                font='Helvetica-Bold' if bold else 'Helvetica';pdf.setFont(font,size);pdf.setFillColor(HexColor(color))
                # ASCII in drawing text avoids incompatible vector-font glyph substitutions.
                {'left':pdf.drawString,'center':pdf.drawCentredString,'right':pdf.drawRightString}[anchor](x,self.h-y,s)
                ta={'left':'base west','center':'base','right':'base east'}[anchor]
                tf=r'\sffamily'+(r'\bfseries' if bold else '')+f'\\fontsize{{{size}}}{{{size*1.15}}}\\selectfont'
                tikz.append(f'\\node[anchor={ta},inner sep=0,text={tc(color)},font={tf}] at ({x},{y}) '+'{'+esc(s)+'};')
            else:
                _,pts,dashed,color,head=op
                path='M '+' L '.join(f'{x} {y}' for x,y in pts);dash=' stroke-dasharray="5 4"' if dashed else ''
                svg.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="1.4"{dash}/>')
                pdf.setStrokeColor(HexColor(color));pdf.setLineWidth(1.4);pdf.setDash([5,4] if dashed else [])
                p=pdf.beginPath();p.moveTo(pts[0][0],self.h-pts[0][1])
                for x,y in pts[1:]:p.lineTo(x,self.h-y)
                pdf.drawPath(p);pdf.setDash([])
                tk=' -- '.join(f'({x},{y})' for x,y in pts)
                tikz.append(f'\\path[draw={tc(color)},line width=1.4bp'+(',dashed' if dashed else '')+'] '+tk+';')
                if head:
                    a,b=pts[-2:];angle=math.atan2(b[1]-a[1],b[0]-a[0]);length=6;side=3
                    tri=[b,(b[0]-length*math.cos(angle)+side*math.sin(angle),b[1]-length*math.sin(angle)-side*math.cos(angle)),(b[0]-length*math.cos(angle)-side*math.sin(angle),b[1]-length*math.sin(angle)+side*math.cos(angle))]
                    svg.append(f'<polygon points="'+ ' '.join(f'{x},{y}' for x,y in tri)+f'" fill="{color}"/>')
                    pdf.setFillColor(HexColor(color));p=pdf.beginPath();p.moveTo(tri[0][0],self.h-tri[0][1])
                    for x,y in tri[1:]:p.lineTo(x,self.h-y)
                    p.close();pdf.drawPath(p,fill=1,stroke=0)
                    tikz.append(f'\\path[fill={tc(color)}] '+' -- '.join(f'({x:.3f},{y:.3f})' for x,y in tri)+' -- cycle;')
        svg.append('</svg>');(HERE/(self.name+'.svg')).write_text('\n'.join(svg),encoding='utf8')
        pdf.showPage();pdf.save();tikz.append(r'\end{tikzpicture}')
        (HERE/(self.name+'-inline.tex')).write_text('\n'.join(tikz),encoding='utf8')
        d=fitz.open(HERE/(self.name+'.pdf'));d[0].get_pixmap(matrix=fitz.Matrix(2.5,2.5),alpha=False).save(HERE/(self.name+'.png'))
        assert not d[0].get_images(),'PDF must be vector'
        # Intended spanning width: 7 inches. These are not single-column figures.
        return {'name':self.name,'canvas_pt':[self.w,self.h], 'intended_width_in':7,'body_font_at_7in_pt':12*504/self.w,'heading_font_at_7in_pt':15*504/self.w,'pdf_raster_images':len(d[0].get_images())}

def overview():
    f=Figure('methodology-overview',720,358)
    f.text(16,22,'PROPOSED METHODOLOGY',15,True)
    specs=[(['Data and','representation'],['CICIDS2017','Audited sidecar','Isolated sessions','Frozen T0 features'],BLUE),
      (['Protocol','development'],['Development only','Feasibility gates','Tuning and pairing','Analysis lock'],GOLD),
      (['Federated','experiments'],['Five clients','Alternative arms','FT / EI / DR','DR / DG / DM / DC','E1-E4; FedAvg'],GREEN),
      (['Fixed-bank','evaluation'],['Clean test banks','Source damage','Persistence','Acquisition','Collateral; costs'],BLUE),
      (['Research','analysis'],['Paired statistics','Matched ablations','Failure analysis','Evidence and','limitations'],PURPLE)]
    for i,(title,lines,fill) in enumerate(specs):
        x=16+140*i;f.panel(x,40,128,166,title,lines,fill)
        if i<4:f.arrow([(x+128,125),(x+140,125)])
    f.rect(16,250,425,73,'#FFFFFF','#89939D')
    f.text(28,270,'CICIoT2023: separate exploratory protocol',15,True)
    f.text(28,290,'Own audit, scaler, schedule and independent runs',12)
    f.text(28,309,'No pooled data, weights or primary estimates',12)
    f.arrow([(220,206),(220,250)],True)
    f.text(236,231,'Method settings only',12)
    f.text(461,273,'Solid: primary dependencies',12)
    f.text(461,294,'Dashed: exploratory transfer',12)
    f.text(16,347,'E2: training-only corruption. E3-E4: withdrawal without fresh Hulk acquisition.',12)
    return f

def architecture():
    f=Figure('proposed-framework-architecture',720,628)
    f.text(16,22,'PROPOSED FRAMEWORK ARCHITECTURE',15,True)
    f.rect(14,38,692,112,BLUE)
    f.text(26,57,'SERVER COORDINATION',15,True)
    blocks=[(26,140,['Shared head'],['Preserve old rows','Add supplied classes']),
      (182,140,['Broadcast'],['Global parameters','Reset local Adam']),
      (390,140,['FedAvg'],['Admitted-row weights','Active clients only']),
      (546,148,['Final broadcast'],['Experience-end state','Frozen evaluation'])]
    for x,w,title,lines in blocks:
        f.rect(x,68,w,69);f.text(x+9,87,title[0],14,True);f.lines(x+9,107,lines,12,17)
    f.arrow([(166,102),(182,102)]);f.arrow([(530,102),(546,102)])
    f.arrow([(390,102),(322,102)])
    f.text(355,88,'repeat',12,anchor='center')
    f.rect(30,184,676,252,'#F5F8F1','#94A886');f.rect(22,192,676,252,'#EDF3E7','#94A886')
    f.rect(14,200,676,252,GREEN,'#6D8A58')
    f.text(26,220,'CLIENT LEARNING: FIVE PERSISTENT CLIENTS',15,True)
    f.text(26,238,'Separate state per experimental arm; blocks below describe one client.',12)
    f.arrow([(252,137),(252,200)])
    f.text(267,174,'parameters',12)
    f.arrow([(646,254),(646,164),(460,164),(460,137)])
    f.text(491,179,'weights + admitted counts',12)
    boxes=[(26,103,'Current shard',['Supplied labels','Training only']),
      (144,128,'Admission',['Bypass, or','frozen scores','DG / DM / DC']),
      (288,182,'One learner',['128/64 MLP','FT: current loss','EI: importance penalty','DR family: DER++']),
      (487,102,'Local update',['Local objective','Local Adam']),
      (606,72,'Upload',['Weights','Counts'])]
    for x,w,title,lines in boxes:
        f.rect(x,254,w,96);f.text(x+8,274,title,13,True);f.lines(x+8,294,lines,12,15 if x==288 else 17)
    for a,b in [(129,144),(272,288),(470,487),(589,606)]:f.arrow([(a,300),(b,300)])
    f.rect(144,374,128,58,'#F6F9F2','#7B956B')
    f.text(154,393,'EI state only',13,True);f.lines(154,410,['Anchor + importance'],12)
    f.arrow([(272,401),(280,401),(280,331),(288,331)],True)
    f.rect(288,374,182,58,'#F6F9F2','#7B956B')
    f.text(298,393,'DER++ replay only',13,True);f.text(298,411,'Unique IDs; stored teachers',12)
    f.arrow([(342,374),(342,350)],True)
    f.arrow([(538,350),(538,403),(470,403)],True)
    f.text(552,384,'teacher + ID',12)
    f.text(26,447,'Admission stays fixed. Local updates / FedAvg repeat for the locked budget.',12)
    f.rect(14,470,692,84,PURPLE,'#877496')
    f.text(26,489,'EXPERIENCE EVOLUTION: THE SCHEDULE GOVERNS ALL ARMS',15,True)
    stages=[('E1: acquire',['FTP / SSH anchors','Filters disabled']),('E2: poison',['Hulk to benign','One client; labels only']),('E3: withdraw',['New attack families','No fresh Hulk']),('E4: withdraw',['New attack families','No fresh Hulk'])]
    for i,(title,lines) in enumerate(stages):
        x=26+i*168;f.rect(x,499,157,52);f.text(x+8,514,title,13,True);f.lines(x+8,529,lines,12,14)
        if i<3:f.arrow([(x+157,522),(x+168,522)])
    f.rect(14,577,692,42,BLUE)
    f.text(26,594,'EVALUATOR ONLY: fixed clean banks; isolated reference labels and poison indicators',13,True)
    f.text(26,611,'Source damage, persistence, acquisition, collateral errors and resource costs',12)
    f.arrow([(694,104),(713,104),(713,598),(706,598)])
    return f

if __name__=='__main__':
    results=[overview().save(),architecture().save()]
    (HERE/'figure-validation.json').write_text(json.dumps(results,indent=2),encoding='utf8')
    if '--embed' not in sys.argv:
        print(json.dumps(results,indent=2));sys.exit(0)
    p=HERE.parent/'submissions/phase2.tex';s=p.read_text(encoding='utf8')
    new=r'''\section{Deliverable 4: Research Methodology Architecture}
Figure~\ref{fig:methodology} summarizes five methodological phases; Figure~\ref{fig:framework} expands the proposed federated experiment. The phases summarize the twelve steps in Deliverable 3: data/representation covers Steps 1--4; development uses Step 7; federated experiments cover Steps 5--7; evaluation is Step 8; analysis covers Steps 9--12. Each learner/admission condition is a separate run with its own client state; conditions do not merge into one learner.

'''
    captions=[('methodology-overview','fig:methodology',r'Proposed methodology overview. Solid arrows transfer audited inputs, locked settings, trained checkpoints and predictions/metrics, respectively. Predictions support failure analysis directly. Component experiments receive their own matched evaluations. The dashed branch transfers method settings to a separate exploratory CICIoT2023 protocol; data, weights and primary estimates are not pooled. Exact settings remain in the protocol tables.'),
      ('proposed-framework-architecture','fig:framework',r'Proposed framework architecture. Server coordination and client learning repeat within each experience. FT/EI/DR are alternative learner arms; DG/DM/DC are alternative admission conditions on DER++. EI alone uses importance/anchor state; DER++ arms alone use replay. Dashed client edges denote state access conditional on the selected learner. Final broadcasts update importance/anchor state on eligible clients once per experience. E2 corrupts training labels on one client only; E3/E4 withdraw corruption without fresh Hulk acquisition. The evaluator remains outside admission/inference.')]
    for name,label,caption in captions:
        new+=r'\begin{figure}[htbp]'+'\n'+r'\centering'+'\n'+r'\resizebox{\linewidth}{!}{%'+'\n'+(HERE/(name+'-inline.tex')).read_text()+'\n}\n'+r'\caption{'+caption+'}\n'+r'\label{'+label+'}\n'+r'\end{figure}'+'\n\n'
    pattern=r'(?:\\clearpage\s*)?\\section\{Deliverable 4:.*?(?=\\section\{Scope and Validity Threats\})'
    s,n=re.subn(pattern,lambda _:new,s,flags=re.S);assert n==1;p.write_text(s,encoding='utf8')
    print(json.dumps(results,indent=2))
