from pathlib import Path

def replace_once(path, old, new):
    p = Path(path)
    s = p.read_text()
    if old not in s:
        raise SystemExit("Patch context not found: " + str(path) + " :: " + old[:80])
    p.write_text(s.replace(old, new, 1))

html = Path("app/src/main/assets/index.html")
s = html.read_text()
old = '''  <div class="scr" id="files">
    <button class="btn p" onclick="A.pickFolder()">📁 إضافة مجلد</button>
    <div id="fv"></div><div class="list" id="fl"></div>
  </div>'''
new = '''  <div class="scr" id="files">
    <button class="btn p" onclick="A.pickFolder()">📁 إضافة مجلد</button>
    <p style="margin:10px 2px 6px">خصص المجلدات للأيقونة التي تريدها:</p>
    <select id="folderTarget" class="btn" style="width:100%;margin-bottom:10px" onchange="renderFiles()"></select>
    <div id="folderHint" style="font-size:13px;opacity:.85;margin-bottom:8px">ضع علامة صح بجانب كل مجلد تريد ربطه بهذه الأيقونة</div>
    <div id="fv"></div><div class="list" id="fl"></div>
  </div>'''
if old not in s: raise SystemExit("HTML file manager layout not found")
s = s.replace(old, new, 1)

start = s.index("// Files (multiple saved folders)")
end = s.index("// Launch other apps", start)
manager = r'''// File manager: independently assign one or more folders to each app section.
let FP=[];
const FOLDER_TARGETS=[['movies','الأفلام'],['tv','التلفزيون'],['web','المتصفح'],['yt','يوتيوب'],['radio','الراديو'],['photos','الصور'],['video','الفيديو'],['files','مدير الملفات'],['news','الأخبار'],['music','الموسيقى'],['kids','أطفال'],['apps','التطبيقات'],['mirror','عرض الشاشة'],['set','الإعدادات']];
function folderAssignments(){try{return JSON.parse(A.folderAssignments?A.folderAssignments():'{}')}catch(e){return {}}}
function saveFolderAssignment(key,uri,on){const a=folderAssignments();a[key]=Array.isArray(a[key])?a[key]:[];const i=a[key].indexOf(uri);if(on&&i<0)a[key].push(uri);if(!on&&i>=0)a[key].splice(i,1);if(A.saveFolderAssignments)A.saveFolderAssignments(JSON.stringify(a));}
function fshow(){
  FP=[];
  const sel=$('folderTarget');
  if(!sel.options.length)FOLDER_TARGETS.forEach(x=>{const o=document.createElement('option');o.value=x[0];o.textContent=x[1];sel.appendChild(o)});
  sel.value='tv';
  renderFiles();
}
function renderFiles(){
  const box=$('fl');box.innerHTML='';
  const target=$('folderTarget').value||'tv';
  const folders=JSON.parse(A.folders());
  const assigned=folderAssignments()[target]||[];
  $('folderHint').textContent='المجلدات المحددة لـ '+(FOLDER_TARGETS.find(x=>x[0]===target)||['','هذه الأيقونة'])[1]+' — ضع أو أزل علامة الصح';
  if(!FP.length){
    folders.forEach(f=>{
      const row=it(box,'📁 '+f.n,()=>{FP.push([f.t,'']);renderFiles()});
      const check=document.createElement('span');check.textContent=assigned.includes(f.t)?'☑':'☐';check.style.cssText='font-size:25px;padding:0 14px;color:#8be9a8';
      check.onclick=e=>{e.stopPropagation();saveFolderAssignment(target,f.t,!assigned.includes(f.t));renderFiles()};
      row.appendChild(check);
      row.appendChild(xb(()=>{A.removeFolder(f.t);renderFiles()}));
    });
    if(!box.children.length)box.innerHTML='<p>ما أضفت أي مجلد. اضغط إضافة مجلد.</p>';
    return;
  }
  const [t,d]=FP[FP.length-1];
  it(box,'⬆ رجوع',()=>{FP.pop();renderFiles()});
  const l=JSON.parse(A.listDir(t,d)).sort((a,b)=>(b.d-a.d)||a.n.localeCompare(b.n));
  l.forEach(x=>{
    if(x.d)it(box,'📁 '+x.n,()=>{FP.push([t,x.id]);renderFiles()});
    else it(box,x.n,()=>{const m=x.m||'';if(/^(image|video|audio)\//.test(m))player($('fv'),x.u,m);else A.view(x.u,m)})
  })
}
'''
s = s[:start] + manager + s[end:]
s = s.replace('onclick="if(A.pickM3uFile)A.pickM3uFile();else m3f.click()"',
              'onclick="A.pickM3uFile?A.pickM3uFile():m3f.click()"')
