#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gitee Release 创建脚本
输入标题、描述、上传文件，自动完成 tag 创建、release 发布和文件上传
支持多文件上传（用空格分隔多个文件路径）
"""

import requests
import json
import sys
import subprocess
import os
from datetime import datetime

# ============ 配置区 ============
# 尝试多个可能的配置文件路径
CONFIG_PATHS = [
    os.path.join(os.environ.get("APPDATA", ""), "gitee-release-cli-nodejs", "Config", "config.json"),
    os.path.join(os.path.expanduser("~"), ".gitee-release-cli-config.json"),
    os.path.join(os.path.expanduser("~"), ".gitee-release", "config.json"),
    os.path.join(os.environ.get("USERPROFILE", ""), ".config", "gitee-release-cli", "config.json"),
]

ACCESS_TOKEN = None

for CONFIG_PATH in CONFIG_PATHS:
    if os.path.exists(CONFIG_PATH):
        print(f"找到配置文件: {CONFIG_PATH}")
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
                ACCESS_TOKEN = config.get("accessToken") or config.get("access_token") or config.get("token")
                if ACCESS_TOKEN:
                    print("成功从配置文件读取到 token")
                    break
        except Exception as e:
            print(f"读取失败: {e}")

# 如果没有，从环境变量读取
if not ACCESS_TOKEN:
    ACCESS_TOKEN = os.environ.get("GITEE_ACCESS_TOKEN")
    if ACCESS_TOKEN:
        print("从环境变量读取到 token")

if not ACCESS_TOKEN:
    print()
    print("未找到配置文件，尝试了以下路径:")
    for p in CONFIG_PATHS:
        print(f"  - {p}")
    print()
    print("请先运行: gitee-release config accessToken 你的令牌")
    print("或者设置环境变量: setx GITEE_ACCESS_TOKEN 你的令牌")
    sys.exit(1)

# ============ 从 .git\config 读取仓库信息 ============
def get_git_info():
    """从 .git\config 读取仓库信息"""
    git_config_path = os.path.join(os.getcwd(), ".git", "config")
    if not os.path.exists(git_config_path):
        return None, None, None
    
    owner = None
    repo = None
    branch = None
    
    with open(git_config_path, "r", encoding="utf-8") as f:
        content = f.read()
        
        # 解析 remote origin URL: git@gitee.com:meow_paz/genshin-impact-data.git
        import re
        match = re.search(r'url\s*=\s*git@[^:]+:([^/]+)/([^/.]+)', content)
        if match:
            owner = match.group(1)
            repo = match.group(2)
        
        # 解析当前分支
        match = re.search(r'\[branch\s+"([^"]+)"\]', content)
        if match:
            branch = match.group(1)
    
    return owner, repo, branch

OWNER, REPO, TARGET_BRANCH = get_git_info()

if not OWNER or not REPO:
    OWNER = input("请输入仓库所有者 (owner): ").strip()
    REPO = input("请输入仓库名 (repo): ").strip()

if not TARGET_BRANCH:
    TARGET_BRANCH = input("请输入目标分支 (默认 master): ").strip() or "master"

print(f"仓库: {OWNER}/{REPO}  分支: {TARGET_BRANCH}")
# =================================

print("=" * 50)
print("        Gitee Release 发布工具")
print("=" * 50)
print()

# 输入
TAG_NAME = input("请输入版本号 (如 v1.0.0): ").strip()
RELEASE_NAME = input("请输入发布标题: ").strip()

print("请输入发布描述 (支持 Markdown，输入完成后按 Ctrl+Z 回车结束):")
lines = []
while True:
    try:
        line = input()
        lines.append(line)
    except EOFError:
        break
RELEASE_BODY = "\n".join(lines)

FILE_PATHS_INPUT = input("请输入要上传的文件路径（多个文件用空格分隔）: ").strip()
FILE_PATHS = FILE_PATHS_INPUT.split()

# 检查文件是否存在
for fp in FILE_PATHS:
    if not os.path.exists(fp):
        print(f"错误：文件不存在: {fp}")
        sys.exit(1)

print()
print("=" * 50)
print("开始创建 Release...")
print("=" * 50)

# 1. 创建/更新 Tag
print()
print("[1/4] 创建 Tag...")

# 先删除本地和远程的旧 tag（如果存在）
subprocess.run(["git", "tag", "-d", TAG_NAME], capture_output=True)
subprocess.run(["git", "push", "origin", f":refs/tags/{TAG_NAME}"], capture_output=True)

# 创建新 tag
result = subprocess.run(["git", "tag", TAG_NAME], capture_output=True, text=True)
if result.returncode != 0:
    print(f"创建 tag 失败: {result.stderr}")
    sys.exit(1)

# 推送 tag
result = subprocess.run(["git", "push", "origin", TAG_NAME], capture_output=True, text=True)
if result.returncode != 0:
    print(f"推送 tag 失败: {result.stderr}")
    sys.exit(1)

print(f"Tag {TAG_NAME} 创建成功")

# 2. 检查 release 是否存在，存在则删除
print()
print("[2/4] 检查旧 Release...")

list_url = f"https://gitee.com/api/v5/repos/{OWNER}/{REPO}/releases"
list_response = requests.get(list_url, params={"access_token": ACCESS_TOKEN})

if list_response.status_code == 200:
    releases = list_response.json()
    for rel in releases:
        if rel.get("tag_name") == TAG_NAME:
            print(f"发现旧 Release，删除中...")
            delete_url = f"https://gitee.com/api/v5/repos/{OWNER}/{REPO}/releases/{rel['id']}"
            requests.delete(delete_url, params={"access_token": ACCESS_TOKEN})
            print("旧 Release 已删除")
            break

# 3. 创建 Release
print()
print("[3/4] 创建 Release...")

create_url = f"https://gitee.com/api/v5/repos/{OWNER}/{REPO}/releases"
data = {
    "access_token": ACCESS_TOKEN,
    "tag_name": TAG_NAME,
    "target_commitish": TARGET_BRANCH,
    "name": RELEASE_NAME,
    "body": RELEASE_BODY
}

response = requests.post(create_url, json=data)

if response.status_code == 201:
    release_info = response.json()
    release_id = release_info["id"]
    print(f"Release 创建成功")
else:
    print(f"创建 Release 失败: {response.status_code}")
    print(response.text)
    sys.exit(1)

# 4. 上传文件
print()
print(f"[4/4] 上传文件 ({len(FILE_PATHS)} 个)...")

upload_url = f"https://gitee.com/api/v5/repos/{OWNER}/{REPO}/releases/{release_id}/attach_files"

for i, FILE_PATH in enumerate(FILE_PATHS, 1):
    FILE_NAME = os.path.basename(FILE_PATH)
    FILE_SIZE = os.path.getsize(FILE_PATH)
    print(f"  [{i}/{len(FILE_PATHS)}] 上传 {FILE_NAME} ({FILE_SIZE} bytes)...")
    
    with open(FILE_PATH, "rb") as f:
        files = {"file": (FILE_NAME, f)}
        data = {"access_token": ACCESS_TOKEN}
        response = requests.post(upload_url, files=files, data=data)
    
    if response.status_code == 200 or response.status_code == 201:
        print(f"  [{i}/{len(FILE_PATHS)}] {FILE_NAME} 上传成功")
    else:
        print(f"  [{i}/{len(FILE_PATHS)}] {FILE_NAME} 上传失败: {response.status_code}")
        print(response.text)

print()
print("=" * 50)
print("发布完成喵～")
print(f"标题: {RELEASE_NAME}")
print(f"文件: {len(FILE_PATHS)} 个")
print(f"地址: {release_info.get('html_url')}")
print("=" * 50)
