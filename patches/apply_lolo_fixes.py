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