s = s.replace(" setInterval(()=>{if(cur==='files'&&!FP.length){const f=A.folders();if(f!==window.__lf){window.__lf=f;renderFiles()}}},1500)", "")
s = s.replace("},900);", "},500);")
html.write_text(s)

java = Path("app/src/main/java/com/carscreens/app/MainActivity.java")
s = java.read_text()
old = '''  private void launchM3uPicker() {
  try {
    Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT);
    i.addCategory(Intent.CATEGORY_OPENABLE);
    i.setType("*/*");
    i.putExtra(Intent.EXTRA_MIME_TYPES, new String[]{"application/x-mpegURL", "audio/x-mpegurl", "application/vnd.apple.mpegurl", "text/plain"});
    startActivityForResult(i, 3);
  } catch (Exception e) {
    getSharedPreferences("ameer_m3u", MODE_PRIVATE).edit().putString("pending", "").apply();
    if (m3uPickerOnly) finish();
  }
}'''
new = '''  private void launchM3uPicker() {
    try {
      Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT);
      i.addCategory(Intent.CATEGORY_OPENABLE);
      i.setType("*/*");
      i.putExtra(Intent.EXTRA_MIME_TYPES, new String[]{"application/x-mpegURL", "audio/x-mpegurl", "application/vnd.apple.mpegurl", "text/plain"});
      // Open the first folder assigned to the TV icon, when available.
      try {
        String saved = getSharedPreferences("folder_assignments", MODE_PRIVATE).getString("map", "{}");
        JSONObject all = new JSONObject(saved);
        JSONArray tvFolders = all.optJSONArray("tv");
        if (tvFolders != null && tvFolders.length() > 0) {
          Uri tree = Uri.parse(tvFolders.getString(0));
          String docId = DocumentsContract.getTreeDocumentId(tree);
          Uri initial = DocumentsContract.buildDocumentUriUsingTree(tree, docId);
          if (Build.VERSION.SDK_INT >= 26) i.putExtra(DocumentsContract.EXTRA_INITIAL_URI, initial);
        }
      } catch (Exception ignored) {}
      i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
      startActivityForResult(i, 3);
    } catch (Exception e) {
      getSharedPreferences("ameer_m3u", MODE_PRIVATE).edit().putString("pending", "").apply();
      if (m3uPickerOnly) finish();
    }
}'''
if old not in s: raise SystemExit("Java M3U picker method not found")
s = s.replace(old, new, 1)

old = '''    WebSettings s = w.getSettings();
    s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setMediaPlaybackRequiresUserGesture(false);'''
new = '''    WebSettings s = w.getSettings();
    w.setLayerType(View.LAYER_TYPE_HARDWARE, null);
    s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setDatabaseEnabled(true);
    s.setLoadsImagesAutomatically(true); s.setMediaPlaybackRequiresUserGesture(false);'''
if old not in s: raise SystemExit("WebView settings context not found")
s = s.replace(old, new, 1)

old = '''    @JavascriptInterface public void pickFolder() { runOnUiThread(() -> launchFolderPicker()); }
    @JavascriptInterface public String folders() {'''
new = '''    @JavascriptInterface public void pickFolder() { runOnUiThread(() -> launchFolderPicker()); }
    @JavascriptInterface public void pickM3uFile() { runOnUiThread(() -> { m3uPickerOnly = false; launchM3uPicker(); }); }
    @JavascriptInterface public String consumeM3u() {
      SharedPreferences sp = getSharedPreferences("ameer_m3u", MODE_PRIVATE);
      String value = sp.getString("pending", "");
      if (value != null && value.length() > 0) sp.edit().putString("pending", "").apply();
      return value == null ? "" : value;
    }
    @JavascriptInterface public String folderAssignments() {
      return getSharedPreferences("folder_assignments", MODE_PRIVATE).getString("map", "{}");
    }
    @JavascriptInterface public void saveFolderAssignments(String json) {
      try { new JSONObject(json); getSharedPreferences("folder_assignments", MODE_PRIVATE).edit().putString("map", json).apply(); }
      catch (Exception ignored) {}
    }
    @JavascriptInterface public String folders() {'''
