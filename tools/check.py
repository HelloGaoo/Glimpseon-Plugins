"""Glimpseon 插件索引校验"""

import json
import re
import sys
import urllib.request

INDEX = "plugins.json"
LEGACY_FIELDS = ("name", "author", "description", "iconUrl", "readmeUrl", "tags")
PLUGIN_ID = re.compile(r"[a-z0-9]+(\.[a-z0-9_-]+)+")
REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
VERSION = re.compile(r"^\d+(\.\d+){0,3}([-+][0-9A-Za-z.-]+)?$")
SHA256 = re.compile(r"[0-9a-fA-F]{64}")
ISO_TIME = re.compile(r"^\d{4}-\d{2}-\d{2}T")

errors = []
warnings = []

try:
    root = json.load(open(INDEX, encoding="utf-8"))
except Exception as e:
    print(f"plugins.json 解析失败: {e}")
    sys.exit(1)

if root.get("apiVersion") != 1:
    errors.append(f"apiVersion 必须为 1 当前 {root.get('apiVersion')!r}")
if not isinstance(root.get("plugins"), list):
    print("ERROR plugins 必须为数组")
    sys.exit(1)

seen = set()


def head_ok(url):
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Glimpseon-PluginIndex"})
        urllib.request.urlopen(req, timeout=15)
        return True, ""
    except Exception as e: 
        return False, str(e)


def check(i, p):
    where = f"plugins[{i}]"
    pid = p.get("id", "")
    if not pid:
        errors.append(f"{where} 缺少 id")
    elif not PLUGIN_ID.fullmatch(pid):
        errors.append(f"{where} id 不合规: {pid!r} (反向域名 全小写)")
    elif pid in seen:
        errors.append(f"{where} id 重复: {pid}")
    seen.add(pid)

    repo = p.get("repo", "")
    if not repo:
        errors.append(f"{where} 缺少 repo (插件项目 owner/repo)")
    elif not REPO.fullmatch(str(repo).replace(".git", "").strip("/")):
        errors.append(f"{where} repo 格式不对: {repo!r} 应为 owner/repo")

    branch = p.get("branch")
    if branch is not None and not isinstance(branch, str):
        errors.append(f"{where} branch 必须是字符串")

    manifest_path = p.get("manifestPath")
    if manifest_path is not None:
        if not isinstance(manifest_path, str) or not manifest_path.endswith(".json"):
            errors.append(f"{where} manifestPath 必须是 .json 相对路径")
        elif manifest_path.startswith("/"):
            errors.append(f"{where} manifestPath 不要以 / 开头")

    homepage = p.get("homepage")
    if homepage is not None and not str(homepage).startswith("https://"):
        errors.append(f"{where} homepage 必须 https")

    latest = p.get("latest")
    if not isinstance(latest, dict):
        errors.append(f"{where} 缺少 latest")
        return

    version = latest.get("version", "")
    if not VERSION.match(str(version)):
        errors.append(f"{where} latest.version 不是版本号: {version!r}")

    asset = latest.get("asset")
    if asset is not None and not str(asset).endswith(".gplugin"):
        errors.append(f"{where} latest.asset 必须以 .gplugin 结尾")

    url = latest.get("downloadUrl")
    if url is not None and not str(url).startswith("https://"):
        errors.append(f"{where} latest.downloadUrl 必须 https")

    if not url and not repo:
        errors.append(f"{where} downloadUrl 与 repo 至少要有一个")

    sha = latest.get("sha256")
    if sha is None:
        warnings.append(f"{where} 未填 sha256, 客户端将跳过完整性校验")
    elif not SHA256.fullmatch(str(sha)):
        errors.append(f"{where} latest.sha256 必须 64 位十六进制")

    published = latest.get("publishedAt")
    if published is not None and not ISO_TIME.match(str(published)):
        errors.append(f"{where} latest.publishedAt 不是 ISO 时间")

    legacy = [k for k in LEGACY_FIELDS if k in p]
    if legacy:
        warnings.append(f"{where} 含废弃字段 {', '.join(legacy)} (应由插件项目 manifest 提供)")

    if repo:
        r = str(repo).replace(".git", "").strip("/")
        mp = (manifest_path or "manifest.json").lstrip("/")
        murl = f"https://raw.githubusercontent.com/{r}/{branch or 'main'}/{mp}"
        ok, err = head_ok(murl)
        if not ok:
            warnings.append(f"{where} manifest 不可达: {murl} ({err})")

    if url:
        ok, err = head_ok(url)
        if not ok:
            warnings.append(f"{where} downloadUrl 不可达: {url} ({err})")


for i, plugin in enumerate(root["plugins"]):
    check(i, plugin)

for w in warnings:
    print(f"WARN {w}")
if errors:
    for e in errors:
        print(f"ERROR {e}")
    sys.exit(1)
print(f"OK {len(root['plugins'])} 个插件全部通过")
