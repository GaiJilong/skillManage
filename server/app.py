"""
AI Skills 管理后端
提供skills的增删改查API
"""
import os
import shutil
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="AI Skills Manager API")

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Skills目录路径
SKILLS_DIR = Path(__file__).parent.parent / "skills"


class SkillCreate(BaseModel):
    """创建Skill的请求体"""
    name: str
    content: str


class SkillUpdate(BaseModel):
    """更新Skill的请求体"""
    content: str


@app.get("/api/skills")
def list_skills():
    """
    获取所有skills列表
    返回: [{"name": "skill-name"}, ...]
    """
    skills = []
    
    if not SKILLS_DIR.exists():
        SKILLS_DIR.mkdir(parents=True, exist_ok=True)
        return skills
    
    for item in SKILLS_DIR.iterdir():
        if item.is_dir():
            skill_file = item / "SKILL.md"
            if skill_file.exists():
                skills.append({"name": item.name})
    
    # 按名称排序
    skills.sort(key=lambda x: x["name"])
    return skills


@app.get("/api/skills/{name}")
def get_skill(name: str):
    """
    获取单个skill的内容
    参数: name - skill名称（文件夹名）
    返回: {"name": "...", "content": "..."}
    """
    skill_dir = SKILLS_DIR / name
    skill_file = skill_dir / "SKILL.md"
    
    if not skill_file.exists():
        raise HTTPException(status_code=404, detail=f"Skill '{name}' not found")
    
    content = skill_file.read_text(encoding="utf-8")
    return {"name": name, "content": content}


@app.post("/api/skills")
def create_skill(skill: SkillCreate):
    """
    创建新的skill
    参数: name - skill名称, content - SKILL.md内容
    """
    # 验证名称格式
    if not skill.name or not skill.name.strip():
        raise HTTPException(status_code=400, detail="Skill name is required")
    
    # 规范化名称
    name = skill.name.strip().lower().replace(" ", "-")
    
    skill_dir = SKILLS_DIR / name
    
    if skill_dir.exists():
        raise HTTPException(status_code=400, detail=f"Skill '{name}' already exists")
    
    # 创建目录和文件
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(skill.content, encoding="utf-8")
    
    return {"name": name, "message": "Skill created successfully"}


@app.put("/api/skills/{name}")
def update_skill(name: str, skill: SkillUpdate):
    """
    更新skill内容
    参数: name - skill名称, content - 新内容
    """
    skill_dir = SKILLS_DIR / name
    skill_file = skill_dir / "SKILL.md"
    
    if not skill_file.exists():
        raise HTTPException(status_code=404, detail=f"Skill '{name}' not found")
    
    skill_file.write_text(skill.content, encoding="utf-8")
    return {"name": name, "message": "Skill updated successfully"}


@app.delete("/api/skills/{name}")
def delete_skill(name: str):
    """
    删除skill
    参数: name - skill名称
    """
    skill_dir = SKILLS_DIR / name
    
    if not skill_dir.exists():
        raise HTTPException(status_code=404, detail=f"Skill '{name}' not found")
    
    shutil.rmtree(skill_dir)
    return {"name": name, "message": "Skill deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
