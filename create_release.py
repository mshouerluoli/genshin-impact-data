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
ACCESS_TOKEN = "7ab29f15b5a3df3c0ff43c6c15471698"  # Gitee 私人令牌
OWNER = "meow_paz"            # 仓库所有者
REPO = "genshin-impact-data"  # 仓库名
TARGET_BRANCH = "master"      # 目标分支
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
