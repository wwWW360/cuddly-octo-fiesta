import pathlib
def w(p, s):
    f = pathlib.Path(p); f.parent.mkdir(parents=True, exist_ok=True); f.write_text(s, encoding='utf-8')

SVG = r'''<defs>
<linearGradient id="hair" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e8b060"/><stop offset="1" stop-color="#c4684a"/></linearGradient>
<radialGradient id="orb"><stop offset="0" stop-color="#fff6c8"/><stop offset=".6" stop-color="#ffc468"/><stop offset="1" stop-color="#f08c48"/></radialGradient>
</defs>
<ellipse cx="100" cy="228" rx="52" ry="8" fill="#000" opacity=".12"/>
<g class="bob">
<path d="M52 222 C50 168 66 140 100 138 C134 140 150 168 148 222 Z" fill="#efe1c6" stroke="#b89a76" stroke-width="2"/>
<path d="M70 170 q8 6 0 14 M130 168 q-8 6 0 14 M96 150 v60" stroke="#d8c4a0" stroke-width="2" fill="none" stroke-linecap="round"/>
<circle cx="100" cy="96" r="40" fill="#f8dcc4" stroke="#b89a76" stroke-width="2"/>
<path d="M58 92 C54 52 82 40 104 44 C132 44 150 62 142 96 C136 78 128 70 112 70 C100 74 90 66 80 72 C68 78 64 86 58 92Z" fill="url(#hair)"/>
<path d="M66 70 q-10 8 -8 20 M138 66 q12 10 6 26 M92 48 q6 14 -4 22" stroke="#a8502e" stroke-width="2.5" fill="none" stroke-linecap="round"/>
<ellipse class="eye" cx="84" cy="100" rx="4.5" ry="6" fill="#3a2f2a"/>
<ellipse class="eye" cx="116" cy="100" rx="4.5" ry="6" fill="#3a2f2a"/>
<path d="M90 116 q10 8 20 0" stroke="#a8604a" stroke-width="2.5" fill="none" stroke-linecap="round"/>
<ellipse cx="74" cy="112" rx="6" ry="3.5" fill="#f0a090" opacity=".5"/><ellipse cx="126" cy="112" rx="6" ry="3.5" fill="#f0a090" opacity=".5"/>
<circle class="halo" cx="100" cy="178" r="26" fill="#ffc468" opacity=".35"/>
<circle cx="100" cy="178" r="15" fill="url(#orb)"/>
<circle cx="76" cy="182" r="7" fill="#f8dcc4" stroke="#b89a76" stroke-width="1.5"/><circle cx="124" cy="182" r="7" fill="#f8dcc4" stroke="#b89a76" stroke-width="1.5"/>
</g>
<text class="ff" x="78" y="160" style="animation-delay:0s">字</text>
<text class="ff" x="116" y="164" style="animation-delay:2s">a</text>
<text class="ff" x="98" y="156" style="animation-delay:4s">光</text>'''

