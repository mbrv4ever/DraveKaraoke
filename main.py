# -*- coding: utf-8 -*-
# DraveKaraoke 0.2 - samen zingen met de pc en je mobiel.
# 0.2: video's die niet buiten YouTube mogen, spelen op de YouTube-pagina zelf (groot), met de tekst eronder;
#      betere songtekst-zoeker + zelf zoeken op je mobiel; grotere letters op de pc.
# De pc speelt het liedje (YouTube) via de boxen/soundbar. Op de mobieltjes: zoeken, wachtrij (om de beurt),
# bediening en de songtekst die meeloopt (LRCLIB), met een duetstand in kleuren. Geen score, geen microfoon.
# Alles via het eigen wifi-netwerk thuis. Dravenlock (Roger & Claudio), 20-11-2026. Donationware: paypal.me/roger076
import os, sys, time, locale, traceback, webbrowser

HERE = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
BUNDEL = getattr(sys, "_MEIPASS", HERE)
CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)
VERSIE = "0.2"
try:
    NL = (locale.getlocale()[0] or "nl").lower().startswith(("nl", "dutch"))
except Exception:
    NL = True

TX = {
    "titel": ("DraveKaraoke", "DraveKaraoke"),
    "scan": ("Scan met je mobiel:", "Scan with your phone:"),
    "of": ("of typ in je browser:", "or type in your browser:"),
    "zelfde": ("Je mobiel moet op hetzelfde wifi zitten als deze pc.", "Your phone must be on the same wifi as this pc."),
    "nu": ("Nu:", "Now:"), "rij": ("Wachtrij (om de beurt):", "Queue (taking turns):"), "leeg": ("Nog niets. Kies een liedje op je mobiel.", "Nothing yet. Pick a song on your phone."),
    "volgende": ("⏭  Volgende", "⏭  Next"), "pauze": ("⏯  Pauze", "⏯  Pause"), "scherm": ("⛶  Groot scherm (F11)", "⛶  Full screen (F11)"),
    "info": ("Info", "Info"), "browser": ("🌐  Speel in mijn browser", "🌐  Play in my browser"),
    "login": ("🔑  YouTube inloggen", "🔑  YouTube sign in"), "login_klaar": ("✔  Klaar met inloggen", "✔  Done signing in"),
    "hier": ("🖥  Speel weer hier", "🖥  Play here again"), "doneer": ("Doneren via PayPal", "Donate via PayPal"), "sluit": ("Sluiten", "Close"),
    "info_tekst": ("DraveKaraoke %s - testversie\nDravenlock (Roger & Claudio)\n\nSamen zingen: de pc speelt het liedje,\nje mobiel toont de tekst die meeloopt.\n"
                   "Alles via je eigen wifi thuis. Geen account.\nSongteksten: LRCLIB (gratis). Video's: YouTube.\n\nSteun ons: paypal.me/roger076\nVragen: service@dravenlock.nl",
                   "DraveKaraoke %s - test version\nDravenlock (Roger & Claudio)\n\nSing together: the pc plays the song,\nyour phone shows the lyrics as they go.\n"
                   "Everything over your own home wifi. No account.\nLyrics: LRCLIB (free). Videos: YouTube.\n\nSupport us: paypal.me/roger076\nQuestions: service@dravenlock.nl"),
    "poortfout": ("De poort %d is bezet. Draait DraveKaraoke al?", "Port %d is in use. Is DraveKaraoke already running?"),
}


def T(k):
    return TX[k][0 if NL else 1]


