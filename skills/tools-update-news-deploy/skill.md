---
name: tools-update-news-deploy
description: 部署 Vite + React 项目（tools-update-news）到 Vercel 的经验总结。涵盖 GitHub Pages 迁移、自定义域名、DNS、GitHub Actions 自动化部署的踩坑记录。
---

# tools-update-news 部署经验总结

## 项目信息

- **项目**: Vite + React + TypeScript 静态站点
- **代码托管**: GitHub (私有仓库)
- **部署平台**: Vercel (Hobby 免费计划)
- **域名**: `ai.firepaintseal.com` (NameCheap 注册，Vercel DNS)
- **CI/CD**: GitHub Actions → Vercel CLI 部署

## 从 GitHub Pages 迁移到 Vercel 的注意事项

### 1. Vite 配置需要调整

移除 `base` 配置，GitHub Pages 需要 base path（如 `/tools-update-news/`），Vercel 不需要：

```typescript
// vite.config.ts — GHPages 需要 base，Vercel 不需要
// ❌ 之前（GitHub Pages）:
export default defineConfig({
  plugins: [react()],
  base: process.env.VITE_BASE_PATH || "/",
});

// ✅ 之后（Vercel）:
export default defineConfig({
  plugins: [react()],
});
```

### 2. GitHub Actions 工作流需要重写

```yaml
# ✅ Vercel 部署 workflow
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 5   # 防止卡死
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - name: Deploy to Vercel
        run: npx --yes vercel --prod --token=${{ secrets.VERCEL_TOKEN }} --yes
```

关键点：
- `timeout-minutes: 5` 防止 job 卡住无限等待
- `npx --yes` 确保 npx 自动下载 CLI（第一个 `--yes` 是给 npx 的，第二个是给 vercel 的）
- 推荐将 `vercel` 安装为 devDependency：`npm install -D vercel`，这样 CI 中 npx 可以直接使用本地包

### 3. Vercel Token 的类型

- OAuth token（`vca_` 开头）有有效期，会在特定时间过期
- **Classic token（`vcp_` 开头）适合 CI/CD 使用，不会过期**
- Classic token 在 Vercel Dashboard → Settings → Tokens 创建
- 创建后通过 `gh secret set VERCEL_TOKEN --body "vcp_xxx"` 存入 GitHub Secrets
- ⚠️ OAuth 登录后无法在 CLI 通过 `vercel tokens add` 创建 token，必须去 Dashboard 手动创建

### 4. 自定义域名与 DNS 配置

推荐直接修改域名注册商的 **Nameservers**，而不是加 A 记录：

| 方式 | Nameservers |
|------|-------------|
| ✅ 推荐 | `ns1.vercel-dns.com` / `ns2.vercel-dns.com` |
| 备选 | A 记录指向 `76.76.21.21` |

验证 DNS 是否生效：

```bash
dig +short NS firepaintseal.com
# 期望: ns1.vercel-dns.com.
#        ns2.vercel-dns.com.

dig +short ai.firepaintseal.com
# Vercel 会返回多个 IP（anycast 网络）
```

NameCheap 操作路径：Dashboard → 域名 Manage → NAMESERVERS 下拉选 Custom DNS → 填入 Vercel 的 nameserver。

### 5. Vercel 部署 BLOCKED 状态的常见原因

| 原因 | 现象 | 解决 |
|------|------|------|
| 域名 DNS 未正确配置 | `"verified": false` | 确认 nameserver 已指向 Vercel |
| 部署队列阻塞 | 多个 BLOCKED deployment | Cancel 旧的重试 |
| 证书签发中 | `"new"` / `"pending"` | 等待自动签发（通常几分钟） |
| gitDirty 标志 | `"gitDirty": 1` | 忽略，不影响部署 |

验证域名状态：

```bash
npx vercel domains inspect ai.firepaintseal.com
# Nameservers 显示 ✔ 表示 DNS 配置正确

# 或通过 API 查看 verified 字段
curl -s "https://api.vercel.com/v9/projects/<project-id>/domains?teamId=<team-id>" \
  -H "Authorization: Bearer $TOKEN"
```

### 6. 部署方式的坑

**本地 CLI 部署 vs GitHub Actions 部署**

- 本地运行 `npx vercel --prod` 会设置 `gitDirty: 1`，因为本地可能有未提交文件
- GitHub Actions 部署更干净（`gitDirty` 通常为 false）
- `vercel deploy`（无 `--prod`）会创建 Preview Deployment，不影响 Production
- 推荐用 GitHub Actions push 触发自动部署

### 7. 验证部署是否成功

```bash
# 检查 Vercel 上最新的生产部署
npx vercel list --prod

# 检查 GitHub Actions 运行状态
gh run list --workflow "Deploy to Vercel"

# 直接访问域名测试
curl -s -o /dev/null -w "%{http_code}" https://ai.firepaintseal.com/
```

## 快速启动新项目到 Vercel 的推荐步骤

1. GitHub 建仓库，push 代码
2. 更新 `vite.config.ts`（移除 `base`）
3. Vercel Dashboard 导入仓库（或手动 `npx vercel link`）
4. Vercel Dashboard 创建 Classic Token → 存入 GitHub Secrets
5. 配置 GitHub Actions workflow（见上）
6. 添加自定义域名，改 nameserver 到 Vercel
7. push 触发自动部署