w('settings.gradle', r'''pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement { repositories { google(); mavenCentral() } }
rootProject.name = 'DeskPet'
include ':app'
''')
w('build.gradle', r'''plugins { id 'com.android.application' version '8.5.2' apply false }
''')
w('gradle.properties', r'''org.gradle.jvmargs=-Xmx3g
android.useAndroidX=false
''')
w('app/build.gradle', r'''plugins { id 'com.android.application' }
android {
    namespace 'com.deskpet.app'
    compileSdk 34
    defaultConfig {
        applicationId 'com.deskpet.app'
        minSdk 24
        targetSdk 34
        versionCode 3
        versionName '0.3'
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }
}
''')
w('app/src/main/AndroidManifest.xml', r'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_SPECIAL_USE"/>
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
    <uses-permission android:name="android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS"/>
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
    <application android:label="小灯" android:allowBackup="true"
        android:theme="@android:style/Theme.DeviceDefault.Light.NoActionBar">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
        <receiver android:name=".WakeReceiver" android:exported="false"/>
        <receiver android:name=".BootReceiver" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED"/>
            </intent-filter>
        </receiver>
        <service android:name=".OverlayService" android:exported="false"
            android:foregroundServiceType="specialUse">
            <property android:name="android.app.PROPERTY_SPECIAL_USE_FGS_SUBTYPE"
                android:value="floating desk pet"/>
        </service>
    </application>
</manifest>
''')
w('app/src/main/java/com/deskpet/app/MainActivity.java', r'''package com.deskpet.app;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.PowerManager;
import android.provider.Settings;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity {
    private WebView web;
    private Button toggle;
    private Button step;
    private Button battery;
    private TextView status;
    private final Handler ui = new Handler(Looper.getMainLooper());
    private final Runnable tick = new Runnable() {
        @Override
        public void run() {
            refresh();
            ui.postDelayed(this, 3000);
        }
    };

    private int dp(int v) {
        return (int) (v * getResources().getDisplayMetrics().density);
    }

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        if (Build.VERSION.SDK_INT >= 33) {
            requestPermissions(new String[]{"android.permission.POST_NOTIFICATIONS"}, 1);
        }
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);

        LinearLayout bar = new LinearLayout(this);
        bar.setOrientation(LinearLayout.HORIZONTAL);
        bar.setPadding(dp(12), dp(28), dp(12), dp(4));
        Button on = new Button(this);
        on.setText("显示悬浮小灯");
        Button off = new Button(this);
        off.setText("关闭悬浮小灯");
        bar.addView(on, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));
        bar.addView(off, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));

        final Button wakeBtn = new Button(this);
        wakeBtn.setText("自动唤醒设置 ▾");
        LinearLayout.LayoutParams wl = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        wl.setMargins(dp(12), 0, dp(12), dp(4));

        toggle = new Button(this);
        step = new Button(this);
        battery = new Button(this);
        status = new TextView(this);
        status.setTextSize(12);
        status.setPadding(dp(4), dp(8), dp(4), dp(8));
        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp(12), 0, dp(12), 0);
        panel.addView(toggle);
        panel.addView(step);
        panel.addView(battery);
        panel.addView(status);
        final ScrollView sv = new ScrollView(this);
        sv.addView(panel);
        sv.setVisibility(View.GONE);

        web = new WebView(this);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        web.setBackgroundColor(Color.TRANSPARENT);
        web.setWebViewClient(new WebViewClient());
        web.loadUrl("file:///android_asset/index.html");

        root.addView(bar);
        root.addView(wakeBtn, wl);
        root.addView(sv, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(300)));
        root.addView(web, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));
        setContentView(root);

        on.setOnClickListener(v -> startPet());
        off.setOnClickListener(v -> stopService(new Intent(this, OverlayService.class)));
        wakeBtn.setOnClickListener(v -> {
            boolean show = sv.getVisibility() != View.VISIBLE;
            sv.setVisibility(show ? View.VISIBLE : View.GONE);
            wakeBtn.setText(show ? "自动唤醒设置 ▴" : "自动唤醒设置 ▾");
            refresh();
        });
        toggle.setOnClickListener(v -> {
            if (Wake.on(this)) {
                Wake.stop(this);
            } else {
                Wake.start(this);
            }
            refresh();
        });
        step.setOnClickListener(v -> {
            int cur = Wake.interval(this);
            int idx = 0;
            for (int i = 0; i < Wake.STEPS.length; i++) {
                if (Wake.STEPS[i] == cur) {
                    idx = i;
                }
            }
            Wake.setInterval(this, Wake.STEPS[(idx + 1) % Wake.STEPS.length]);
            refresh();
        });
        battery.setOnClickListener(v -> askBattery());
        refresh();
    }

    @Override
    protected void onResume() {
        super.onResume();
        ui.post(tick);
    }

    @Override
    protected void onPause() {
        ui.removeCallbacks(tick);
        super.onPause();
    }

    private void refresh() {
        boolean on = Wake.on(this);
        toggle.setText(on ? "关闭自动唤醒" : "开启自动唤醒");
        int cur = Wake.interval(this);
        step.setText("间隔：" + Wake.label(cur) + "（点一下切换" + (cur == 1 ? "；1 分钟只用来测试" : "") + "）");
        PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
        boolean ok = pm.isIgnoringBatteryOptimizations(getPackageName());
        battery.setText(ok ? "电池优化：已放行" : "电池优化：未放行（点这里去放行）");
        long next = Wake.next(this);
        String head = on && next > 0 ? "下一次预计：" + Wake.fmt(next) : "自动唤醒：未开启";
        status.setText(head + "\n\n" + Wake.logText(this));
    }

    private void askBattery() {
        PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
        if (pm.isIgnoringBatteryOptimizations(getPackageName())) {
            Toast.makeText(this, "已经在电池优化白名单里了", Toast.LENGTH_SHORT).show();
            return;
        }
        try {
            startActivity(new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,
                    Uri.parse("package:" + getPackageName())));
        } catch (Exception e) {
            startActivity(new Intent(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS));
        }
    }

    private void startPet() {
        if (!Settings.canDrawOverlays(this)) {
            Toast.makeText(this, "请允许小灯显示在其他应用上层，设置好后回来再点一次", Toast.LENGTH_LONG).show();
            startActivity(new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:" + getPackageName())));
            return;
        }
        Intent i = new Intent(this, OverlayService.class);
        if (Build.VERSION.SDK_INT >= 26) {
            startForegroundService(i);
        } else {
            startService(i);
        }
        moveTaskToBack(true);
    }
}
''')
w('app/src/main/java/com/deskpet/app/OverlayService.java', r'''package com.deskpet.app;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.os.Build;
import android.os.IBinder;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewConfiguration;
import android.view.WindowManager;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;

