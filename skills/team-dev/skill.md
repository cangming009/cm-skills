# 国产模型协同工作技能 (Teams Multi-Model Skill)

## 技能概述

本 skill 支持多个国产AI模型协同工作，实现任务分工、消息传递和协作规则管理。

## 工具清单

| 工具名称 | 功能描述 | 适用场景 |
|---------|---------|---------|
| `TeamCreate` | 创建新团队 | 项目启动时初始化团队 |
| `TeamDelete` | 删除团队 | 项目完成时清理资源 |
| `SendMessage` | 发送消息 | 团队成员间通信 |
| `SendMessage broadcast` | 广播消息 | 全员通知、重大决策 |
| `SendMessage type: "message"` | 私聊 | 任务分配、进度汇报 |
| `TaskCreate` | 创建任务 | 分解工作项 |
| `TaskUpdate` | 更新任务 | 状态变更、进度同步 |
| `TaskList` | 列出任务 | 任务概览、依赖检查 |

## 模型分配规则

### ⚠️ 重要约束

**必须为每个团队成员显式指定 `model` 字段！**

- ✅ **正确做法**: 每个成员都明确指定 `model: "sonnet"` 或 `model: "haiku"`
- ❌ **错误做法**: 不指定 `model` 字段，导致默认使用 `opus-4.6` 模型

**禁止使用的模型**:
- `claude-opus-4-6` (包括 `opus-4-6`、`opus` 等变体)
- 原因: 成本较高，不适合团队协作场景
- `sonnet` 和 `haiku` 已能满足绝大多数需求

### 🔧 自动修复机制

创建团队配置时，系统会自动检查并修复 `.claude/teams/*/config.json` 中的模型设置：

```
修复规则:
1. 扫描所有团队配置文件
2. 检测禁止的模型 (opus-4.6, opus)
3. 自动替换为 'sonnet'
4. 保存修复后的配置
```

**自动修复时**:
```
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  🔧 自动修复团队配置
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

团队: my-team
  ✅ [team-lead] 'claude-opus-4-6' -> 'sonnet'
  ✅ [coder] 'opus' -> 'sonnet'

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

### 模型选择策略
每个团队成员必须明确指定 `model` 字段，根据任务复杂度选择：

| 角色类型 | 推荐模型 | 适用场景 |
|---------|---------|---------|
| **team-lead** | `sonnet` | 任务分配、关键决策、复杂推理 |
| **coder** | `sonnet` | 代码实现、重构、debug |
| **reviewer** | `sonnet` | 代码审查、质量把控 |
| **architect** | `sonnet` | 架构设计、技术方案 |
| **analyzer** | `haiku` | 代码扫描、快速分析 |
| **tester** | `haiku` | 用例执行、回归测试 |

### 配置示例
```json
{
  "members": [
    {
      "name": "team-lead",
      "agentType": "team-lead",
      "model": "sonnet"
    },
    {
      "name": "coder",
      "agentType": "general-purpose",
      "model": "sonnet"
    },
    {
      "name": "analyzer",
      "agentType": "Explore",
      "model": "haiku"
    }
  ]
}
```

### 任务分工模式

### 1. PMO + Coder 双人组
```
PMO (项目经理)
├── 任务规划与分解
├── 进度跟踪与协调
└── 质量把控

Coder (开发者)
├── 代码实现
├── 测试编写
└── Bug修复
```

### 2. 多角色团队
```
Leader (领导者)
├── 项目总体负责
└── 关键决策

Architect (架构师)
├── 技术方案设计
└── 代码审查

Developer (开发者)
├── 功能开发
└── 单元测试

Tester (测试员)
├── 测试用例设计
└── 集成测试
```

## 工作流程

### 标准流程
1. PMO 创建团队并分配角色
2. PMO 分解任务并分配
3. 各角色独立工作
4. 通过 mailbox 同步进度
5. PMO 验收并合并

### 紧急流程
1. 广播紧急通知
2. 相关成员私聊确认
3. 快速响应处理
4. 事后复盘归档

## 成功案例：video-subtitle-txt 项目

### 项目背景
- **目标**: 构建 B站/抖音/YouTube 视频字幕 TXT 提取工具
- **技术栈**: Python FastAPI + React + Tailwind + yt-dlp + faster-whisper
- **团队配置**: team-lead (协调) + react-dev (前端) + backend-dev (后端)

### 协作流程
1. **任务分解**: TeamCreate 创建团队 → TaskCreate 分解任务
2. **并行开发**: react-dev 构建 React 前端, backend-dev 修复后端 CORS/async 问题
3. **进度同步**: 通过 SendMessage mailbox 自动同步
4. **验收**: 运行 bash scripts/test_bilibili_demo.sh 验证

### 关键修复记录
| 问题 | 解决方案 |
|------|---------|
| process_task 非 async | 改为 `async def process_task` |
| SRT 时间戳残留 | text_cleaner 添加 `,\d+ --> ,.*` 清洗 |
| React 资源 404 | app.mount("/assets", StaticFiles) |
| asyncio.create_task 报错 | 函数改为 async coroutine |

### 验证结果
```
[Test 1] GET /           Status: 200 ✓
[Test 2] POST /api/tasks Status: 200 ✓
[Test 3] GET /api/tasks/{task_id} Status: 200 ✓
[Test 4] GET /api/tasks/invalid Status: 404 ✓
[Test 5] GET /assets/*.css Status: 200 ✓

DEMO_BILIBILI_TRANSCRIPT_READY
outputs/demo_bilibili/transcript.txt: 6224 字符
```

### 团队协作要点
- **并行任务分配**: 前端和后端任务同时进行，节省时间
- **清晰的角色定义**: 每个 agent 有明确的职责范围
- **后台运行**: 使用 `run_in_background: true` 并行执行
- **tmux 会话保持**: 即使 SSH 断开，团队工作继续运行
- **最终验证**: 必须运行 test_bilibili_demo.sh 确认端到端可用

### tmux + Agent Teams 最佳实践 (v2.0)
```bash
# 1. 创建 tmux 会话
tmux new -s <project-name>

# 2. 在 tmux 会话中启动 Claude Code
claude

# 3. 创建团队并启动agents
TeamCreate → Agent() × N

# 4. 完成后分离会话
Ctrl+b d

# 5. 随时重新连接
tmux attach -t <project-name>
```

**成功案例**: `tmux new -s tools-update-news5` 启动 video-subtitle-txt 项目团队，协调 react-dev 和 backend-dev 并行开发

## tmux 配合使用

### tmux 会话管理
```bash
# 创建新会话
tmux new -s <session-name>

# 分离会话 (Ctrl+b d)
# 重新连接
tmux attach -t <session-name>

# 列出所有会话
tmux list-sessions
```

### 与 Agent Teams 配合
在 tmux 会话中运行 Agent Teams 可以：
1. **会话保持**: 即使 SSH 断开，团队工作继续运行
2. **多团队并行**: 不同 tmux 会话运行不同项目团队
3. **日志分离**: 每个团队的输出在独立会话中，便于追踪

### 推荐工作流
```bash
# 1. 创建项目会话
tmux new -s <project-name>

# 2. 在会话中启动 Agent Team
Agent Tool → TeamCreate → Agent()

# 3. 团队并行工作，日志实时输出

# 4. 完成后分离会话
Ctrl+b d

# 5. 之后可随时重新连接查看结果
tmux attach -t <project-name>
```