if old not in s: raise SystemExit("Java bridge insertion point not found")
s = s.replace(old, new, 1)

old = '''        JSONArray a = new JSONArray(sp.getString("l", "[]"));
        JSONObject o = new JSONObject();
        o.put("t", t.toString()); o.put("n", name);
        a.put(o);
        sp.edit().putString("l", a.toString()).apply();'''
new = '''        JSONArray a = new JSONArray(sp.getString("l", "[]"));
        boolean exists = false;
        for (int x = 0; x < a.length(); x++) if (t.toString().equals(a.getJSONObject(x).optString("t"))) exists = true;
        if (!exists) {
          JSONObject o = new JSONObject();
          o.put("t", t.toString()); o.put("n", name);
          a.put(o);
          sp.edit().putString("l", a.toString()).apply();
        }'''
if old not in s: raise SystemExit("Java folder save context not found")
s = s.replace(old, new, 1)
java.write_text(s)
print("Patch script ready")


# Follow-up refinements: preserve the selected icon, avoid UI polling, and
# make navigation/WebView interactions lighter without changing app features.
def patch_if_present(path, old, new):
    p = Path(path)
    s = p.read_text()
    if new in s:
        return
    if old not in s:
        raise SystemExit("Follow-up patch context not found: " + str(path) + " :: " + old[:90])
    p.write_text(s.replace(old, new, 1))

html_path = "app/src/main/assets/index.html"
patch_if_present(html_path,
    "['kids','أطفال'],['apps','التطبيقات']",
    "['kids','أطفال'],['maps','الخرائط'],['apps','التطبيقات']")
patch_if_present(html_path,
    "  sel.value='tv';\n  renderFiles();",
    "  if(!sel.value)sel.value='tv';\n  renderFiles();")
patch_if_present(html_path,
    "function carBack(){if($('app').style.display==='none')return;if(cur==='files'&&FP.length){FP.pop();renderFiles();return}if(cur==='radio'&&$('rl').querySelector('button')){radioCountries();return}home()}",
    "function carBack(){if($('app').style.display==='none')return false;if(cur==='files'&&FP.length){FP.pop();renderFiles();return true}if(cur==='radio'&&$('rl').querySelector('button')){radioCountries();return true}home();return true}")
patch_if_present(html_path,
    "if(A.consumeM3u&&!window.__ameerM3uPoll){window.__ameerM3uPoll=true;setInterval(()=>{try{const t=A.consumeM3u();if(t&&t.length)addList(parseM3u(t));}catch(e){}},500);}",
    "function onM3uPicked(){try{const t=A.consumeM3u?A.consumeM3u():'';if(t&&t.length)addList(parseM3u(t));}catch(e){alert('تعذّر قراءة ملف M3U')}}")

java_path = "app/src/main/java/com/carscreens/app/MainActivity.java"
patch_if_present(java_path,
    "    s.setAllowFileAccess(true); s.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);",
    "    s.setAllowFileAccess(true); s.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);\n    s.setSupportZoom(false); s.setBuiltInZoomControls(false); s.setDisplayZoomControls(false);\n    s.setTextZoom(100);\n    if (Build.VERSION.SDK_INT >= 23) s.setOffscreenPreRaster(true);\n    w.setVerticalScrollBarEnabled(false); w.setHorizontalScrollBarEnabled(false);\n    w.setOverScrollMode(View.OVER_SCROLL_NEVER);")
patch_if_present(java_path,
    "    getSharedPreferences(\"ameer_m3u\", MODE_PRIVATE).edit().putString(\"pending\", playlist).apply();\n    if (m3uPickerOnly) finish();",
    "    getSharedPreferences(\"ameer_m3u\", MODE_PRIVATE).edit().putString(\"pending\", playlist).apply();\n    if (m3uPickerOnly) finish();\n    else if (w != null) w.post(() -> w.evaluateJavascript(\"onM3uPicked()\", null));")
