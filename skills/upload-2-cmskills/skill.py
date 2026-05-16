#!/usr/bin/env python3
"""upload-2-cmskills - Upload skill to cm-skills repository"""
import os
import subprocess
import sys

def upload_skill(skill_name: str) -> dict:
    """Upload a skill to cm-skills GitHub repository."""
    cm_skills_path = os.path.expanduser("~/Desktop/claude/cm-skills")
    local_skills_path = os.path.expanduser("~/.claude/skills")

    # Check if cm-skills exists, clone if not
    if not os.path.exists(cm_skills_path):
        print(f"Cloning cm-skills repository...")
        subprocess.run([
            "git", "clone", "https://github.com/cangming009/cm-skills.git",
            cm_skills_path
        ], check=True)

    # Source and destination paths
    src_path = os.path.join(local_skills_path, skill_name)
    dst_path = os.path.join(cm_skills_path, "skills", skill_name)

    # Check if skill exists locally
    if not os.path.exists(src_path):
        return {"ok": False, "error": f"Skill '{skill_name}' not found in ~/.claude/skills/"}

    # Create destination directory
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)

    # Copy skill files (excluding .git and large directories)
    subprocess.run(["cp", "-r"] + [
        os.path.join(src_path, f) for f in os.listdir(src_path)
        if f != ".git" and not f.endswith(".pyc")
    ] + [dst_path], check=True)

    # Git add, commit, push
    subprocess.run(["git", "-C", cm_skills_path, "add", "-A"], check=True)
    subprocess.run([
        "git", "-C", cm_skills_path, "commit",
        "-m", f"Add {skill_name} skill"
    ], check=True)
    subprocess.run(["git", "-C", cm_skills_path, "push"], check=True)

    return {
        "ok": True,
        "skill_name": skill_name,
        "path": f"https://github.com/cangming009/cm-skills/tree/main/skills/{skill_name}"
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: upload-2-cmskills <skill-name>")
        sys.exit(1)

    result = upload_skill(sys.argv[1])
    print(result)