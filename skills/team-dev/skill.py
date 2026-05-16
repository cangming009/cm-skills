"""
teams-multi-model skill v2.2

功能:
1. 自动识别当前项目
2. 自动生成/更新 CLAUDE.md 规则
3. 输出协作规则
4. 团队配置门禁检查 - 自动修复禁止的模型

使用方法:
/teams-multi-model {任务}
"""

import json
import os
from datetime import datetime

TEAMS_DIR = os.path.expanduser("~/.claude/teams/")

# 禁止使用的模型列表
FORBIDDEN_MODELS = [
    "claude-opus-4-6",
    "opus-4-6",
    "opus",
]

# 替换模型
DEFAULT_REPLACEMENT_MODEL = "sonnet"


def fix_team_config(config_path: str, auto_fix: bool = True) -> dict:
    """
    验证并修复团队配置文件

    Args:
        config_path: 团队配置文件路径
        auto_fix: 是否自动修复问题

    Returns:
        dict: 验证结果 {"valid": bool, "errors": list, "warnings": list, "fixed": list}
    """
    result = {"valid": True, "errors": [], "warnings": [], "fixed": []}

    if not os.path.exists(config_path):
        result["valid"] = False
        result["errors"].append(f"配置文件不存在: {config_path}")
        return result

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        result["valid"] = False
        result["errors"].append(f"配置文件 JSON 格式错误: {e}")
        return result

    # 检查成员配置
    members = config.get("members", [])
    if not members:
        result["warnings"].append("团队没有配置任何成员")
        return result

    needs_save = False

    for i, member in enumerate(members):
        member_name = member.get("name", f"成员{i+1}")
        model = member.get("model", "")

        # 检查是否设置了模型
        if not model:
            result["warnings"].append(
                f"[{member_name}] 未指定 model 字段，将使用默认模型"
            )
            continue

        # 检查是否使用了禁止的模型
        model_lower = model.lower()
        is_forbidden = False
        for forbidden in FORBIDDEN_MODELS:
            if forbidden in model_lower:
                is_forbidden = True
                break

        if is_forbidden:
            if auto_fix:
                # 自动修复
                member["model"] = DEFAULT_REPLACEMENT_MODEL
                needs_save = True
                result["fixed"].append(
                    f"[{member_name}] '{model}' -> '{DEFAULT_REPLACEMENT_MODEL}'"
                )
            else:
                result["valid"] = False
                result["errors"].append(
                    f"[{member_name}] 禁止使用模型 '{model}'！"
                    f"请使用 'sonnet' 或 'haiku'"
                )

    # 保存修复后的配置
    if needs_save:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    return result


def check_and_fix_all_teams(auto_fix: bool = True) -> dict:
    """
    检查并修复所有团队配置

    Args:
        auto_fix: 是否自动修复问题

    Returns:
        dict: 检查结果 {"checked": int, "fixed": int, "details": list}
    """
    result = {"checked": 0, "fixed": 0, "details": []}

    if not os.path.exists(TEAMS_DIR):
        return result

    for team_dir in os.listdir(TEAMS_DIR):
        config_path = os.path.join(TEAMS_DIR, team_dir, "config.json")
        if os.path.exists(config_path):
            result["checked"] += 1
            fix_result = fix_team_config(config_path, auto_fix)

            if fix_result["fixed"]:
                result["fixed"] += 1
                result["details"].append({
                    "team": team_dir,
                    "fixes": fix_result["fixed"]
                })

            if not fix_result["valid"] and not auto_fix:
                result["details"].append({
                    "team": team_dir,
                    "errors": fix_result["errors"]
                })

    return result


def get_project_name():
    """自动识别项目名称"""
    cwd = os.getcwd()
    # 尝试读取 package.json
    pkg = os.path.join(cwd, "package.json")
    if os.path.exists(pkg):
        with open(pkg) as f:
            return json.load(f).get("name", os.path.basename(cwd))

    # 尝试读取 go.mod
    gomod = os.path.join(cwd, "go.mod")
    if os.path.exists(gomod):
        with open(gomod) as f:
            first = f.readline()
            if "module" in first:
                return first.split()[-1].split("/")[-1]

    return os.path.basename(cwd)


def get_claude_rules():
    """返回协作规则内容"""
    return """
## Agent Teams 协作规则

### 角色
- **team_leader**: 任务分配、进度追踪、关键决策
- **coder**: 代码实现、完成后通知 reviewer
- **reviewer**: 代码审查、提出改进建议、确认后批准

### 通信规则
- 任务开始 → SendMessage broadcast 开始通知
- 任务完成 → SendMessage 通知下一角色
- 遇到问题 → SendMessage broadcast 问题 + 私聊相关成员
- 代码审查 → 私聊 coder + 列出问题清单

### 工作流程
```
1. team_leader: TaskList → TaskUpdate 分配任务
2. coder: 开始编码 → SendMessage "完成"
3. reviewer: 审查代码 → SendMessage "批准" 或 "需修改"
4. 重复 2-3 直至通过
```

### 重要约束
1. 成员间必须通信同步，禁止独立行动
2. 代码必须经过 reviewer 审核后才能完成
3. 每完成一个任务，广播通知其他成员
"""


def update_claude_md(project_path: str) -> str:
    """更新项目的 CLAUDE.md，返回路径"""
    claude_path = os.path.join(project_path, "CLAUDE.md")
    rules = get_claude_rules()

    if os.path.exists(claude_path):
        # 检查是否已有协作规则
        with open(claude_path) as f:
            content = f.read()
            if "Agent Teams" in content or "team_leader" in content:
                return claude_path  # 已存在

        # 追加规则
        with open(claude_path, 'a') as f:
            f.write(rules)
        return claude_path
    else:
        # 创建新文件
        project_name = os.path.basename(project_path)
        content = f"""# CLAUDE.md - {project_name}

{get_claude_rules()}
"""
        with open(claude_path, 'w') as f:
            f.write(content)
        return claude_path


def run_skill(task: str = None):
    """执行 skill"""

    project_path = os.getcwd()
    project_name = get_project_name()
    team_name = f"team_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # 门禁检查：验证并自动修复所有团队配置
    check_result = check_and_fix_all_teams(auto_fix=True)

    # 输出修复结果
    if check_result["fixed"] > 0:
        print("")
        print("!" * 60)
        print("  🔧 自动修复团队配置")
        print("!" * 60)
        for detail in check_result["details"]:
            if "fixes" in detail:
                print(f"\n团队: {detail['team']}")
                for fix in detail["fixes"]:
                    print(f"  ✅ {fix}")
        print("")
        print("!" * 60)

    # 自动更新 CLAUDE.md
    claude_path = update_claude_md(project_path)

    print("")
    print("=" * 60)
    print(f"  [teams-multi-model] 项目: {project_name}")
    print("=" * 60)
    print(f"团队: {team_name}")
    print(f"任务: {task}")
    print(f"规则文件: {claude_path}")
    print("-" * 60)
    print(get_claude_rules())
    print("=" * 60)

    return {
        "status": "success",
        "team": team_name,
        "task": task,
        "project": project_name,
        "claude_md": claude_path,
        "fixed_teams": check_result["fixed"],
        "message": "CLAUDE.md 已自动更新"
    }


if __name__ == "__main__":
    import sys
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "处理任务"
    result = run_skill(task)
    print(json.dumps(result, indent=2, ensure_ascii=False))