patch_if_present(java_path,
    "        sp.edit().putString(\"l\", n.toString()).apply();",
    "        sp.edit().putString(\"l\", n.toString()).apply();\n        SharedPreferences as = getSharedPreferences(\"folder_assignments\", MODE_PRIVATE);\n        JSONObject map = new JSONObject(as.getString(\"map\", \"{}\"));\n        JSONObject cleaned = new JSONObject();\n        java.util.Iterator<String> names = map.keys();\n        while (names.hasNext()) {\n          String key = names.next(); JSONArray assigned = map.optJSONArray(key); JSONArray kept = new JSONArray();\n          if (assigned != null) for (int j = 0; j < assigned.length(); j++) if (!t.equals(assigned.optString(j))) kept.put(assigned.opt(j));\n          cleaned.put(key, kept);\n        }\n        as.edit().putString(\"map\", cleaned.toString()).apply();")
patch_if_present(java_path,
    '''    w.evaluateJavascript("(function(){var a=document.getElementById('app');if(a&&a.style.display!=='none'){home();return 1}return 0})()", new ValueCallback<String>() {
      public void onReceiveValue(String v) { if (!"1".equals(v)) finish(); }
    });''',
    '''    if (w == null) { finish(); return; }
    w.evaluateJavascript("carBack()", new ValueCallback<String>() {
      public void onReceiveValue(String v) { if ("false".equals(v) || "null".equals(v)) finish(); }
    });''')


# Android Auto launcher visibility: register the existing media browser service
# without changing app screens, playback logic, or other application features.
import re
import xml.etree.ElementTree as ET

ANDROID_NS = "http://schemas.android.com/apk/res/android"
ET.register_namespace("android", ANDROID_NS)
A = "{%s}" % ANDROID_NS

manifest_path = Path("app/src/main/AndroidManifest.xml")
if not manifest_path.exists():
    raise SystemExit("AndroidManifest.xml not found; cannot safely register Android Auto")

manifest_tree = ET.parse(manifest_path)
manifest = manifest_tree.getroot()
application = manifest.find("application")
if application is None:
    raise SystemExit("AndroidManifest.xml has no application element")

# Find the real MediaBrowserService implementation in the existing source.
service_class = None
for source in Path("app/src/main").rglob("*.java"):
    source_text = source.read_text(errors="ignore")
    if re.search(r"extends\s+(?:androidx\.media\.MediaBrowserServiceCompat|MediaBrowserServiceCompat|android\.service\.media\.MediaBrowserService|MediaBrowserService)\b", source_text):
        package_match = re.search(r"^\s*package\s+([\w.]+)\s*;", source_text, re.M)
        class_match = re.search(r"\bclass\s+(\w+)", source_text)
        if package_match and class_match:
            service_class = package_match.group(1) + "." + class_match.group(1)
            break
for source in Path("app/src/main").rglob("*.kt"):
    source_text = source.read_text(errors="ignore")
    if re.search(r":\s*(?:MediaBrowserServiceCompat|MediaBrowserService)\b", source_text):
        package_match = re.search(r"^\s*package\s+([\w.]+)\s*$", source_text, re.M)
        class_match = re.search(r"\bclass\s+(\w+)", source_text)
        if package_match and class_match:
            service_class = package_match.group(1) + "." + class_match.group(1)
            break

if not service_class:
    raise SystemExit("No existing MediaBrowserService implementation found; refusing to add a fake Android Auto service")

# Add the required Android Auto media-app descriptor metadata.
meta_name = "com.google.android.gms.car.application"
meta = next((x for x in application.findall("meta-data") if x.get(A + "name") == meta_name), None)
if meta is None:
    meta = ET.SubElement(application, "meta-data")
    meta.set(A + "name", meta_name)
meta.set(A + "resource", "@xml/automotive_app_desc")
meta.attrib.pop(A + "value", None)

# Register the existing media browser service and its Android Auto intent action.
resolved_service = service_class
service_node = None
for node in application.findall("service"):
    name = node.get(A + "name", "")
    if name in (resolved_service, "." + resolved_service.split(".")[-1]) or name.endswith("." + resolved_service.split(".")[-1]):
        service_node = node
        break
if service_node is None:
    service_node = ET.SubElement(application, "service")
    service_node.set(A + "name", resolved_service)
