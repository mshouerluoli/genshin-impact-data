# 原神数据项目

本项目包含《原神》游戏相关数据的JSON数据文件及配套处理程序。

## 项目简介

本仓库致力于收集和整理《原神》游戏中的各类数据，包括但不限于：

- 物品数据 (Item.json)
- 传送点数据 (teleport_tasks.json)
- 角色数据处理工具 (avatarlist.cpp)

## 数据说明

### 物品数据 (Item.json)

包含游戏中各类道具、武器、圣遗物等信息的数据集合。

**数据来源更新记录：**

| 数据来源目录 | 更新内容 | 更新数量 |
|---|---|---|
| `genshin-db-main\src\data\ChineseSimplified\enemies` | 更新了敌人名称数据 | 1 |
| `genshin-db-main\src\data\ChineseSimplified\characters` | 更新了角色名称数据 | 1 |
| `genshin-db-main\src\data\ChineseSimplified\materials` | 更新了各类素材、矿石、食材、天赋书、元素印等 | 855 |
| `genshin-db-main\src\data\ChineseSimplified\animals` | 更新了动物名称数据 | 2 |
| `genshin-db-main\src\data\ChineseSimplified\tcgcharactercards` | 更新了七圣召唤角色卡牌数据 | 113 |
| `genshin-db-main\src\data\ChineseSimplified\talents` | 更新了角色天赋数据 | 111 |

### 传送任务数据 (teleport_tasks.json)

包含游戏内传送点及相关任务数据。

### 角色列表处理 (avatarlist.cpp)

C++ 程序，用于处理和解析游戏角色数据。

## 使用方法

请参考各数据文件的具体格式说明进行使用。

## 贡献指南

欢迎提交 Pull Request 来完善数据内容。

## 许可证

请查看项目中的 LICENSE 文件了解具体许可协议。