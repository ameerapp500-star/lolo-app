from pathlib import Path
import re
out = []
root = Path("app/src/main")
for p in sorted(root.rglob("*")):
    if not p.is_file() or p.suffix not in (".java", ".kt", ".xml", ".html"):
        continue
    try: s = p.read_text(errors="replace")
    except Exception: continue
    if p.name == "AndroidManifest.xml" or p.name == "index.html" or re.search(r"MediaBrowserService|onLoadChildren|onGetRoot|MediaSession|CarAppService|onCreateSession|NavigationTemplate|ScreenManager", s):
        out.append("\n\n===== " + str(p) + " =====\n" + s)
Path("/tmp/lolo-diagnostic.txt").write_text("\n".join(out))
print("Diagnostic source report generated:", len(out), "files")
