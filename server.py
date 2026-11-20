# -*- coding: utf-8 -*-
"""DraveKaraoke - klein webservertje op de pc. De mobieltjes openen de pagina via het eigen wifi-netwerk.
Niets gaat via een cloud van ons; alleen thuis, op het eigen netwerk."""
from __future__ import annotations

import json
import os
import socket
import threading
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler


def eigen_ip() -> str:
    """Het adres van deze pc in het thuisnetwerk (bijv. 192.168.1.20)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def maak_server(kar, web_map: str, poort: int):
    import karaoke

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _json(self, d, code=200):
            b = json.dumps(d, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def _bestand(self, naam, soort):
            try:
                with open(os.path.join(web_map, naam), "rb") as f:
                    b = f.read()
            except Exception:
                self.send_error(404); return
            self.send_response(200)
            self.send_header("Content-Type", soort)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def _lijf(self):
            n = int(self.headers.get("Content-Length") or 0)
            try:
                return json.loads(self.rfile.read(n).decode("utf-8")) if n else {}
            except Exception:
                return {}

        def do_GET(self):
            u = urllib.parse.urlparse(self.path)
            q = urllib.parse.parse_qs(u.query)
            p = u.path
            if p in ("/", "/mobiel"):
                return self._bestand("mobiel.html", "text/html; charset=utf-8")
            if p == "/speler":
                return self._bestand("speler.html", "text/html; charset=utf-8")
            if p in ("/icon.png", "/manifest.json"):
                return self._bestand(p[1:], "image/png" if p.endswith(".png") else "application/json")
            if p in ("/app", "/DraveKaraoke.apk"):                       # 0.2: de Android-app downloaden
                apk = os.path.join(os.path.dirname(web_map.rstrip("\\/")), "DraveKaraoke.apk")
                if not os.path.exists(apk):
                    apk = os.path.join(os.path.dirname(os.path.dirname(web_map.rstrip("\\/"))), "DraveKaraoke.apk")
                try:
                    with open(apk, "rb") as f:
                        b = f.read()
                except Exception:
                    self.send_error(404); return
                self.send_response(200)
                self.send_header("Content-Type", "application/vnd.android.package-archive")
                self.send_header("Content-Disposition", 'attachment; filename="DraveKaraoke.apk"')
                self.send_header("Content-Length", str(len(b)))
                self.end_headers(); self.wfile.write(b); return
            if p == "/api/stand":
                return self._json(kar.stand())
            if p == "/api/tekst":
                return self._json(kar.tekst((q.get("id") or [""])[0]))
            if p == "/api/zoek":
                try:
                    return self._json({"lijst": karaoke.zoek((q.get("q") or [""])[0])})
                except Exception as ex:
                    return self._json({"lijst": [], "fout": str(ex)})
            if p == "/api/speler":
                return self._json(kar.voor_speler())
            self.send_error(404)

        def do_POST(self):
            p = urllib.parse.urlparse(self.path).path
            d = self._lijf()
            if p == "/api/voeg":
                return self._json(kar.voeg_toe(d))
            if p == "/api/weg":
                kar.weg(int(d.get("nr") or 0)); return self._json({"ok": True})
            if p == "/api/bedien":
                kar.bedien(str(d.get("actie") or "")); return self._json({"ok": True})
            if p == "/api/offset":
                kar.verschuif(float(d.get("delta") or 0)); return self._json({"ok": True})
            if p == "/api/duet":
                kar.duet(int(d.get("regel") or 0), str(d.get("kleur") or "")); return self._json({"ok": True})
            if p == "/api/tekstzoek":                                   # 0.2: zelf de tekst zoeken
                kar.zoek_tekst(str(d.get("q") or "")); return self._json({"ok": True})
            if p == "/api/modus":                                       # 0.2: karaoke of muziek
                kar.zet_modus(str(d.get("modus") or "")); return self._json({"ok": True})
            if p == "/api/naam":
                kar.ken_naam(str(d.get("naam") or "")); return self._json({"ok": True})
            if p == "/api/speler":
                kar.van_speler(d.get("tijd", 0), d.get("speelt", False), d.get("eind", False), d.get("fout"))
                return self._json({"ok": True})
            self.send_error(404)

    srv = ThreadingHTTPServer(("0.0.0.0", poort), H)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv
