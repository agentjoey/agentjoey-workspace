# Agentjoey Workspace - Vercel 部署指南

## 📋 Monorepo 部署架构

```
agentjoey-workspace/
├── apps/
│   ├── website/      → vercel.com → agentjoey.com
│   ├── documentation/ → vercel.com → docs.agentjoey.com
│   ├── dashboard/    → (占位，暂不部署)
│   └── api-service/  → (占位，暂不部署)
└── packages/         → (共享代码，不单独部署)
```

---

## 🚀 快速部署步骤

### 1. 登录 Vercel

```bash
vercel login
# 按提示完成浏览器授权
```

### 2. 部署 Website（主站）

```bash
cd ~/clawspace/agentjoey-workspace/apps/website

# 首次部署（创建项目）
vercel --yes

# 配置项目
# - 项目名称: agentjoey-website
# - Root Directory: ./ (已在 apps/website 内)
# - Framework: Next.js

# 绑定自定义域名
vercel domains add agentjoey.com

# 生产部署
vercel --prod
```

### 3. 部署 Documentation（文档站）

```bash
cd ~/clawspace/agentjoey-workspace/apps/documentation

# 首次部署
vercel --yes

# 配置项目
# - 项目名称: agentjoey-docs
# - Root Directory: ./
# - Framework: Next.js

# 绑定子域名
vercel domains add docs.agentjoey.com

# 生产部署
vercel --prod
```

---

## ⚙️ 从根目录部署（推荐方式）

如果不想进入每个 app 目录，可以使用 `--cwd`：

```bash
cd ~/clawspace/agentjoey-workspace

# 部署 website
vercel --cwd apps/website --yes

# 部署 documentation
vercel --cwd apps/documentation --yes
```

---

## 🔧 Vercel Dashboard 配置

### Website 项目设置

| 设置项 | 值 |
|--------|-----|
| **Framework** | Next.js |
| **Root Directory** | `apps/website` |
| **Build Command** | `next build` (默认) |
| **Output Directory** | `.next` (默认) |
| **Install Command** | `npm install` |

### Environment Variables

如有需要，添加以下环境变量：

```
NEXT_PUBLIC_SITE_URL=https://agentjoey.com
```

### 构建缓存优化

Vercel 会自动缓存 `node_modules` 和 `.next/cache`，无需额外配置。

---

## 📦 Turborepo 远程缓存（可选）

如需启用 Turborepo Remote Cache，在 Vercel 项目设置中添加：

```
TURBO_TOKEN=your_token
TURBO_TEAM=your_team
```

然后修改 Build Command：
```
cd ../.. && npx turbo run build --filter=website
```

---

## 🔄 持续部署

推送代码到 GitHub 后，Vercel 会自动：
1. 检测代码变更
2. 运行构建
3. 部署预览环境（Preview）
4. 合并到 main 后自动部署生产环境

---

## 🌐 域名配置

### 主域名 (agentjoey.com)
1. 在 Vercel Dashboard → Domains 添加域名
2. 在 DNS 提供商添加 A 记录指向 Vercel

### 子域名 (docs.agentjoey.com)
1. 在 Documentation 项目添加域名 `docs.agentjoey.com`
2. 在 DNS 添加 CNAME 记录

---

## 📝 部署状态检查

```bash
# 查看部署状态
vercel list

# 查看日志
vercel logs agentjoey-website

# 删除项目（如需重建）
vercel remove agentjoey-website
```

---

## ❓ 常见问题

### Q: 为什么提示 "Command not found: turbo"?
A: 确保在 Root Directory 正确设置了 `package.json` 中的 scripts。

### Q: 共享 packages 如何生效？
A: Vercel 会自动安装根目录的依赖，workspaces 机制会链接本地 packages。

### Q: 构建失败提示找不到模块？
A: 检查 `turbo.json` 中的 pipeline 配置，确保依赖顺序正确。

---

## ✅ 部署检查清单

- [ ] Website 部署成功
- [ ] Documentation 部署成功
- [ ] 自定义域名绑定
- [ ] HTTPS 证书自动配置
- [ ] 预览环境正常工作
- [ ] 生产环境正常访问

---

**完成部署后，您的架构：**
- 🌐 agentjoey.com → Website
- 📚 docs.agentjoey.com → Documentation
- ⚙️ Vercel Dashboard → 统一管理
