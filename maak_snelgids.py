# DraveKaraoke - snelgids (PDF) - versie 0.2
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
HERE = os.path.dirname(os.path.abspath(__file__))
G = lambda n: os.path.join(HERE, 'gids', n)
t = ParagraphStyle('t', fontName='Helvetica-Bold', fontSize=26, leading=32, textColor='#4a3d8f', spaceAfter=8)
h = ParagraphStyle('h', fontName='Helvetica-Bold', fontSize=18, leading=24, textColor='#4a3d8f', spaceBefore=12, spaceAfter=6, keepWithNext=1)
b = ParagraphStyle('b', fontName='Helvetica', fontSize=14, leading=20, spaceAfter=6)
k = ParagraphStyle('k', parent=b, fontSize=11, leading=14, alignment=1, textColor='#555555')
L = [Image(os.path.join(HERE, 'assets', 'icon_256.png'), 2.6 * cm, 2.6 * cm, hAlign='LEFT'), Paragraph('DraveKaraoke - snelgids', t),
     Paragraph('Versie 0.2. Samen zingen: de pc speelt het liedje via je boxen of soundbar, en op je mobiel loopt de songtekst mee. '
               'Gewoon voor de lol: geen score, geen microfoon. En met de <b>muziek-modus</b> bedien je je muziek vanaf de bank.', b)]
def blok(kop, regels):
    L.append(Paragraph(kop, h))
    for x in regels: L.append(Paragraph('&bull; ' + x, b))
def plaatjes(namen, onder):
    w = 3.9 * cm
    L.append(Table([[Image(G(n), w, w * 2.035) for n in namen], [Paragraph(o, k) for o in onder]]))
blok('1. Starten op de pc', ['Dubbelklik op <b>DraveKaraoke.exe</b>. Rechts zie je een <b>QR-code</b> en een adres.',
     'De eerste keer vraagt Windows misschien of DraveKaraoke het netwerk mag gebruiken. Kies <b>Toestaan</b> (alleen Priv&eacute;-netwerken). Anders kan je mobiel de pc niet vinden.'])
blok('2. Koppelen met je mobiel', ['Je mobiel moet op <b>hetzelfde wifi</b> zitten als de pc.', 'Scan de QR-code met de camera van je mobiel, of typ het adres in je browser.',
     'Kies wie je bent, of typ je naam.'])
blok('3. De Android-app (aanrader)', ['Op je mobiel staat bij <b>Wachtrij</b> de knop <b>Download de Android-app</b>. Installeer hem. De eerste keer vraagt Android of je "uit onbekende bron" mag installeren: dat mag, de app komt van je eigen pc.',
     'De app <b>zoekt zelf de pc</b> in je wifi en onthoudt hem. Nooit meer scannen.',
     'Vindt hij de pc niet? Tik op <b>Opnieuw zoeken</b>, of <b>Adres zelf typen</b> (het adres staat rechts op de pc).'])
L.append(PageBreak())
blok('4. Een liedje kiezen', ['Tik op <b>Zoeken</b>, typ een liedje of artiest. Tip: zet er <b>karaoke</b> achter, dan vind je versies zonder zang.',
     'Een groen <font color="#2a9d8f"><b>vinkje</b></font> = speelt in DraveKaraoke. Oranje <font color="#d9822b"><b>YouTube</b></font> = mag alleen op YouTube zelf; die speelt op de YouTube-pagina, de tekst loopt toch mee.',
     '<b>Nu zingen</b> = meteen spelen (het liedje van nu stopt). <b>+ Later</b> = achteraan in de wachtrij.'])
plaatjes(['m_zoek.png', 'm_rij.png', 'm_zing.png', 'm_muziek.png'], ['Zoeken', 'Wachtrij', 'Zingen (duet)', 'Muziek-modus'])
blok('5. Om de beurt', ['De wachtrij gaat <b>om de beurt</b>: steeds iemand anders dan net. Je eigen liedjes haal je weg met het rode kruisje.'])
blok('6. Zingen', ['Bij <b>Zingen</b> loopt de songtekst mee: de regel van nu is groot en wit.',
     'Loopt de tekst voor of achter? Tik op <b>Tekst eerder</b> of <b>Tekst later</b>. Wordt per liedje onthouden.',
     'Geen of de verkeerde tekst? Typ onder de tekst bij <b>Zoek tekst</b> zelf artiest en titel, bijvoorbeeld "Pastorale Ramses Shaffy".'])
blok('7. Duet', ['Tik op <b>Duet aanpassen</b> en tik op een regel: <font color="#7a5fd0">paars</font> (zanger 1), <font color="#2a9d8f">turquoise</font> (zanger 2), <font color="#c9a227">geel</font> (samen) of weer gewoon. Je eigen regels zijn onderstreept.'])
L.append(PageBreak())
blok('8. Muziek-modus', ['Bovenaan op je mobiel: tik op <b>Karaoke-modus &middot; tik voor Muziek</b>.',
     'Dan geen songtekst: de rij speelt gewoon <b>op volgorde</b>. Is de rij leeg, dan kiest DraveKaraoke zelf iets van <b>dezelfde artiest</b>.',
     'Ideaal als de pc in een andere kamer staat: alles bedien je vanaf de bank.'])
blok('9. Geen reclame met YouTube Premium', ['Heb je YouTube Premium? Klik rechts op de pc op <b>YouTube inloggen</b>, log rechtsboven in, en klik op <b>Klaar met inloggen</b>. DraveKaraoke onthoudt het.',
     'Zonder Premium kan er reclame komen. De tekst wacht dan netjes tot het liedje echt begint.',
     'Liever in je eigen browser? Klik op <b>Speel in mijn browser</b>. Klik daar &eacute;&eacute;n keer om te starten (F11 = groot). "Alleen YouTube"-liedjes openen dan in &eacute;&eacute;n vast YouTube-tabblad, dat na het liedje vanzelf dichtgaat. Sta pop-ups toe voor 127.0.0.1.'])
L.append(Image(G('pc_speler.png'), 13 * cm, 7.3 * cm)); L.append(Paragraph('Het pc-scherm: de video, met onderaan de regel van nu en de volgende regel.', k))
blok('10. Bediening', ['Onderaan op je mobiel: zachter, pauze, opnieuw, volgende, harder.', 'Op de pc: <b>F11</b> = groot scherm, <b>spatie</b> = pauze, <b>F1</b> = info.'])
blok('Goed om te weten', ['Songteksten komen van <b>LRCLIB</b> (gratis, zonder account). Niet elk liedje heeft een tekst die meeloopt.',
     'Alles gaat via je eigen wifi. Je instellingen en je inlog staan in de map van de app, niet in de cloud.'])
L.append(Spacer(1, 10)); L.append(Paragraph('Dravenlock (Roger &amp; Claudio) - gratis, steun via paypal.me/roger076 - service@dravenlock.nl', b))
SimpleDocTemplate(os.path.join(HERE, 'DraveKaraoke_snelgids.pdf'), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.6 * cm, bottomMargin=1.6 * cm,
                  title='DraveKaraoke snelgids').build(L)
print('snelgids klaar')
