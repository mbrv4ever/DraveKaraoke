package nl.dravenlock.karaoke;

// DraveKaraoke voor je mobiel (Android).
// Zoekt zelf in het eigen wifi-netwerk de pc waarop DraveKaraoke draait, onthoudt die,
// en toont dan de karaoke-pagina van die pc. Geen QR-code nodig. Alles blijft thuis.

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.ConnectivityManager;
import android.net.LinkAddress;
import android.net.LinkProperties;
import android.net.Network;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.text.InputType;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.TextView;

import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.Inet4Address;
import java.net.URL;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class MainActivity extends Activity {
    static final int POORT = 8765;
    static final boolean NL = Locale.getDefault().getLanguage().startsWith("nl");
    static String T(String nl, String en) { return NL ? nl : en; }

    final Handler ui = new Handler(Looper.getMainLooper());
    SharedPreferences prefs;
    FrameLayout wortel;
    WebView web;
    LinearLayout zoekScherm;
    TextView status;
    ProgressBar draai;
    LinearLayout knoppen;
    volatile boolean bezig = false;
    String adres = null;

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);   // scherm blijft aan tijdens het zingen
        prefs = getSharedPreferences("drave", MODE_PRIVATE);
        wortel = new FrameLayout(this);
        wortel.setBackgroundColor(Color.parseColor("#16131f"));
        maakWeb();
        maakZoekScherm();
        setContentView(wortel);
        String oud = prefs.getString("adres", null);
        if (oud != null) probeerOud(oud); else zoek();
    }

    // ---------- de karaoke-pagina
    void maakWeb() {
        web = new WebView(this);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setTextZoom(100);
        web.setBackgroundColor(Color.parseColor("#16131f"));
        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest r) {
                Uri u = r.getUrl();
                if (adres != null && u.toString().startsWith(adres)) return false;
                try { startActivity(new Intent(Intent.ACTION_VIEW, u)); } catch (Exception ignored) {}
                return true;                                     // links naar buiten: in de gewone browser
            }
            @Override
            public void onReceivedError(WebView v, WebResourceRequest r, WebResourceError e) {
                if (r.isForMainFrame()) {
                    toonZoek(T("De pc antwoordt niet.\nStaat DraveKaraoke aan op de pc?",
                               "The pc does not answer.\nIs DraveKaraoke running on the pc?"), false);
                }
            }
        });
        web.setVisibility(View.GONE);
        wortel.addView(web, new FrameLayout.LayoutParams(-1, -1));
    }

    void openKaraoke(String a) {
        adres = a;
        prefs.edit().putString("adres", a).apply();
        zoekScherm.setVisibility(View.GONE);
        zoekSchermHouder.setVisibility(View.GONE);              // anders ligt het (lege) zoekscherm over de pagina en vangt het elke tik
        web.setVisibility(View.VISIBLE);
        web.loadUrl(a + "/");
    }

    // ---------- het zoekscherm (grote letters)
    void maakZoekScherm() {
        ScrollView sv = new ScrollView(this);
        zoekScherm = new LinearLayout(this);
        zoekScherm.setOrientation(LinearLayout.VERTICAL);
        zoekScherm.setGravity(Gravity.CENTER_HORIZONTAL);
        int p = dp(22);
        zoekScherm.setPadding(p, dp(40), p, p);

        TextView kop = tekst("🎤 DraveKaraoke", 34, "#b59cff", true);
        zoekScherm.addView(kop);
        draai = new ProgressBar(this);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(dp(70), dp(70));
        lp.topMargin = dp(30); lp.bottomMargin = dp(20);
        zoekScherm.addView(draai, lp);
        status = tekst("", 24, "#f0f0f5", false);
        zoekScherm.addView(status);
        knoppen = new LinearLayout(this);
        knoppen.setOrientation(LinearLayout.VERTICAL);
        LinearLayout.LayoutParams kl = new LinearLayout.LayoutParams(-1, -2);
        kl.topMargin = dp(24);
        zoekScherm.addView(knoppen, kl);
        sv.addView(zoekScherm);
        wortel.addView(sv, new FrameLayout.LayoutParams(-1, -1));
        zoekSchermHouder = sv;
    }
    ScrollView zoekSchermHouder;

    TextView tekst(String t, int sp, String kleur, boolean vet) {
        TextView v = new TextView(this);
        v.setText(t);
        v.setTextSize(sp);
        v.setTextColor(Color.parseColor(kleur));
        v.setGravity(Gravity.CENTER);
        if (vet) v.setTypeface(Typeface.DEFAULT_BOLD);
        return v;
    }

    Button knop(String t, String rand, View.OnClickListener l) {
        Button k = new Button(this);
        k.setText(t);
        k.setAllCaps(false);
        k.setTextSize(24);
        k.setTextColor(Color.WHITE);
        k.setTypeface(Typeface.DEFAULT_BOLD);
        GradientDrawable g = new GradientDrawable();
        g.setColor(Color.parseColor("#221d33"));
        g.setStroke(dp(3), Color.parseColor(rand));
        g.setCornerRadius(dp(16));
        k.setBackground(g);
        k.setPadding(dp(12), dp(18), dp(12), dp(18));
        k.setOnClickListener(l);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-1, -2);
        lp.bottomMargin = dp(14);
        k.setLayoutParams(lp);
        return k;
    }

    void toonZoek(String bericht, boolean metDraai) {
        ui.post(() -> {
            web.setVisibility(View.GONE);
            zoekSchermHouder.setVisibility(View.VISIBLE);
            zoekScherm.setVisibility(View.VISIBLE);
            draai.setVisibility(metDraai ? View.VISIBLE : View.GONE);
            status.setText(bericht);
            knoppen.removeAllViews();
            if (!metDraai) {
                knoppen.addView(knop(T("🔍 Opnieuw zoeken", "🔍 Search again"), "#5ee0c8", v -> zoek()));
                knoppen.addView(knop(T("⌨ Adres zelf typen", "⌨ Type the address"), "#4a3d66", v -> zelfTypen()));
                knoppen.addView(knop(T("❤ Doneer (PayPal)", "❤ Donate (PayPal)"), "#4a3d66", v -> {
                    try { startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("https://paypal.me/roger076"))); } catch (Exception ignored) {}
                }));
                knoppen.addView(tekst("dravenlock.nl · service@dravenlock.nl", 15, "#9a93b8", false));
            }
        });
    }

    void zelfTypen() {
        knoppen.removeAllViews();
        status.setText(T("Typ het adres dat rechts op de pc staat.\nBijvoorbeeld: 192.168.1.20",
                         "Type the address shown on the right of the pc.\nFor example: 192.168.1.20"));
        EditText in = new EditText(this);
        in.setTextSize(26);
        in.setTextColor(Color.WHITE);
        in.setHintTextColor(Color.parseColor("#7d7798"));
        in.setHint("192.168.1.20");
        in.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_URI);
        knoppen.addView(in);
        knoppen.addView(knop(T("✔ Verbinden", "✔ Connect"), "#5ee0c8", v -> {
            String t = in.getText().toString().trim().replace("http://", "").replaceAll("/.*$", "");
            if (t.isEmpty()) return;
            if (!t.contains(":")) t = t + ":" + POORT;
            probeerOud("http://" + t);
        }));
    }

    // ---------- de pc zoeken
    void probeerOud(String a) {
        toonZoek(T("Even verbinden met de pc...", "Connecting to the pc..."), true);
        new Thread(() -> {
            if (isKaraoke(a, 2500)) ui.post(() -> openKaraoke(a));
            else zoek();
        }).start();
    }

    void zoek() {
        if (bezig) return;
        bezig = true;
        toonZoek(T("Ik zoek de pc met DraveKaraoke\nin je wifi...", "Looking for the pc with DraveKaraoke\non your wifi..."), true);
        new Thread(() -> {
            String mijnIp = eigenIp();
            if (mijnIp == null) {
                bezig = false;
                toonZoek(T("Je mobiel zit niet op wifi.\nZet wifi aan, op hetzelfde netwerk als de pc.",
                           "Your phone is not on wifi.\nTurn on wifi, on the same network as the pc."), false);
                return;
            }
            String basis = mijnIp.substring(0, mijnIp.lastIndexOf('.') + 1);
            List<String> gevonden = Collections.synchronizedList(new ArrayList<>());
            ExecutorService pool = Executors.newFixedThreadPool(48);
            for (int i = 1; i < 255; i++) {
                final String a = "http://" + basis + i + ":" + POORT;
                pool.execute(() -> { if (isKaraoke(a, 700)) gevonden.add(a); });
            }
            pool.shutdown();
            try { pool.awaitTermination(25, TimeUnit.SECONDS); } catch (InterruptedException ignored) {}
            bezig = false;
            if (gevonden.isEmpty()) {
                toonZoek(T("Ik vind de pc niet.\n\n• Staat DraveKaraoke aan op de pc?\n• Zit je mobiel op dezelfde wifi?",
                           "I can't find the pc.\n\n• Is DraveKaraoke running on the pc?\n• Is your phone on the same wifi?"), false);
            } else if (gevonden.size() == 1) {
                ui.post(() -> openKaraoke(gevonden.get(0)));
            } else {
                ui.post(() -> kiesUit(gevonden));
            }
        }).start();
    }

    void kiesUit(List<String> lijst) {
        toonZoek(T("Ik vond meer pc's. Welke?", "I found more pcs. Which one?"), false);
        ui.post(() -> {
            knoppen.removeAllViews();
            for (String a : lijst) {
                knoppen.addView(knop("💻 " + a.replace("http://", "").replace(":" + POORT, ""), "#5ee0c8", v -> openKaraoke(a)));
            }
        });
    }

    static boolean isKaraoke(String a, int ms) {
        HttpURLConnection c = null;
        try {
            c = (HttpURLConnection) new URL(a + "/api/stand").openConnection();
            c.setConnectTimeout(ms);
            c.setReadTimeout(ms * 2);
            if (c.getResponseCode() != 200) return false;
            InputStream in = c.getInputStream();
            java.io.ByteArrayOutputStream bo = new java.io.ByteArrayOutputStream();
            byte[] buf = new byte[4096];
            int n;
            while ((n = in.read(buf)) > 0 && bo.size() < 65536) bo.write(buf, 0, n);
            String s = bo.toString("UTF-8");
            return s.contains("\"wachtrij\"") && s.contains("\"namen\"");
        } catch (Exception e) {
            return false;
        } finally {
            if (c != null) c.disconnect();
        }
    }

    String eigenIp() {
        try {
            ConnectivityManager cm = (ConnectivityManager) getSystemService(CONNECTIVITY_SERVICE);
            Network n = cm.getActiveNetwork();
            if (n == null) return null;
            LinkProperties lp = cm.getLinkProperties(n);
            if (lp == null) return null;
            for (LinkAddress la : lp.getLinkAddresses()) {
                if (la.getAddress() instanceof Inet4Address && !la.getAddress().isLoopbackAddress()) {
                    String ip = la.getAddress().getHostAddress();
                    if (ip.startsWith("192.168.") || ip.startsWith("10.") || ip.matches("^172\\.(1[6-9]|2\\d|3[01])\\..*")) return ip;
                }
            }
        } catch (Exception ignored) {}
        return null;
    }

    int dp(int v) { return Math.round(v * getResources().getDisplayMetrics().density); }

    @Override
    public void onBackPressed() {
        if (web.getVisibility() == View.VISIBLE && web.canGoBack()) web.goBack();
        else super.onBackPressed();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (web != null) web.onResume();
    }

    @Override
    protected void onPause() {
        if (web != null) web.onPause();
        super.onPause();
    }
}
