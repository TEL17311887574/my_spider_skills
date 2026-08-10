# my_spider_skills

本仓库包含多个 Web / JS 逆向相关的技能包，并使用 **git 子模块**管理上游技能。

## 克隆本仓库

子模块不会随普通 `git clone` 自动拉取，请按以下方式操作：

```bash
git clone https://github.com/TEL17311887574/my_spider_skills.git
cd my_spider_skills
git submodule update --init --remote --recursive
```

> `--init`：首次初始化并拉取子模块；`--remote`：同时更新到上游最新版本；`--recursive`：递归处理所有子模块。
> 已初始化后重复运行此命令同样安全，不会报错。

或者一步到位（等价于上面三行）：

```bash
git clone --recurse-submodules https://github.com/TEL17311887574/my_spider_skills.git
```

## 添加新子模块

不要手动编辑 `.gitmodules`，直接用命令一步到位：

```bash
git submodule add <仓库URL> <本地目录名>
```

示例：

```bash
git submodule add https://github.com/xxx/skill.git skill-name
```

该命令会自动写入 `.gitmodules`、克隆内容到本地目录、并在索引中记录子模块 commit。