def main():
    sys.path.insert(0, HERE)
    import karaoke, server
    from PyQt6.QtCore import Qt, QTimer, QUrl
    from PyQt6.QtGui import QFont, QIcon, QPixmap, QImage, QShortcut, QKeySequence
    from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QDialog, QMessageBox
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile, QWebEnginePage

    os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--autoplay-policy=no-user-gesture-required")
    app = QApplication(sys.argv)
    kar = karaoke.Karaoke(HERE)
    poort = int(kar.inst.get("poort", 8765))
    web = os.path.join(BUNDEL, "web") if os.path.isdir(os.path.join(BUNDEL, "web")) else os.path.join(HERE, "web")
    try:
        server.maak_server(kar, web, poort)
    except OSError:
        QMessageBox.warning(None, T("titel"), T("poortfout") % poort)
        return
    ip = server.eigen_ip()
    adres = "http://%s:%d" % (ip, poort)

    w = QMainWindow()
    w.setWindowTitle(T("titel"))
    ic = os.path.join(HERE, "assets", "icon_256.png")
    if os.path.exists(ic):
        w.setWindowIcon(QIcon(ic))
    w.setStyleSheet("""
        QMainWindow, QWidget { background:#16131f; color:#f0f0f5; }
        QPushButton { background:#221c34; border:3px solid #b59cff; border-radius:14px; padding:10px 14px; color:white; }
        QPushButton:hover { background:#4a3d66; }
        QLabel { background:transparent; }
    """)
    F = lambda px, vet=True: QFont("Segoe UI", px, QFont.Weight.Bold if vet else QFont.Weight.Normal)

    # links: de speler (video + meelopende tekst)
    profiel = QWebEngineProfile("DraveKaraoke", w)
    profiel.setPersistentStoragePath(os.path.join(CACHE, "web"))        # portable: in de app-map
    profiel.setCachePath(os.path.join(CACHE, "webcache"))
    profiel.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)   # 0.2: ingelogd blijven
    view = QWebEngineView()
    view.setPage(QWebEnginePage(profiel, view))
    s = view.settings()
    s.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
    s.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
    view.setUrl(QUrl("http://127.0.0.1:%d/speler" % poort))

    # rechts: koppelen + wachtrij
    paneel = QWidget(); paneel.setFixedWidth(400)
    pl = QVBoxLayout(paneel); pl.setContentsMargins(14, 14, 14, 14); pl.setSpacing(10)
    kop = QLabel("🎤 " + T("titel")); kop.setFont(F(24)); kop.setStyleSheet("color:#b59cff;")
    l1 = QLabel(T("scan")); l1.setFont(F(16))
    qr = QLabel(); qr.setAlignment(Qt.AlignmentFlag.AlignCenter)
    try:
        import qrcode
        img = qrcode.make(adres, border=2).convert("RGB").resize((340, 340))
        data = img.tobytes("raw", "RGB")
        qr.setPixmap(QPixmap.fromImage(QImage(data, img.width, img.height, img.width * 3, QImage.Format.Format_RGB888).copy()))
    except Exception:
        qr.setText("(QR)")
    l2 = QLabel(T("of")); l2.setFont(F(14, False))
    url = QLabel(adres); url.setFont(F(18)); url.setStyleSheet("color:#ffdc5a;"); url.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    l3 = QLabel(T("zelfde")); l3.setFont(F(13, False)); l3.setWordWrap(True); l3.setStyleSheet("color:#9a93b8;")
    nu = QLabel(""); nu.setFont(F(17)); nu.setWordWrap(True); nu.setStyleSheet("color:#5ee0c8;")
    rijkop = QLabel(T("rij")); rijkop.setFont(F(16))
    rij = QLabel(T("leeg")); rij.setFont(F(15, False)); rij.setWordWrap(True); rij.setAlignment(Qt.AlignmentFlag.AlignTop)
    b_volg, b_pauze, b_scherm, b_info = QPushButton(T("volgende")), QPushButton(T("pauze")), QPushButton(T("scherm")), QPushButton(T("info"))
    b_login = QPushButton(T("browser"))
    b_inlog = QPushButton(T("login"))
    for b in (b_volg, b_pauze, b_scherm, b_inlog, b_login, b_info):
        b.setFont(F(17)); b.setMinimumHeight(60); b.setCursor(Qt.CursorShape.PointingHandCursor)
    for x in (kop, l1, qr, l2, url, l3, nu, rijkop):
        pl.addWidget(x)
    pl.addWidget(rij, 1)
    for b in (b_volg, b_pauze, b_scherm, b_inlog, b_login, b_info):
        pl.addWidget(b)

    # 0.2: tekstbalk voor als de video op de YouTube-pagina zelf speelt
    balk = QWidget(); balk.setFixedHeight(170); balk.setStyleSheet("background:#16131f; border-top:3px solid #4a3d66;")
    bl = QVBoxLayout(balk); bl.setContentsMargins(20, 10, 20, 10)
    regel_nu = QLabel(""); regel_nu.setFont(F(34)); regel_nu.setAlignment(Qt.AlignmentFlag.AlignCenter); regel_nu.setWordWrap(True)
    regel_straks = QLabel(""); regel_straks.setFont(F(20, False)); regel_straks.setAlignment(Qt.AlignmentFlag.AlignCenter)
    regel_straks.setStyleSheet("color:#9a93b8;")
    bl.addWidget(regel_nu); bl.addWidget(regel_straks); balk.hide()
    links = QWidget(); ll = QVBoxLayout(links); ll.setContentsMargins(0, 0, 0, 0); ll.setSpacing(0)
    ll.addWidget(view, 1); ll.addWidget(balk)
    midden = QWidget(); hl = QHBoxLayout(midden); hl.setContentsMargins(0, 0, 0, 0); hl.setSpacing(0)
    hl.addWidget(links, 1); hl.addWidget(paneel)

    yt = {"modus": "speler", "id": None, "tekst": None}
    SPELER_URL = "http://127.0.0.1:%d/speler" % poort
    GROOT_JS = """(function(){ if(!document.getElementById('drave_groot')){ var s=document.createElement('style'); s.id='drave_groot';
      s.textContent='#movie_player,.html5-video-player{position:fixed!important;left:0!important;top:0!important;width:100vw!important;height:100vh!important;z-index:2147483646!important;background:#000!important}'
      +'#masthead-container,ytd-masthead,#secondary,#below,#comments,#chat{display:none!important} body{overflow:hidden!important}'
      +'video.html5-main-video{width:100vw!important;height:100vh!important;left:0!important;top:0!important;object-fit:contain!important}';
      document.head.appendChild(s);} window.dispatchEvent(new Event('resize')); return 1; })()"""
    STAND_JS = "(function(){var v=document.querySelector('video.html5-main-video')||document.querySelector('video'); if(!v) return null;" \
               "var ad=!!document.querySelector('.ad-showing'); return [v.currentTime, !v.paused, v.ended, ad, location.search];})()"

    def yt_stand(r):
        if yt["modus"] != "yt" or not r:
            return
        tijd, speelt, eind, ad, waar = r
        n = kar.stand()["nu"]
        if ad or not n or n["id"] != yt["id"] or ("v=" + n["id"]) not in (waar or ""):
            return                                                   # reclame of oude pagina: niets doorgeven
        kar.van_speler(tijd, speelt, eind=bool(eind))

    def yt_doe(o):
        a = o.get("actie")
        js = {"pauze": "v.pause()", "verder": "v.play()", "opnieuw": "v.currentTime=0",
              "volume": "v.volume=%f" % (o.get("waarde", 80) / 100.0)}.get(a)
        if js:
            view.page().runJavaScript("(function(){var v=document.querySelector('video'); if(v){%s;}})()" % js)

    def yt_tekst_regels():
        n = kar.stand()
        if n.get("modus") == "muziek":
            regel_nu.setText("🎵 " + (n["nu"]["titel"] if n["nu"] else "")); regel_straks.setText("Muziek-modus" if NL else "Music mode"); return
        if not n["nu"]:
            regel_nu.setText(""); regel_straks.setText(""); return
        t = kar.tekst(n["nu"]["id"])
        if not t.get("klaar"):
            regel_nu.setText("♪"); regel_straks.setText(""); return
        r = t.get("regels") or []
        if not r:
            regel_nu.setText("♪ (geen songtekst gevonden)" if NL else "♪ (no lyrics found)"); regel_straks.setText(""); return
        tijd = n["tijd"] + (t.get("offset") or 0)
        i = -1
        if t.get("meelopend"):
            for k, (ts, _) in enumerate(r):
                if ts <= tijd: i = k
                else: break
        else:
            i = 0
        regel_nu.setText((r[i][1] if i >= 0 else "♪") or "♪"); regel_straks.setText(r[i + 1][1] if i + 1 < len(r) else "")

    RUST_HTML = ("<html><body style='margin:0;background:#16131f;color:#f0f0f5;font-family:Segoe UI,Arial;display:flex;"
                 "flex-direction:column;align-items:center;justify-content:center;height:100vh;text-align:center'>"
                 "<h1 style='color:#b59cff;font-size:56px;margin:0 0 20px'>🌐 " + T("browser").split("  ")[-1] + "</h1>"
                 "<p style='font-size:28px'>" + ("De liedjes spelen nu in je eigen browser (met je YouTube-account)." if NL else
                 "The songs now play in your own browser (with your YouTube account).") + "</p>"
                 "<p style='font-size:22px;color:#9a93b8'>" + ("Liedjes die alleen op YouTube mogen, openen daar in één YouTube-tabblad." if NL else
                 "Songs that only play on YouTube itself open there in one YouTube tab.") + "</p></body></html>")

    def browser_wissel():
        # 0.2: in je eigen browser spelen, waar je al bent ingelogd (Premium = geen reclame).
        if not yt["browser"]:
            yt.update(browser=True, modus="rust", id=None); balk.hide()
            view.setHtml(RUST_HTML)
            webbrowser.open(SPELER_URL)
            b_login.setText(T("hier"))
        else:
            yt.update(browser=False, modus="speler", id=None); balk.hide()
            view.setUrl(QUrl(SPELER_URL)); b_login.setText(T("browser"))
    yt["browser"] = False
    b_login.clicked.connect(browser_wissel)

    def inlog_wissel():
        # 0.2: jij logt zelf in op YouTube (rechtsboven "Inloggen"); DraveKaraoke onthoudt het in cache\web.
        if yt["modus"] != "login":
            if kar.stand()["speelt"]:
                kar.bedien("pauze")
            n0 = kar.stand()["nu"]
            yt.update(modus="login", id=None, login_nu=(n0["id"] if n0 else None)); balk.hide()
            view.setUrl(QUrl("https://www.youtube.com/"))
            b_inlog.setText(T("login_klaar"))
        else:
            b_inlog.setText(T("login"))
            if yt["browser"]:
                yt.update(modus="rust", id=None); view.setHtml(RUST_HTML)
            else:
                yt.update(modus="speler", id=None); view.setUrl(QUrl(SPELER_URL))
    b_inlog.clicked.connect(inlog_wissel)

    def yt_stap():
        if yt["modus"] == "login":
            n1 = kar.stand()["nu"]
            if n1 and n1["id"] != yt.get("login_nu"):                # er is een (nieuw) liedje gekozen: vanzelf terug
                inlog_wissel()
            return
        st = kar.stand(); n = st["nu"]
        wil_yt = bool(n and not n.get("insluiten", True)) and not yt["browser"]   # in browser-modus regelt de browser het zelf
        if wil_yt and (yt["modus"] != "yt" or yt["id"] != n["id"]):
            yt.update(modus="yt", id=n["id"]); balk.show()
            view.setUrl(QUrl("https://www.youtube.com/watch?v=%s&autoplay=1" % n["id"]))
        elif not wil_yt and yt["modus"] == "yt":
            balk.hide()
            if yt["browser"]:
                yt.update(modus="rust", id=None); view.setHtml(RUST_HTML)
            else:
                yt.update(modus="speler", id=None); view.setUrl(QUrl(SPELER_URL))
        if yt["modus"] == "yt":
            for o in kar.voor_speler()["opdrachten"]:
                yt_doe(o)
            view.page().runJavaScript(GROOT_JS)
            view.page().runJavaScript(STAND_JS, yt_stand)
            yt_tekst_regels()
    yt_t = QTimer(); yt_t.timeout.connect(yt_stap); yt_t.start(300)
    w.setCentralWidget(midden)

    def ververs():
        st = kar.stand()
        n = st["nu"]
        nu.setText(("%s 🎤 %s\n%s" % (T("nu"), n["wie"], n["titel"])) if n else "")
        v = st["wachtrij"]
        rij.setText("\n".join("%d. %s - %s" % (i + 1, x["wie"], x["titel"][:48]) for i, x in enumerate(v[:12])) if v else (T("leeg") if not n else "-"))
    t = QTimer(); t.timeout.connect(ververs); t.start(1000)

    def groot():
        if w.isFullScreen():
            w.showMaximized(); paneel.show()
        else:
            paneel.hide(); w.showFullScreen()

    def info():
        d = QDialog(w); d.setWindowTitle(T("titel")); d.setStyleSheet(w.styleSheet())
        v = QVBoxLayout(d); v.setContentsMargins(24, 20, 24, 20)
        l = QLabel(T("info_tekst") % VERSIE); l.setFont(F(12, False)); v.addWidget(l)
        k1, k2 = QPushButton(T("doneer")), QPushButton(T("sluit"))
        k1.clicked.connect(lambda: webbrowser.open("https://paypal.me/roger076")); k2.clicked.connect(d.accept)
        h = QHBoxLayout(); h.addWidget(k1); h.addWidget(k2); v.addLayout(h)
        d.exec()

    b_volg.clicked.connect(lambda: kar.bedien("volgende"))
    b_pauze.clicked.connect(lambda: kar.bedien("pauze" if kar.stand()["speelt"] else "verder"))
    b_scherm.clicked.connect(groot); b_info.clicked.connect(info)
    QShortcut(QKeySequence("F11"), w, activated=groot)
    QShortcut(QKeySequence("Esc"), w, activated=lambda: (w.showMaximized(), paneel.show()) if w.isFullScreen() else None)
    QShortcut(QKeySequence("F1"), w, activated=info)
    QShortcut(QKeySequence("Space"), w, activated=lambda: kar.bedien("pauze" if kar.stand()["speelt"] else "verder"))

    if os.environ.get("KARAOKE_PROEF"):                              # alleen voor de proef: "id|titel|wie;..."
        for deel in os.environ["KARAOKE_PROEF"].split(";"):
            i_, t_, wie_ = deel.split("|")
            kar.voeg_toe({"id": i_, "titel": t_, "wie": wie_, "duur": 0, "plaatje": "https://i.ytimg.com/vi/%s/mqdefault.jpg" % i_})
    if os.environ.get("KARAOKE_SHOT"):
        def foto():
            w.grab().save(os.path.join(CACHE, "shot.png")); app.quit()
        QTimer.singleShot(int(float(os.environ["KARAOKE_SHOT"]) * 1000), foto)

    ververs()
    w.showMaximized()
    app.exec()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        with open(os.path.join(CACHE, "error.log"), "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + traceback.format_exc() + "\n")
    finally:
        os._exit(0)
