# -*- coding: utf-8 -*-
"""DraveKaraoke - het brein: zoeken op YouTube, songteksten (LRCLIB) en de wachtrij (om de beurt).
Geen account, geen cloud van ons: alleen YouTube (zoeken) en LRCLIB (gratis teksten met tijdcodes)."""
from __future__ import annotations

import json
import os
import random
import re
import threading
import time
import urllib.parse
import urllib.request

UA = "DraveKaraoke/0.1 (https://dravenlock.nl)"


# ---------------------------------------------------------------- zoeken op YouTube
def zoek(vraag: str, aantal: int = 10) -> list[dict]:
    """Zoek liedjes op YouTube (via yt-dlp, zonder te downloaden)."""
    import yt_dlp
    vraag = (vraag or "").strip()
    if not vraag:
        return []
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "extract_flat": True, "skip_download": True}) as y:
        r = y.extract_info("ytsearch%d:%s" % (aantal, vraag), download=False)
    uit = []
    for e in r.get("entries") or []:
        if not e or not e.get("id") or e.get("live_status") == "is_live":
            continue
        uit.append({"id": e["id"], "titel": e.get("title") or "?", "duur": int(e.get("duration") or 0),
                    "kanaal": e.get("channel") or e.get("uploader") or "",
                    "plaatje": "https://i.ytimg.com/vi/%s/mqdefault.jpg" % e["id"]})
    import concurrent.futures as cf                            # 0.2: mag hij buiten YouTube spelen?
    with cf.ThreadPoolExecutor(8) as ex:
        for it, ok in zip(uit, ex.map(lambda x: mag_insluiten(x["id"]), uit)):
            it["insluiten"] = ok
    uit.sort(key=lambda x: 0 if x["insluiten"] else 1)       # die wel mogen bovenaan
    return uit


def mag_insluiten(vid: str) -> bool:
    """0.2: YouTube oEmbed: 200 = mag in een andere app spelen, 401 = alleen op YouTube zelf."""
    try:
        req = urllib.request.Request("https://www.youtube.com/oembed?format=json&url=" +
                                     urllib.parse.quote("https://www.youtube.com/watch?v=" + vid), headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=6) as r:
            return r.status == 200
    except Exception:
        return False


# ---------------------------------------------------------------- songteksten
_WEG = r"\b(karaoke|karaokeversie|karaoke-versie|lyrics?|songtekst|met songtekst|official|officiële|video|audio|hd|hq|4k|" \
       r"remaster(ed)?|clip|live|instrumental|instrumentaal|versie|version|with|met|sing ?along|karafun|cover|piano|guitar|gitaar|tekst|lyric video)\b"