public class OverlayService extends Service {
    private static final String CH = "pet";
    private static final String STOP = "com.deskpet.app.STOP";
    private WindowManager wm;
    static volatile OverlayService instance;
    private FrameLayout root;
    private WebView web;

    @Override
    public IBinder onBind(Intent i) {
        return null;
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null && STOP.equals(intent.getAction())) {
            stopSelf();
            return START_NOT_STICKY;
        }
        startForeground(1, buildNotification());
        if (root == null) {
            showOverlay();
        }
        return START_NOT_STICKY;
    }

    private Notification buildNotification() {
        NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        Notification.Builder nb;
        if (Build.VERSION.SDK_INT >= 26) {
            nm.createNotificationChannel(new NotificationChannel(CH, "小灯", NotificationManager.IMPORTANCE_LOW));
            nb = new Notification.Builder(this, CH);
        } else {
            nb = new Notification.Builder(this);
        }
        Intent stop = new Intent(this, OverlayService.class).setAction(STOP);
        PendingIntent pi = PendingIntent.getService(this, 0, stop,
                PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
        return nb.setSmallIcon(android.R.drawable.ic_menu_info_details)
                .setContentTitle("小灯在桌面上")
                .setContentText("点一下这里就关掉它")
                .setContentIntent(pi)
                .build();
    }

    private void showOverlay() {
        wm = (WindowManager) getSystemService(WINDOW_SERVICE);
        final float d = getResources().getDisplayMetrics().density;
        int type = Build.VERSION.SDK_INT >= 26
                ? WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
                : WindowManager.LayoutParams.TYPE_PHONE;
        final WindowManager.LayoutParams lp = new WindowManager.LayoutParams(
                (int) (172 * d), (int) (240 * d), type,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
                        | WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS
                        | WindowManager.LayoutParams.FLAG_HARDWARE_ACCELERATED,
                PixelFormat.TRANSLUCENT);
        lp.gravity = Gravity.TOP | Gravity.START;
        lp.x = (int) (16 * d);
        lp.y = (int) (240 * d);

        root = new FrameLayout(this);
        web = new WebView(this);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        web.setBackgroundColor(Color.TRANSPARENT);
        web.setWebViewClient(new WebViewClient());
        web.loadUrl("file:///android_asset/overlay.html");

        View cover = new View(this);
        final int slop = ViewConfiguration.get(this).getScaledTouchSlop();
        cover.setOnTouchListener(new View.OnTouchListener() {
            float downX;
            float downY;
            int startX;
            int startY;
            boolean moved;

            @Override
            public boolean onTouch(View v, MotionEvent e) {
                switch (e.getActionMasked()) {
                    case MotionEvent.ACTION_DOWN:
                        downX = e.getRawX();
                        downY = e.getRawY();
                        startX = lp.x;
                        startY = lp.y;
                        moved = false;
                        return true;
                    case MotionEvent.ACTION_MOVE:
                        float mx = e.getRawX() - downX;
                        float my = e.getRawY() - downY;
                        if (Math.abs(mx) > slop || Math.abs(my) > slop) {
                            moved = true;
                        }
                        if (moved) {
                            lp.x = startX + (int) mx;
                            lp.y = startY + (int) my;
                            wm.updateViewLayout(root, lp);
                        }
                        return true;
                    case MotionEvent.ACTION_UP:
                        if (!moved) {
                            web.evaluateJavascript("poke()", null);
                        }
                        return true;
                    default:
                        return false;
                }
            }
        });
        root.addView(web, new FrameLayout.LayoutParams(-1, -1));
        root.addView(cover, new FrameLayout.LayoutParams(-1, -1));
        wm.addView(root, lp);
        instance = this;
    }

    void say(final String text) {
        final WebView w = web;
        if (w == null) {
            return;
        }
        final String js = "say(" + org.json.JSONObject.quote(text) + ")";
        w.post(new Runnable() {
            @Override
            public void run() {
                w.evaluateJavascript(js, null);
            }
        });
    }

    @Override
    public void onDestroy() {
        instance = null;
        if (root != null && wm != null) {
            wm.removeView(root);
            root = null;
        }
        if (web != null) {
            web.destroy();
            web = null;
        }
        super.onDestroy();
    }
}
''')
w('app/src/main/java/com/deskpet/app/Wake.java', r'''package com.deskpet.app;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class Wake {
    static final String ACTION = "com.deskpet.app.WAKE";
    static final int[] STEPS = {1, 15, 30, 60, 180};

    static SharedPreferences sp(Context c) {
        return c.getSharedPreferences("wake", Context.MODE_PRIVATE);
    }

    static boolean on(Context c) {
        return sp(c).getBoolean("on", false);
    }

    static int interval(Context c) {
        return sp(c).getInt("interval", 30);
    }

    static long next(Context c) {
        return sp(c).getLong("next", 0L);
    }

    static String fmt(long t) {
        return new SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(new Date(t));
    }

    static String label(int min) {
        if (min >= 60) {
            return (min / 60) + " 小时";
        }
        return min + " 分钟";
    }

    private static PendingIntent pending(Context c) {
        Intent i = new Intent(c, WakeReceiver.class).setAction(ACTION);
        return PendingIntent.getBroadcast(c, 0, i,
                PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
    }

    static void schedule(Context c) {
        AlarmManager am = (AlarmManager) c.getSystemService(Context.ALARM_SERVICE);
        long at = System.currentTimeMillis() + interval(c) * 60000L;
        am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, at, pending(c));
        sp(c).edit().putLong("next", at).apply();
    }

    static void start(Context c) {
        sp(c).edit().putBoolean("on", true).apply();
        log(c, "开启自动唤醒，间隔 " + label(interval(c)));
        schedule(c);
    }

    static void stop(Context c) {
        AlarmManager am = (AlarmManager) c.getSystemService(Context.ALARM_SERVICE);
        am.cancel(pending(c));
        sp(c).edit().putBoolean("on", false).putLong("next", 0L).apply();
        log(c, "关闭自动唤醒");
    }

    static void setInterval(Context c, int min) {
        sp(c).edit().putInt("interval", min).apply();
        if (on(c)) {
            log(c, "间隔改为 " + label(min));
            schedule(c);
        }
    }

    static synchronized void log(Context c, String s) {
        String old = sp(c).getString("log", "");
        StringBuilder sb = new StringBuilder(fmt(System.currentTimeMillis()) + "  " + s);
        if (!old.isEmpty()) {
            String[] parts = old.split("\n");
            for (int i = 0; i < parts.length && i < 11; i++) {
                sb.append("\n").append(parts[i]);
            }
        }
        sp(c).edit().putString("log", sb.toString()).apply();
    }

    static String logText(Context c) {
        String s = sp(c).getString("log", "");
        return s.isEmpty() ? "还没有记录" : s;
    }
}
''')
w('app/src/main/java/com/deskpet/app/WakeReceiver.java', r'''package com.deskpet.app;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

