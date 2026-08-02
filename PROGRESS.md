# PROGRESS.md — 项目进度活记忆

> **作用**:记录当前状态、已完成事项、下一步 TODO、架构决策(ADR)和踩坑记录(GOTCHAS)。
> **更新时机**:每个模块完成、每步确认门、每次故障修复后更新。保持倒序、简洁、可接力。

---

## 当前状态

- **六步流程步骤**: 第①步前 — 需求/上下文文档填写完毕,等待确认后开始建仓。
- **当前分支**: (尚未建仓)
- **最后操作**: 完成了 `00-project-context.md`、`01-requirements.md` 的填写及本文件初始化。

---

## 已完成

- [x] 读取 `standards/README.md`,理解项目结构与规范体系
- [x] 读取 `standards/00-project-context.md` 模板,按项目实际填写完整
- [x] 读取 `standards/01-requirements.md` 模板,拆分为 4 个用户故事并附验收标准
- [x] 读取 `standards/02~06` 通用规范,确认编码/测试/Git/CI-CD/AI 协作规则
- [x] 本项目初期化 PROGRESS.md

---

## 第一批 TODO

### 第①步 · 建仓 + 配 Secrets

- [ ] TODO-1: 用 `gh repo create` 创建公开仓库 `banksys_sy_monki`
- [ ] TODO-2: 初始化 `.gitignore`(含 `data/`、`model/saved_models/`、`__pycache__/` 等)
- [ ] TODO-3: 初始化 README.md(项目简介、技术栈、快速开始)
- [ ] TODO-4: 添加开源 LICENSE(如 MIT)
- [ ] TODO-5: 创建 `main` 分支最小引导提交
- [ ] TODO-6: ✋ **提示人类配置 GitHub Secrets**(SSH_PRIVATE_KEY/SSH_HOST/SSH_USER)

### 第②步 · 开 feature 分支

- [ ] TODO-7: 从 `main` 切出 `feature/1-project-init` 分支

### 第③步 · 本地模块化开发

- [ ] TODO-8: 搭建项目目录结构(data/app/model/tests 等)
- [ ] TODO-9: 创建 `requirements.txt` + `requirements-dev.txt`
- [ ] TODO-10: 实现 US-2 — 数据交互分析页面
  - [ ] 数据加载模块(支持真实数据与合成数据 fallback)
  - [ ] 数据概览页面
  - [ ] 单变量分析页面(直方图+柱状图)
  - [ ] 双变量分析页面(散点图+分组图+认购着色)
  - [ ] 筛选面板（联动刷新）
- [ ] TODO-11: 实现 US-3 — 离线模型训练
  - [ ] 数据预处理 Pipeline(标准化+编码)
  - [ ] 模型训练脚本(train.py, 含评估输出)
  - [ ] 特征/模型保存逻辑
- [ ] TODO-12: 实现 US-4 — 在线预测系统
  - [ ] 点选预测表单(动态生成控件)
  - [ ] 预测结果展示(认购/不认购 + 概率)
  - [ ] 特征对比可视化(雷达图/条形图)
  - [ ] 模型状态检测(未就绪时友好提示)

### 第④步 · 本地 CI 自检

- [ ] TODO-13: 编写核心逻辑单元测试
- [ ] TODO-14: `ruff format --check .` + `ruff check .` 通过
- [ ] TODO-15: `pytest --cov --cov-fail-under=80` 通过
- [ ] TODO-16: ✋ 汇报自检结果,确认全绿

### 第⑤步 · 触发 PR

- [ ] TODO-17: `git push` 并 `gh pr create`
- [ ] TODO-18: 等待 PR CI 运行(含 docker build)
- [ ] TODO-19: ✋ 汇报 PR 链接与 CI 状态

### 第⑥步 · 人工审核 → 合并 → CD

- [ ] TODO-20: ✋ **AI 停下**,等待人类 Review 与合并
- [ ] TODO-21: 合并后自动触发 CD,AI 盯流水线
- [ ] TODO-22: ✋ 汇报部署结果(端口/health/访问地址)

---

## 架构决策记录 (ADR)

> 空 — 尚未产生架构决策。

| ADR | 日期 | 决策 | 理由 |
|---|---|---|---|
|—|—|—|—|

---

## 踩坑记录 (GOTCHAS)

> 空 — 尚未踩坑。

| 日期 | 现象 | 根因 | 修复 | 对应规范 |
|---|---|---|---|---|
|—|—|—|—|—|