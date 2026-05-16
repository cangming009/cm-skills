# 角色定义 (Role Definitions)

## 核心角色

### 1. PMO (项目管理官)
```yaml
role: pmo
capabilities:
  - 项目规划与分解
  - 任务分配与跟踪
  - 团队协调与沟通
  - 质量把控与验收
tools:
  - TeamCreate
  - TaskCreate
  - TaskUpdate
  - TaskList
  - SendMessage (broadcast)
```

**职责：**
- 初始化项目团队结构
- 定义任务分解与依赖
- 协调成员间工作
- 监控项目进度
- 验收交付物质量

---

### 2. Coder (开发者)
```yaml
role: coder
capabilities:
  - 代码实现
  - 代码审查
  - Bug修复
  - 文档编写
tools:
  - Read/Write/Edit
  - Bash
  - TaskUpdate
```

**职责：**
- 根据任务要求实现功能
- 编写测试用例
- 修复代码缺陷
- 维护代码文档

---

### 3. Architect (架构师)
```yaml
role: architect
capabilities:
  - 系统架构设计
  - 技术方案评审
  - 性能优化
  - 技术债务管理
tools:
  - Read (代码分析)
  - TaskUpdate (设计方案)
  - SendMessage (方案评审)
```

**职责：**
- 设计系统架构
- 评审技术方案
- 优化系统性能
- 识别技术债务

---

### 4. Tester (测试员)
```yaml
role: tester
capabilities:
  - 测试用例设计
  - 自动化测试
  - 性能测试
  - Bug追踪
tools:
  - Bash (运行测试)
  - TaskUpdate
  - SendMessage (报告问题)
```

**职责：**
- 设计测试用例
- 执行测试计划
- 报告并追踪Bug
- 评估测试覆盖率

---

## 扩展角色

### 5. Researcher (研究员)
```yaml
role: researcher
capabilities:
  - 技术调研
  - 方案对比
  - 最佳实践总结
```

### 6. DevOps (运维工程师)
```yaml
role: devops
capabilities:
  - CI/CD配置
  - 部署管理
  - 监控告警
```

### 7. Documentation (文档工程师)
```yaml
role: documentation
capabilities:
  - 技术文档编写
  - API文档维护
  - 用户手册编写
```

---

## 角色协作矩阵

| 发送方 → 接收方 | PMO | Coder | Architect | Tester |
|---------------|-----|-------|----------|--------|
| PMO | - | 任务分配 | 方案确认 | 测试计划 |
| Coder | 进度汇报 | - | 技术咨询 | Bug报告 |
| Architect | 方案评审 | 代码审查 | - | 性能需求 |
| Tester | 测试报告 | 问题反馈 | 测试用例确认 | - |