service_node.set(A + "exported", "true")
service_node.set(A + "foregroundServiceType", "mediaPlayback")
has_action = any(
    action.get(A + "name") == "android.media.browse.MediaBrowserService"
    for intent_filter in service_node.findall("intent-filter")
    for action in intent_filter.findall("action")
)
if not has_action:
    intent_filter = ET.SubElement(service_node, "intent-filter")
    ET.SubElement(intent_filter, "action").set(A + "name", "android.media.browse.MediaBrowserService")

# Required foreground-service permissions for modern Android versions.
for permission in ("android.permission.FOREGROUND_SERVICE", "android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK"):
    if not any(x.get(A + "name") == permission for x in manifest.findall("uses-permission")):
        ET.SubElement(manifest, "uses-permission").set(A + "name", permission)

manifest_tree.write(manifest_path, encoding="utf-8", xml_declaration=True)

descriptor = Path("app/src/main/res/xml/automotive_app_desc.xml")
descriptor.parent.mkdir(parents=True, exist_ok=True)
descriptor.write_text('<?xml version="1.0" encoding="utf-8"?>\n<automotiveApp>\n    <uses name="media" />\n    <uses name="template" />\n</automotiveApp>\n')

# Fix the Android Auto NavigationTemplate pan action configuration only.
car_screen_path = "app/src/main/java/com/carscreens/app/CarWebScreen.java"
patch_if_present(car_screen_path,
    "        template.setMapActionStrip(new ActionStrip.Builder().addAction(Action.PAN).build());",
    "        template.setMapActionStrip(new ActionStrip.Builder().addAction(Action.PAN).build());\n        template.setPanModeListener((isInPanMode) -> {});")

print("Android Auto media launcher registration applied for " + service_class)


# Allow the Android Auto host to bind to this debug APK during device testing.
# Release builds keep the official Android Auto host signature allowlist.
service_path = "app/src/main/java/com/carscreens/app/MapsCarAppService.java"
patch_if_present(service_path,
    """  public HostValidator createHostValidator() {
    return new HostValidator.Builder(this)
        .addAllowedHosts(androidx.car.app.R.array.hosts_allowlist_sample)
        .build();
  }""",
    """  public HostValidator createHostValidator() {
    if ((getApplicationInfo().flags & android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE) != 0) {
      return HostValidator.ALLOW_ALL_HOSTS_VALIDATOR;
    }
    return new HostValidator.Builder(this)
        .addAllowedHosts(androidx.car.app.R.array.hosts_allowlist_sample)
        .build();
  }""")

# Prevent an unused remote CDN script from blocking the in-car WebView parser.
# The bundled UI does not reference Hls anywhere; removing it lets local menus
# initialize immediately even when the car head unit cannot reach cdnjs.
index_path = Path("app/src/main/assets/index.html")
index_source = index_path.read_text()
unused_hls = '<script src="https://cdnjs.cloudflare.com/ajax/libs/hls.js/1.5.15/hls.min.js"></script>'
if unused_hls in index_source:
    index_path.write_text(index_source.replace(unused_hls, "", 1))


# Create all car-surface views with the Presentation display context.
# A WebView created from CarContext is attached to the phone's default display
# while its window is hosted by the car virtual display; this can leave the
# in-car surface stuck/blank while the host keeps showing its loading state.
car_screen_path = "app/src/main/java/com/carscreens/app/CarWebScreen.java"
patch_if_present(car_screen_path,
    """      presentation = new Presentation(getCarContext(), display);
      web = new WebView(getCarContext()) {""",
    """      presentation = new Presentation(getCarContext(), display);
      Context displayContext = presentation.getContext();
      web = new WebView(displayContext) {""")
patch_if_present(car_screen_path,
    """root = new FrameLayout(getCarContext());
playerView = new PlayerView(getCarContext());""",
    """root = new FrameLayout(displayContext);
playerView = new PlayerView(displayContext);""")


