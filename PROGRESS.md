# PROGRESS.md — 项目进度活记忆

> **作用**:记录当前状态、已完成事项、下一步 TODO、架构决策(ADR)和踩坑记录(GOTCHAS)。
> **更新时机**:每个模块完成、每步确认门、每次故障修复后更新。保持倒序、简洁、可接力。

---

## 当前状态

- **六步流程步骤**: 第⑥步 — CD 修复中（第 3 轮）
- **当前分支**: `main`（PR #1、PR #2 已合并）
- **最后操作**: 修复 Dockerfile（移除 curl 依赖，Python stdlib 健康检查）+ CD timeout 30m
- **CD 状态**: ✅ 第 6 轮部署成功 (2026-08-02)

---

## 已完成

- [x] 读取所有标准文档，填写 00/01/PROGRESS
- [x] 第①步: 建仓 + 配置 Secrets
- [x] 第②步: 切出 feature/1-project-init 分支
- [x] 第③步: 模块化开发（US-2 分析页 + US-3 模型训练 + US-4 在线预测）
- [x] 第④步: 本地 CI 自检（ruff format ✅, ruff check ✅, pytest 20/20 ✅, cov 93% ✅）
- [x] 第⑤步: PR #1 创建 → CI 复检全绿 ✅（最终 19/20 → 20/20）
- [x] **PR #1 合并** ✅ → CD 自动触发
- [x] **PR #2 修复** CD 脚本（rsync 替代 git clone）→ 合并 ✅
- [x] **第 2 轮** CD 修复（去除 curl 依赖、增加超时 30m）→ 直接推送 main ✅

---

## 待办（下一步）

- [ ] TODO: 等待 CD 第 3 轮运行完毕
- [ ] TODO: 如果 CD 通过，汇报最终访问地址和端口
- [ ] TODO: 如 CD 仍有问题，继续排查

---

## 架构决策记录 (ADR)

| ADR | 日期 | 决策 | 理由 |
|---|---|---|---|
| ADR-001 | 2026-08-02 | Streamlit 多页面架构（app.py + pages/） | 天然支持路由、侧边栏导航 |
| ADR-002 | 2026-08-02 | sklearn Pipeline 一体化保存（预处理器+模型） | 确保预测时预处理与训练一致 |
| ADR-003 | 2026-08-02 | 合成数据回退机制 | 无真实数据时仍可演示，CI 不依赖外部数据 |
| ADR-004 | 2026-08-02 | CD 采用 rsync 替代 git clone | 避免服务器端认证问题 |
| ADR-005 | 2026-08-02 | 健康检查用 Python stdlib 替代 curl | 减少 Docker 镜像大小和构建时间 |

---

## 踩坑记录 (GOTCHAS)

| 日期 | 现象 | 根因 | 修复 | 对应规范 |
|---|---|---|---|---|
| 2026-08-02 | ruff format 本地通过、CI 失败 | 本地 ruff 0.6.9 与 CI ruff 0.9+ 格式规则不一致 | 手动调整 import 排序和空行 | 05-cicd-standards.md |
| 2026-08-02 | sklearn OneHotEncoder 报 `sparse=False` 参数错误 | 本地 sklearn 旧版用 `sparse`，新版用 `sparse_output` | try/except 兼容两者 | 05-cicd-standards.md |
| 2026-08-02 | ROC 曲线绘制失败 | 旧版 sklearn 无 `RocCurveDisplay.from_predictions` | 改用 `roc_curve()` + matplotlib | 03-testing-standards.md |
| 2026-08-02 | CD 端口检测全部失败 | shell 函数在多行 SSH 脚本中被 | 改用内联 for 循环 + 函数定义 | 05-cicd-standards.md |
| 2026-08-02 | Docker build 超时 >10 分钟 | apt-get 安装 curl 依赖过多 + 默认 SSH timeout 10m | 移除 curl(Python 替代) + command_timeout=30m | 05-cicd-standards.md |