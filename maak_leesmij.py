# DraveKaraoke - "Lees mij eerst" (PDF, grote letters)
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
import os
HERE = os.path.dirname(os.path.abspath(__file__))
t = ParagraphStyle('t', fontName='Helvetica-Bold', fontSize=34, leading=42, textColor='#4a3d8f', spaceAfter=12)
h = ParagraphStyle('h', fontName='Helvetica-Bold', fontSize=24, leading=30, textColor='#4a3d66', spaceBefore=18, spaceAfter=8)
b = ParagraphStyle('b', fontName='Helvetica', fontSize=20, leading=28, spaceAfter=10)
L = [Image(os.path.join(HERE, 'assets', 'icon_256.png'), width=3.2 * cm, height=3.2 * cm, hAlign='LEFT'), Paragraph('Lees mij eerst', t),
     Paragraph('Hallo! Dit is <b>DraveKaraoke</b>. Samen zingen met je pc en je mobiel. De pc speelt het liedje, op je mobiel loopt de tekst mee.', b)]
def blok(kop, regels):
    L.append(Paragraph(kop, h))
    for x in regels: L.append(Paragraph(x, b))
blok('1. Starten', ['Dubbelklik op <b>DraveKaraoke.exe</b>.', 'Vraagt Windows of het netwerk mag? Kies <b>Toestaan</b>.'])
blok('2. Ziet u een blauw venster van Windows?', ['<i>"Windows heeft uw pc beschermd"</i> is normaal bij nieuwe gratis programma&#39;s. Klik op <b>Meer informatie</b> en dan op <b>Toch uitvoeren</b>. Dit hoeft maar &eacute;&eacute;n keer.'])
blok('3. Je mobiel', ['Zelfde wifi als de pc. Scan de <b>QR-code</b> rechts op de pc.', 'Daarna kun je de <b>Android-app</b> downloaden (bij Wachtrij). Die vindt de pc voortaan zelf.'])
blok('4. Zingen of muziek', ['Zoek een liedje, tik op <b>Nu zingen</b> of <b>Later</b>.', 'Bovenaan wissel je tussen <b>Karaoke</b> (met tekst) en <b>Muziek</b> (de rij speelt gewoon door).'])
blok('Meer hulp', ['In de map staat de <b>snelgids</b> met plaatjes, en een <b>uitlegfilmpje</b>.', 'Mail ons: <b>service@dravenlock.nl</b>',
     'DraveKaraoke is gratis. Steunen mag: <b>paypal.me/roger076</b>. Dank je wel!', '<i>Dravenlock - Roger en Claudio</i>'])
SimpleDocTemplate(os.path.join(HERE, 'Lees_mij_eerst.pdf'), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                  title='DraveKaraoke - Lees mij eerst').build(L)
print('KLAAR')
