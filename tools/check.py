import json, re, sys, urllib.request

errors = []
warnings = []

try:
    root = json.load(open("plugins.json", encoding="utf-8"))
except Exception as e:
    print(f"plugins.json 解析失败: {e}")
    sys.exit(1)

if root.get("apiVersion") != 1:
    errors.append(f"apiVersion 必须为 1 当前 {root.get('apiVersion')}")
if not isinstance(root.get("plugins"), list):
    errors.append("plugins 必须为数组")
    sys.exit(1)

ids = set()
plugin_errors = []

def check(i, p):
    def req(name):
        if not p.get(name):
            plugin_errors.append(f"plugins[{i}] 缺少 {name}")
            return False
        return True

    pid = p.get("id", "")
    if not re.fullmatch(r"[a-z0-9]+(\.[a-z0-9_-]+)+", pid or ""):
        plugin_errors.append(f"plugins[{i}] id 不合规: {pid!r} (反向域名全小写)")
    if pid in ids:
        plugin_errors.append(f"plugins[{i}] id 重复: {pid}")
    ids.add(pid)
    for name in ("name", "author", "description", "homepage"):
        req(name)
    latest = p.get("latest")
    if not isinstance(latest, dict):
        plugin_errors.append(f"plugins[{i}] 缺少 latest")
        return
    if latest.get("apiVersion") != 1:
        plugin_errors.append(f"plugins[{i}] latest.apiVersion 必须为 1")
    if not re.match(r"^\d+(\.\d+){0,3}$", str(latest.get("version", ""))):
        plugin_errors.append(f"plugins[{i}] latest.version 不是版本号: {latest.get('version')}")
    url = latest.get("downloadUrl", "")
    if not url.startswith("https://"):
        plugin_errors.append(f"plugins[{i}] latest.downloadUrl 必须 https")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", str(latest.get("sha256", ""))):
        plugin_errors.append(f"plugins[{i}] latest.sha256 必须 64 位十六进制")
    if not re.match(r"^\d{4}-\d{2}-\d{2}T", str(latest.get("publishedAt", ""))):
        plugin_errors.append(f"plugins[{i}] latest.publishedAt 不是 ISO 时间")

for i, p in enumerate(root["plugins"]):
    check(i, p)

if plugin_errors:
    errors += plugin_errors

if not errors:
    for i, p in enumerate(root["plugins"]):
        url = p["latest"]["downloadUrl"]
        try:
            r = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Glimpseon-PluginIndex"})
            urllib.request.urlopen(r, timeout=15)
        except Exception as e:
            warnings.append(f"plugins[{i}] downloadUrl 不可达: {url} ({e})")

for w in warnings:
    print(f"WARN {w}")
if errors:
    for e in errors:
        print(f"ERROR {e}")
    sys.exit(1)
print(f"OK {len(root['plugins'])} 个插件全部通过")
