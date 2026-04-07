# AgentJoey Workspace 🚀

一个基于 **Turborepo** 的 monorepo，用于管理所有的产品项目。

## 📦 项目结构

```
agentjoey-workspace/
├── apps/                    # 应用程序
│   ├── website/            # 主网站
│   ├── dashboard/          # SaaS 管理面板 (计划中)
│   ├── api-service/        # API 服务 (计划中)
│   └── documentation/      # 文档站点
│
├── packages/               # 共享包
│   ├── ui/                 # UI 组件库
│   ├── utils/              # 工具函数
│   ├── hooks/              # React Hooks
│   ├── eslint-config/      # ESLint 配置
│   └── typescript-config/  # TypeScript 配置
│
└── turbo.json              # Turborepo 配置
```

## 🚀 快速开始

### 前置要求
- Node.js >= 18
- npm >= 9

### 安装

```bash
# Clone 仓库
git clone https://github.com/agentjoey/agentjoey-workspace.git
cd agentjoey-workspace

# 安装依赖
npm install
```

### 开发

```bash
# 启动所有应用的开发模式
npm run dev

# 只启动 website
cd apps/website && npm run dev

# 只启动 dashboard
cd apps/dashboard && npm run dev
```

### 构建

```bash
# 构建所有应用和包
npm run build

# 构建特定应用
cd apps/website && npm run build
```

### 其他命令

```bash
# 代码检查
npm run lint

# 类型检查
npm run check-types

# 格式化代码
npm run format
```

## 🏗️ 技术栈

- **Framework**: Next.js 14+
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: 自定义 + shadcn/ui
- **Build Tool**: Turborepo
- **Package Manager**: npm workspaces

## 📚 应用说明

### website
- **端口**: 3000
- **描述**: 主网站和落地页
- **技术**: Next.js App Router + Tailwind

### dashboard (计划中)
- **端口**: 3001
- **描述**: AI 代理管理面板
- **技术**: Next.js + 数据可视化

### api-service (计划中)
- **端口**: 3002
- **描述**: 后端 API 服务
- **技术**: Next.js API Routes / Express

## 📦 共享包

### @workspace/ui
UI 组件库，包含设计系统的所有组件。

```tsx
import { Button, Card } from '@workspace/ui';
```

### @workspace/utils
通用工具函数。

```ts
import { formatDate, cn } from '@workspace/utils';
```

### @workspace/hooks
React Hooks。

```tsx
import { useAuth, useLocalStorage } from '@workspace/hooks';
```

## 🛠️ 开发指南

### 添加新应用

```bash
cd apps
npx create-next-app@latest my-app --typescript --tailwind
# 更新 turbo.json 和根 package.json
```

### 添加新包

```bash
cd packages
mkdir my-package && cd my-package
npm init -y
# 配置 package.json name 为 @workspace/my-package
```

### 最佳实践

1. **依赖管理**
   - 共享依赖放在根 `package.json`
   - 应用特有依赖放在各自 `package.json`

2. **代码复用**
   - UI 组件 → `@workspace/ui`
   - 工具函数 → `@workspace/utils`
   - 业务逻辑 → 各自应用内

3. **环境变量**
   - 使用 `.env.local`
   - 绝不提交到 git

4. **提交规范**
   ```
   feat: 新功能
   fix: 修复
   docs: 文档
   refactor: 重构
   chore: 杂项
   ```

## 🚀 部署

### Vercel (推荐)

每个应用可以独立部署到 Vercel：

```bash
# 部署 website
cd apps/website
vercel --prod

# 部署 dashboard
cd apps/dashboard
vercel --prod
```

### 配置说明

- 每个应用有自己的 `vercel.json` 配置
- 共享包会自动构建
- 环境变量在 Vercel Dashboard 中配置

## 📄 相关文档

- [项目结构说明](./PROJECT_STRUCTURE.md)
- [Turborepo 文档](https://turbo.build/repo/docs)
- [Next.js 文档](https://nextjs.org/docs)

## 🔗 链接

- **GitHub**: https://github.com/agentjoey/agentjoey-workspace
- **Website**: (部署中)
- **Dashboard**: (开发中)

## 📝 License

Private - All rights reserved
