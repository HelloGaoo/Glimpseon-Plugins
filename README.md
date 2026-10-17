# Glimpseon-Plugins

Glimpseon 插件索引仓库。

1. **登记**：注册插件
2. **中转**：指向插件的项目仓库（`repo`）与发布包（release asset）

## 条目格式

```json
{
  "id": "com.author.plugin",
  "repo": "author/repo",
  "branch": "main",
  "manifestPath": "manifest.json",
  "homepage": "https://github.com/author/repo",
  "latest": {
    "version": "1.0.0",
    "asset": "com.author.plugin.gplugin",
    "sha256": "64 位十六进制",
    "publishedAt": "2026-10-17T00:00:00Z"
  }
}
```

| 字段                   | 必填 | 说明                                                                          |
| -------------------- | -- | --------------------------------------------------------------------------- |
| `id`                 | 1  | 反向域名= `manifest.id`                                                         |
| `repo`               | 1  | 插件项目 `owner/repo` 或GitHub URL                                               |
| `branch`             | —  | 默认 `main`                                                                   |
| `manifestPath`       | —  | 默认 `manifest.json`                                                          |
| `homepage`           | —  | 项目主页                                                                        |
| `latest.version`     | 1  | 最新版本号                                                                       |
| `latest.asset`       | —  | 发布资产名 默认 `<id>.gplugin`                                                     |
| `latest.downloadUrl` | —  | 指定下载地址时填；不填则按 `https://github.com/<repo>/releases/latest/download/<asset>`  |
| `latest.sha256`      | —  | 校验                                                                          |
| `latest.publishedAt` | —  | 发布时间                                                                        |

## 插件项目的发布约定

1. 根目录放 `manifest.json`，把`icon`、`readme` 用相对路径指向仓库内文件
2. 打 tag：`v<version>`（`v1.0.0`）
3. Release 上传插件包，文件名默认 `<id>.gplugin`（自定义则同步写 `latest.asset`）
4. 把 `version`、`sha256`、`publishedAt` 填进本仓库 `plugins.json`

## 图标与 README

- 图标：插件项目里的 `manifest.icon` 指向的文件
- README：`manifest.readme`

## 本地校验

```bash
python tools/check.py
```

<br />

## 发布后刷新 CDN

```bash
curl -s "https://purge.jsdelivr.net/gh/HelloGaoo/Glimpseon-Plugins@main/plugins.json"
```