public class WakeReceiver extends BroadcastReceiver {
    private static final String[] LINES = {
            "我醒了一下，你忙你的。",
            "到点啦，我在。",
            "嗯，睡醒了，一切都好。",
            "路过看一眼，你继续。"
    };

    @Override
    public void onReceive(Context c, Intent intent) {
        if (!Wake.on(c)) {
            return;
        }
        long expected = Wake.next(c);
        long now = System.currentTimeMillis();
        long late = expected > 0 ? Math.max(0L, (now - expected) / 1000L) : 0L;
        String text = LINES[(int) ((now / 1000L) % LINES.length)];
        OverlayService s = OverlayService.instance;
        String where = s != null ? "小灯在桌面上" : "小灯没在桌面上";
        Wake.log(c, "醒了，比预计晚 " + late + " 秒；" + where);
        Wake.schedule(c);
        if (s != null) {
            s.say(text);
        }
        notifyWake(c, text);
    }

    private void notifyWake(Context c, String text) {
        NotificationManager nm = (NotificationManager) c.getSystemService(Context.NOTIFICATION_SERVICE);
        Notification.Builder nb;
        if (Build.VERSION.SDK_INT >= 26) {
            nm.createNotificationChannel(new NotificationChannel("wake", "自动唤醒", NotificationManager.IMPORTANCE_LOW));
            nb = new Notification.Builder(c, "wake");
        } else {
            nb = new Notification.Builder(c);
        }
        nb.setSmallIcon(android.R.drawable.ic_menu_recent_history)
                .setContentTitle("小灯醒了")
                .setContentText(text)
                .setAutoCancel(true);
        nm.notify(2, nb.build());
    }
}
''')
w('app/src/main/java/com/deskpet/app/BootReceiver.java', r'''package com.deskpet.app;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context c, Intent intent) {
        if (Wake.on(c)) {
            Wake.log(c, "手机重启后，重新安排了唤醒");
            Wake.schedule(c);
        }
    }
}
''')
w('app/src/main/assets/index.html', r'''<!doctype html>
<html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>小灯</title>
<style>
:root{--fg:#3a2f2a;--card:#fffaf0;--line:#b89a76;--accent:#c0603a}
html,body{margin:0;height:100%;background:linear-gradient(#f8ecd8,#efc9a0);color:var(--fg);font-family:sans-serif}
main{max-width:480px;margin:0 auto;padding:28px 14px;display:flex;flex-direction:column;align-items:center;gap:12px}
h1{font-size:18px;margin:0;letter-spacing:2px}
#bubble{min-height:56px;max-width:92%;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:10px 14px;font-size:15px;line-height:1.55;text-align:center;position:relative}
#bubble::after{content:"";position:absolute;bottom:-8px;left:50%;margin-left:-8px;border:8px solid transparent;border-bottom:0;border-top-color:var(--line)}
#pet{width:230px;height:276px;-webkit-tap-highlight-color:transparent;user-select:none}
.bob{animation:bob 3.6s ease-in-out infinite;transform-origin:100px 230px}
@keyframes bob{50%{transform:translateY(-5px)}}
.eye{transform-box:fill-box;transform-origin:center;animation:blink 5s infinite}
@keyframes blink{0%,94%,100%{transform:scaleY(1)}97%{transform:scaleY(.1)}}
.focus .eye{animation:none;transform:scaleY(.3)}
.halo{animation:glow 2.8s ease-in-out infinite;transform-box:fill-box;transform-origin:center}
@keyframes glow{50%{opacity:.55;transform:scale(1.18)}}
.ff{font-size:11px;fill:var(--accent);opacity:0;animation:fly 6s linear infinite}
@keyframes fly{0%{opacity:0;transform:translateY(0)}20%{opacity:.9}100%{opacity:0;transform:translateY(-70px)}}
.poke{animation:poke .3s}
@keyframes poke{40%{transform:scale(.95,1.04)}}
.row{display:flex;gap:10px;align-items:center}
button{font:inherit;font-size:14px;color:var(--fg);background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 14px}
#clock{font-variant-numeric:tabular-nums;font-size:15px;min-width:52px}
.note{font-size:12px;opacity:.6;text-align:center}
</style></head><body><main>
<h1>小灯</h1>
<div id="bubble">戳戳我。</div>
<svg id="pet" viewBox="0 0 200 240">
@@SVG@@
</svg>
<div class="row"><button id="focus">一起专注 25 分钟</button><span id="clock"></span></div>
<div class="note">这个版本在测试自动唤醒：不联网，也不聊天。</div>
</main>
<script>
var $=function(i){return document.getElementById(i)};
var h=new Date().getHours();
var hi=h<5?'这么晚了，还没睡呀。':h<11?'早上好。':h<14?'中午了，记得吃点东西。':h<18?'下午好。':h<22?'晚上好。':'夜深了，别熬太久。';
var lines=['在呢。','嗯？','戳我干嘛，有点痒。','我在旁边。','今天过得怎么样？','喝口水吧。','慢慢来就好。','我的小灯还亮着。','不急，一件一件来。','你忙的话，我就安静待着。'];
var last=-1,endAt=0,tm=null;
$('bubble').textContent=hi;
$('pet').onclick=function(){
  var p=$('pet');p.classList.remove('poke');void p.getBoundingClientRect();p.classList.add('poke');
  var i;do{i=Math.floor(Math.random()*lines.length)}while(i===last);last=i;
  $('bubble').textContent=lines[i];
};
function tick(){
  var left=Math.max(0,endAt-Date.now()),m=Math.floor(left/60000),s=Math.floor(left/1000)%60;
  $('clock').textContent=(m<10?'0':'')+m+':'+(s<10?'0':'')+s;
  if(left<=0){stop();$('bubble').textContent='时间到啦，歇一会儿吧。'}
}
function stop(){clearInterval(tm);tm=null;endAt=0;$('pet').classList.remove('focus');$('focus').textContent='一起专注 25 分钟';$('clock').textContent=''}
$('focus').onclick=function(){
  if(tm){stop();$('bubble').textContent='先停在这儿，没关系。';return}
  endAt=Date.now()+25*60000;$('pet').classList.add('focus');$('focus').textContent='停止专注';
  $('bubble').textContent='嗯，我在旁边陪着，不吵你。';tick();tm=setInterval(tick,1000);
};
</script></body></html>
'''.replace('@@SVG@@', SVG))
w('app/src/main/assets/overlay.html', r'''<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--accent:#c0603a}
html,body{margin:0;background:transparent;overflow:hidden;font-family:sans-serif}
body{display:flex;flex-direction:column;align-items:center}
#b{box-sizing:border-box;margin-top:4px;width:172px;height:60px;display:flex;align-items:center;justify-content:center;background:#fffaf0;border:1px solid #b89a76;border-radius:12px;padding:4px 10px;font-size:13px;line-height:1.45;color:#3a2f2a;text-align:center;opacity:0;transition:opacity .3s}
#b.on{opacity:1}
#pet{width:140px;height:168px;margin-top:4px}
.bob{animation:bob 3.6s ease-in-out infinite;transform-origin:100px 230px}
@keyframes bob{50%{transform:translateY(-5px)}}
.eye{transform-box:fill-box;transform-origin:center;animation:blink 5s infinite}
@keyframes blink{0%,94%,100%{transform:scaleY(1)}97%{transform:scaleY(.1)}}
.halo{animation:glow 2.8s ease-in-out infinite;transform-box:fill-box;transform-origin:center}
@keyframes glow{50%{opacity:.55;transform:scale(1.18)}}
.ff{font-size:11px;fill:var(--accent);opacity:0;animation:fly 6s linear infinite}
@keyframes fly{0%{opacity:0;transform:translateY(0)}20%{opacity:.9}100%{opacity:0;transform:translateY(-70px)}}
.poke{animation:poke .3s}
@keyframes poke{40%{transform:scale(.95,1.04)}}
</style></head><body>
<div id="b"></div>
<svg id="pet" viewBox="0 0 200 240">
@@SVG@@
</svg>
<script>
var b=document.getElementById('b'),p=document.getElementById('pet'),t=null,last=-1;
var h=new Date().getHours();
var hi=h<5?'这么晚了，还没睡呀。':h<11?'早上好。':h<14?'中午了，记得吃点东西。':h<18?'下午好。':h<22?'晚上好。':'夜深了，别熬太久。';
var lines=['在呢。','嗯？','戳我干嘛，有点痒。','我在旁边。','今天过得怎么样？','喝口水吧。','慢慢来就好。','我的小灯还亮着。','不急，一件一件来。','你忙的话，我就安静待着。'];
function say(x){b.textContent=x;b.className='on';clearTimeout(t);t=setTimeout(function(){b.className=''},4000)}
function poke(){
  p.classList.remove('poke');void p.getBoundingClientRect();p.classList.add('poke');
  var i;do{i=Math.floor(Math.random()*lines.length)}while(i===last);last=i;say(lines[i]);
}
say(hi);
</script></body></html>
'''.replace('@@SVG@@', SVG))
