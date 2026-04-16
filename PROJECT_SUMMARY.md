# 项目总结 - Some Skills

这个文件保留为仓库级补充说明，但当前以 [README.md](./README.md) 和 [CONTRIBUTING.md](./CONTRIBUTING.md) 为准。

## 当前定位

`some-skills` 已经从“单个 skill 项目”演进为“多 skill 持续扩展仓库”。现在更重要的不是为某一个 skill 设计特殊结构，而是把以下约定固定下来：

- 所有可安装 skill 都放在 `skills/<skill-name>/`
- 每个 skill 只强制要求 `SKILL.md`
- `scripts/`、`references/`、`evals/`、`assets/` 都是按需添加
- 评测和实验产物放在 sibling `*-workspace/` 目录，不进入 git
- token、state、用户本地配置放在仓库外或 gitignored 文件中

## 当前技能

- `pr-reminder`
  - GitHub PR 状态分析与提醒
  - 依赖外部 GitHub 数据和本地状态对比
- `ernie-image`
  - ERNIE-Image / ERNIE-Image-Turbo 文生图
  - 支持 Access Token、本地 config、参数玩法和评测闭环

## 仓库层面的统一要求

后续新增 skill 时，至少同步检查这几件事：

1. `README.md` 中的技能目录是否已更新
2. `.claude/INSTALL.md` 是否仍然符合实际安装方式
3. `CONTRIBUTING.md` 的结构约定是否仍然准确
4. 新 skill 是否把 secrets、评测产物、本地状态和正式代码分开

## 为什么要这样收口

随着 skill 种类增加，仓库最容易失真的地方不是代码，而是“文档写的结构”和“真实目录结构”逐渐分叉。现在这份仓库级约定的目标，就是让之后的新 skill 合并进来时，大家还能沿着同一套规则扩展，而不是每加一个 skill 就重发明一次目录和文档规范。
