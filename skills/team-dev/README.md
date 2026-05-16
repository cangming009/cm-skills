# 国产模型协同工作技能包

## 快速开始

```bash
# 创建 PMO 团队
/claude-code-skill use teams-multi-model --role pmo --project "项目名称"

# 创建开发者团队
/claude-code-skill use teams-multi-model --role coder --project "项目名称"
```

## 文件结构

```
teams-multi-model/
├── skill.md      # 技能使用说明
├── role.md       # 角色定义
├── protocol.md   # 协作协议
└── README.md     # 本文件
```

## 核心流程

```
1. 创建团队 → 2. 分配角色 → 3. 分解任务 → 4. 协同开发 → 5. 验收交付
```

## 最佳实践

- **清晰分工**: 避免角色重叠
- **及时同步**: 重要决策广播
- **文档记录**: 关键讨论留存
- **定期回顾**: 持续改进流程