def schoon_titel(titel: str, kanaal: str = "") -> str:
    """'Ramses Shaffy - Pastorale ( KARAOKE ) Lyrics' -> 'Ramses Shaffy Pastorale'. 0.2: ook emoji en kanaalnaam weg."""
    t = titel or ""
    if kanaal and len(kanaal) > 2:
        t = re.sub(re.escape(kanaal), " ", t, flags=re.I)
    t = re.sub(r"[^\w\s\-–—:|'&(){}\[\]]", " ", t)                   # emoji en rare tekens
    t = re.sub(r"\b\w*\d\w*angels?\b|\bby [\w&]+$", " ", t, flags=re.I)
    t = re.sub(r"[\(\[\{].*?[\)\]\}]", " ", t)
    t = re.sub(r"\S+&\s|\S+&$", " ", t)                                     # losse 'AJ&'-stukjes
    t = re.sub(r"[|*•·_]", " ", t)
    t = re.sub(_WEG, " ", t, flags=re.I)
    t = re.sub(r"\s*[-–—:]\s*", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def lees_lrc(lrc: str) -> list[list]:
    """'[01:02.34] tekst' -> [[62.34, 'tekst'], ...]"""
    regels = []
    for regel in (lrc or "").splitlines():
        tijden = re.findall(r"\[(\d+):(\d+(?:\.\d+)?)\]", regel)
        tekst = re.sub(r"\[[^\]]*\]", "", regel).strip()
        for m, s in tijden:
            regels.append([int(m) * 60 + float(s), tekst])
    regels.sort(key=lambda x: x[0])
    return regels


def _lrclib(q: str) -> list:
    try:
        req = urllib.request.Request("https://lrclib.net/api/search?" + urllib.parse.urlencode({"q": q}), headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=12) as r:
            return json.loads(r.read().decode("utf-8")) or []
    except Exception:
        return []


def pogingen(titel: str, kanaal: str = "") -> list:
    """0.2: een paar zoekzinnen, van precies naar ruim."""
    uit = []
    def voeg(x):
        x = re.sub(r"\s+", " ", x or "").strip()
        if len(x) >= 3 and x.lower() not in [u.lower() for u in uit]:
            uit.append(x)
    voeg(schoon_titel(titel, kanaal))
    delen = [schoon_titel(d) for d in re.split(r"\s[-–—|:]\s|\|", titel or "") if d.strip()]
    if len(delen) >= 2:
        voeg(delen[0] + " " + delen[1]); voeg(delen[1] + " " + delen[0])
    for d in delen:
        if len(d.split()) >= 1:
            voeg(d)
    return uit[:5]


def haal_tekst(titel: str, duur: int = 0, kanaal: str = "", eigen: str = "") -> dict:
    """Zoek de songtekst bij LRCLIB. Liefst met tijdcodes (meelopend), anders gewone tekst.
    0.2: meerdere pogingen; 'eigen' = zelf getypte zoektekst (wint altijd)."""
    lijst, q = [], ""
    for q in ([eigen] if eigen else pogingen(titel, kanaal)):
        lijst = _lrclib(q)
        if any(x.get("syncedLyrics") or x.get("plainLyrics") for x in lijst):
            break
    leeg = {"regels": [], "meelopend": False, "gevonden": "", "zoek": q}
    if not lijst:
        return leeg
    met = [x for x in lijst if x.get("syncedLyrics")]
    kies = met or [x for x in lijst if x.get("plainLyrics")]
    if not kies:
        return leeg
    if duur:
        kies.sort(key=lambda x: abs(float(x.get("duration") or 0) - duur))
    x = kies[0]
    naam = "%s - %s" % (x.get("artistName", ""), x.get("trackName", ""))
    if x.get("syncedLyrics"):
        return {"regels": lees_lrc(x["syncedLyrics"]), "meelopend": True, "gevonden": naam, "zoek": q,
                "lengte": float(x.get("duration") or 0)}
    regels = [[0.0, r.strip()] for r in (x.get("plainLyrics") or "").splitlines()]
    return {"regels": regels, "meelopend": False, "gevonden": naam, "zoek": q, "lengte": float(x.get("duration") or 0)}


# ---------------------------------------------------------------- de wachtrij en de stand
class Karaoke:
    """Alles wat de pc en de mobieltjes delen. Thread-veilig."""

    def __init__(self, map_):
        self.map = map_
        self.lock = threading.RLock()
        self.wachtrij: list[dict] = []      # in volgorde van toevoegen; de beurt wordt berekend
        self.nu: dict | None = None
        self.laatste_wie = ""
        self.tijd, self.tijd_t, self.speelt = 0.0, time.time(), False
        self.volume = 80
        self.opdrachten: list[dict] = []    # voor de speler op de pc
        self.teksten: dict = {}              # id -> tekst
        self.melding, self.melding_t = "", 0.0
        self.inst = self._lees("instellingen.json", {"namen": [], "poort": 8765})
        self.extra = self._lees("liedjes.json", {})   # id -> {"offset": s, "duet": {regel: kleur}}
        self.teller = 0
        self.gespeeld: list[str] = []       # 0.2 muziek: recent gespeelde id's (niet herhalen)
        self.auto_bezig = False

    # ---- bestanden (alles in de app-map, portable)
    def _lees(self, naam, standaard):
        try:
            with open(os.path.join(self.map, naam), encoding="utf-8") as f:
                d = json.load(f)
            return d if isinstance(d, type(standaard)) else standaard
        except Exception:
            return standaard

    def _schrijf(self, naam, d):
        try:
            with open(os.path.join(self.map, naam), "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=1)
        except Exception:
            pass

    # ---- namen
    def ken_naam(self, naam: str):
        naam = (naam or "").strip()[:20]
        with self.lock:
            if naam and naam not in self.inst["namen"]:
                self.inst["namen"].append(naam)
                self._schrijf("instellingen.json", self.inst)

    # ---- 0.2: muziek-modus (geen tekst, gewoon de rij af; is de rij leeg dan iets van dezelfde artiest)
    def modus(self) -> str:
        return "muziek" if self.inst.get("modus") == "muziek" else "karaoke"

    def zet_modus(self, m: str):
        with self.lock:
            self.inst["modus"] = "muziek" if m == "muziek" else "karaoke"
            self._schrijf("instellingen.json", self.inst)
        self.meld("🎵 Muziek-modus" if m == "muziek" else "🎤 Karaoke-modus")

    def _auto_volgende(self, vorige: dict):
        """Rij leeg in muziek-modus: zoek iets van dezelfde artiest en speel dat."""
        try:
            k = re.sub(r"\s*(- Topic|VEVO|Official|Music)\s*$", "", vorige.get("kanaal", ""), flags=re.I).strip()
            t = schoon_titel(vorige.get("titel", ""), vorige.get("kanaal", ""))
            artiest = t.split(" - ")[0].strip() if " - " in t else (k or t)
            for vraag in (artiest + " songs", artiest, t):
                lijst = [x for x in zoek(vraag, 15) if x["id"] not in self.gespeeld and 90 <= (x.get("duur") or 0) <= 600]
                lijst.sort(key=lambda x: 0 if x.get("insluiten", True) else 1)
                if lijst:
                    keus = random.choice(lijst[:6])
                    with self.lock:
                        if self.nu is None and not self.wachtrij and self.modus() == "muziek":
                            keus["wie"] = "🎵"
                            self.meld("🎵 Ik kies zelf: " + keus["titel"])
                            self.voeg_toe(keus)
                    return
        except Exception:
            pass
        finally:
            self.auto_bezig = False

    def meld(self, tekst):
        with self.lock:
            self.melding, self.melding_t = tekst, time.time()

    # ---- wachtrij: om de beurt
    def volgorde(self) -> list[dict]:
        """De wachtrij zoals hij gespeeld wordt: steeds iemand anders dan net, in volgorde van aanmelden."""
        if self.modus() == "muziek":
            return list(self.wachtrij)
        rest, uit, vorige = list(self.wachtrij), [], self.laatste_wie
        while rest:
            k = next((x for x in rest if x["wie"] != vorige), rest[0])
            uit.append(k); rest.remove(k); vorige = k["wie"]
        return uit

    def voeg_toe(self, item: dict) -> dict:
        with self.lock:
            self.teller += 1
            it = {"nr": self.teller, "id": item["id"], "titel": item.get("titel", "?")[:120], "plaatje": item.get("plaatje", ""),
                  "duur": int(item.get("duur") or 0), "wie": (item.get("wie") or "?")[:20], "kanaal": item.get("kanaal", "")[:60],
                  "insluiten": item.get("insluiten", True) is not False}
            self.ken_naam(it["wie"])
            if item.get("nu"):                                        # 0.2: "Nu zingen" - meteen spelen
                self.nu, self.laatste_wie = it, it["wie"]
                self.gespeeld = (self.gespeeld + [it["id"]])[-40:]
                self.tijd, self.tijd_t, self.speelt = 0.0, time.time(), False
                self.opdrachten.append({"actie": "laad", "id": it["id"]})
                plek = 0
            else:
                self.wachtrij.append(it)
                plek = None
        threading.Thread(target=self._tekst_voor, args=(it,), daemon=True).start()   # tekst alvast ophalen
        if self.nu is None:
            self.volgende()
        with self.lock:
            if plek is None:
                if self.nu is it:
                    plek = 0
                else:
                    v = self.volgorde()
                    plek = next((i + 1 for i, x in enumerate(v) if x is it), len(v))
        return dict(it, plek=plek)

    def weg(self, nr: int):
        with self.lock:
            self.wachtrij = [x for x in self.wachtrij if x["nr"] != nr]

    def volgende(self):
        with self.lock:
            v = self.volgorde()
            if not v:
                vorige = self.nu
                self.nu, self.speelt = None, False
                self.opdrachten.append({"actie": "stop"})
                if vorige and self.modus() == "muziek" and not self.auto_bezig:
                    self.auto_bezig = True
                    threading.Thread(target=self._auto_volgende, args=(vorige,), daemon=True).start()
                return
            self.nu = v[0]
            self.wachtrij.remove(self.nu)
            self.gespeeld = (self.gespeeld + [self.nu["id"]])[-40:]
            self.laatste_wie = self.nu["wie"]
            self.tijd, self.tijd_t, self.speelt = 0.0, time.time(), False
            self.opdrachten.append({"actie": "laad", "id": self.nu["id"]})
        if self.nu and self.nu["id"] not in self.teksten:
            threading.Thread(target=self._tekst_voor, args=(self.nu,), daemon=True).start()

    def _tekst_voor(self, it):
        if it["id"] in self.teksten:
            return
        eigen = self.liedje(it["id"]).get("zoek", "")
        t = haal_tekst(it["titel"], it.get("duur", 0), it.get("kanaal", ""), eigen)
        with self.lock:
            self.teksten[it["id"]] = t

    # ---- bediening
    def bedien(self, actie: str):
        with self.lock:
            if actie == "volgende":
                self.volgende(); return
            if actie in ("harder", "zachter"):
                self.volume = max(0, min(100, self.volume + (10 if actie == "harder" else -10)))
                self.opdrachten.append({"actie": "volume", "waarde": self.volume}); return
            if actie in ("pauze", "verder", "opnieuw"):
                self.opdrachten.append({"actie": actie})

    def zoek_tekst(self, q: str):
        """0.2: zelf de songtekst zoeken voor het liedje van nu ('Pastorale Ramses Shaffy'). Wordt onthouden."""
        q = (q or "").strip()[:80]
        with self.lock:
            if not self.nu or not q:
                return
            it = self.nu
            self.liedje(it["id"])["zoek"] = q
            self.teksten.pop(it["id"], None)
            self._schrijf("liedjes.json", self.extra)
        threading.Thread(target=self._tekst_voor, args=(it,), daemon=True).start()

    def liedje(self, id_):
        return self.extra.setdefault(id_, {"offset": 0.0, "duet": {}})

    def verschuif(self, delta: float):
        with self.lock:
            if self.nu:
                l = self.liedje(self.nu["id"])
                l["offset"] = round(max(-30.0, min(30.0, l["offset"] + delta)), 2)
                self._schrijf("liedjes.json", self.extra)

    def duet(self, regel: int, kleur: str):
        with self.lock:
            if self.nu:
                d = self.liedje(self.nu["id"])["duet"]
                if kleur:
                    d[str(regel)] = kleur
                else:
                    d.pop(str(regel), None)
                self._schrijf("liedjes.json", self.extra)

    # ---- de speler op de pc meldt zich
    def van_speler(self, tijd: float, speelt: bool, eind=False, fout=None):
        with self.lock:
            self.tijd, self.tijd_t, self.speelt = float(tijd or 0), time.time(), bool(speelt)
            if fout and self.nu and str(fout) in ("101", "150", "153") and self.nu.get("insluiten", True):
                self.nu["insluiten"] = False                          # 0.2: dan op de YouTube-pagina zelf spelen
                self.meld("Deze video mag alleen op YouTube zelf. Ik open de YouTube-pagina.")
                return
            if fout and self.nu:
                self.meld("Deze video lukt niet (%s). Ik sla hem over." % fout)
            if eind or fout:
                self.volgende()

    def voor_speler(self) -> dict:
        with self.lock:
            o, self.opdrachten = self.opdrachten, []
            return {"opdrachten": o, "nu": self.nu, "volume": self.volume}

    # ---- de stand voor iedereen
    def stand(self) -> dict:
        with self.lock:
            tijd = self.tijd + ((time.time() - self.tijd_t) if self.speelt else 0.0)
            nu = dict(self.nu) if self.nu else None
            if nu:
                t = self.teksten.get(nu["id"])
                nu["tekst_klaar"] = t is not None
                nu["offset"] = self.liedje(nu["id"])["offset"]
            return {"nu": nu, "tijd": round(tijd, 2), "speelt": self.speelt, "volume": self.volume,
                    "wachtrij": self.volgorde(), "namen": self.inst["namen"], "modus": self.modus(),
                    "melding": self.melding if time.time() - self.melding_t < 12 else ""}

    def tekst(self, id_) -> dict:
        with self.lock:
            t = self.teksten.get(id_)
            if t is None:
                return {"klaar": False}
            l = self.liedje(id_)
            return dict(t, klaar=True, offset=l["offset"], duet=l["duet"])