# Surface rendering fix: make the Android Auto virtual display render its own
# Presentation content instead of mirroring the phone's default display.
car_screen_path = "app/src/main/java/com/carscreens/app/CarWebScreen.java"
patch_if_present(car_screen_path,
    """    Surface surface = c.getSurface();
    if (surface == null || !surface.isValid()) return;
    try {
      DisplayManager dm = (DisplayManager) getCarContext().getSystemService(Context.DISPLAY_SERVICE);
      virtualDisplay = dm.createVirtualDisplay("AmeerScreensCar", c.getWidth(), c.getHeight(),
          c.getDpi(), surface, DisplayManager.VIRTUAL_DISPLAY_FLAG_PRESENTATION);""",
    """    Surface surface = c.getSurface();
    final int surfaceWidth = c.getWidth();
    final int surfaceHeight = c.getHeight();
    final int surfaceDpi = c.getDpi();
    if (surface == null || !surface.isValid()
        || surfaceWidth <= 0 || surfaceHeight <= 0 || surfaceDpi <= 0) {
      Log.w("AmeerCarWeb", "Car surface is not ready: surface=" + (surface != null && surface.isValid())
          + ", size=" + surfaceWidth + "x" + surfaceHeight + ", dpi=" + surfaceDpi);
      return;
    }
    try {
      DisplayManager dm = (DisplayManager) getCarContext().getSystemService(Context.DISPLAY_SERVICE);
      virtualDisplay = dm.createVirtualDisplay("AmeerScreensCar", surfaceWidth, surfaceHeight,
          surfaceDpi, surface, DisplayManager.VIRTUAL_DISPLAY_FLAG_PRESENTATION
              | DisplayManager.VIRTUAL_DISPLAY_FLAG_OWN_CONTENT_ONLY);""")
patch_if_present(car_screen_path,
    """      if (virtualDisplay == null) return;
      Display display = virtualDisplay.getDisplay();""",
    """      if (virtualDisplay == null) {
        Log.e("AmeerCarWeb", "createVirtualDisplay returned null");
        return;
      }
      Display display = virtualDisplay.getDisplay();
      Log.i("AmeerCarWeb", "Car virtual display created: " + surfaceWidth + "x" + surfaceHeight
          + " dpi=" + surfaceDpi + " display=" + display.getDisplayId());""")
patch_if_present(car_screen_path,
    """        @Override public void onPageFinished(WebView view, String url) {
          super.onPageFinished(view, url);
          installCarKeyboard(view);
        }""",
    """        @Override public void onPageStarted(WebView view, String url, android.graphics.Bitmap favicon) {
          super.onPageStarted(view, url, favicon);
          Log.i("AmeerCarWeb", "Car WebView loading: " + url);
        }
        @Override public void onPageFinished(WebView view, String url) {
          super.onPageFinished(view, url);
          Log.i("AmeerCarWeb", "Car WebView finished: " + url);
          installCarKeyboard(view);
        }
        @Override public void onReceivedError(WebView view, android.webkit.WebResourceRequest request,
                                              android.webkit.WebResourceError error) {
          super.onReceivedError(view, request, error);
          if (request.isForMainFrame()) {
            Log.e("AmeerCarWeb", "Car WebView main-frame error: " + error.getErrorCode()
                + " " + error.getDescription() + " url=" + request.getUrl());
          }
        }""")


// Follow the official Android for Cars surface-rendering pattern.
// The host-provided Surface is already a presentation target; use flags=0.
// Release each Surface instance after its VirtualDisplay is detached.
car_screen_path = "app/src/main/java/com/carscreens/app/CarWebScreen.java"
patch_if_present(car_screen_path,
    """          surfaceDpi, surface, DisplayManager.VIRTUAL_DISPLAY_FLAG_PRESENTATION
              | DisplayManager.VIRTUAL_DISPLAY_FLAG_OWN_CONTENT_ONLY);""",
    """          surfaceDpi, surface, 0);""")
patch_if_present(car_screen_path,
    """  private SurfaceContainer current;
  private VirtualDisplay virtualDisplay;""",
    """  private SurfaceContainer current;
  private Surface ownedSurface;
  private VirtualDisplay virtualDisplay;""")
patch_if_present(car_screen_path,
    """    Surface surface = c.getSurface();
    final int surfaceWidth = c.getWidth();""",
    """    Surface surface = c.getSurface();
    ownedSurface = surface;
    final int surfaceWidth = c.getWidth();""")
patch_if_present(car_screen_path,
    """    try { if (virtualDisplay != null) virtualDisplay.release(); } catch (Exception ignored) {}
    virtualDisplay = null;""",
    """    try { if (virtualDisplay != null) virtualDisplay.release(); } catch (Exception ignored) {}
    virtualDisplay = null;
    try { if (ownedSurface != null) ownedSurface.release(); } catch (Exception ignored) {}
    ownedSurface = null;""")

print("Android Auto surface compatibility correction applied")
