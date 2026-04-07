# AgentJoey Workspace - 项目结构

这是一个 **Turborepo** monorepo，用于管理所有的产品项目。

## 📁 目录结构

```
agentjoey-workspace/
├── apps/                          # 应用程序
│   ├── website/                   # 主网站 (Next.js)
│   ├── dashboard/                 # SaaS 管理面板 (待创建)
│   └── api-service/               # API 服务 (待创建)
│
├── packages/                      # 共享包
│   ├── ui/                        # UI 组件库
│   ├── utils/                     # 工具函数 (待创建)
│   ├── config/                    # 共享配置
│   │   ├── eslint-config/         # ESLint 配置
│   │   └── typescript-config/     # TypeScript 配置
│   └── hooks/                     # React Hooks (待创建)
│
├── turbo.json                     # Turborepo 配置
└── package.json                   # Workspace 根配置
```

## 🚀 快速开始

```bash
# 安装依赖
npm install

# 开发模式（所有应用）
npm run dev

# 构建所有
npm run build

# 测试所有
npm run test

# 只开发 website
cd apps/website && npm run dev
```

## 📦 应用列表

### website
- **类型**: Next.js 网站
- **端口**: 3000
- **描述**: 主网站/落地页

### dashboard (计划中)
- **类型**: Next.js 应用
- **端口**: 3001
- **描述**: AI 代理管理面板

### api-service (计划中)
- **类型**: Node.js/Next.js API
- **端口**: 3002
- **描述**: 后端 API 服务

## 📚 共享包

### @workspace/ui
- UI 组件库
- 使用方式: `import { Button } from '@workspace/ui'`

### @workspace/utils (计划中)
- 通用工具函数
- 使用方式: `import { formatDate } from '@workspace/utils'`

### @workspace/hooks (计划中)
- React Hooks
- 使用方式: `import { useAuth } from '@workspace/hooks'`

## 🏗️ 添加新应用

```bash
# 创建新的 Next.js 应用
cd apps
npx create-next-app@latest my-new-app --typescript --tailwind --eslint

# 更新根 package.json workspaces
# 在 turbo.json 中添加 pipeline 配置
```

## 🏗️ 添加新包

```bash
# 创建包目录
mkdir packages/my-package
cd packages/my-package
npm init -y

# 配置 package.json name 为 @workspace/my-package
# 导出模块
```

## 💡 最佳实践

### 1. 依赖管理
- 共享依赖放在根 `package.json`
- 应用特有依赖放在各自 `package.json`

### 2. 代码复用
- UI 组件 → `@workspace/ui`
- 工具函数 → `@workspace/utils`
- 业务逻辑 → 各自应用内

### 3. 环境变量
- 应用级 `.env.local`
- 绝不提交到 git

### 4. 提交规范
```
feat: 新功能
fix: 修复
docs: 文档
refactor: 重构
chore: 杂项
```

## 🔗 相关链接

- **GitHub**: https://github.com/agentjoey/agentjoey-workspace
- **Turborepo 文档**: https://turbo.build/repo/docs
- **部署**: Vercel (配置中)
