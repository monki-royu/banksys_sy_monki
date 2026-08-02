# 00 · 项目上下文 〔本项目活记忆 · AI 维护〕

> **作用**:这是项目的"身份档案"。AI 接管项目时先读这里,了解项目目标、技术栈、目录、部署取值。
> **更新时机**:架构、技术栈、目录结构、端口、部署目录、重要约束变化时更新。

---

## 1. 项目是什么

- **项目名称**: `banksys_sy_monki`
- **一句话目标**:基于银行营销数据,构建数据分析交互页面与在线认购预测系统,帮助银行营销人员快速洞察数据并通过点选表单预测客户是否会认购定期存款。
- **使用者/受益者**:银行营销人员/数据分析师,通过交互式分析页面理解客户特征与认购关系,利用离线训练的 ML 模型在线预测潜在客户认购倾向。
- **核心功能**:
  - 数据交互分析页面:展示银行营销数据集概况、单变量/双变量分析、可视化图表,支持按字段筛选过滤
  - 在线预测系统:离线训练分类模型(如 Logistic Regression / XGBoost 等),通过 Streamlit 点选表单输入客户信息,实时返回是否认购的预测结果及概率
- **输入/数据**:基于 UCI Bank Marketing Dataset 或等价银行营销数据(约 4 万+ 样本,20+ 特征,含数值与分类变量),数据不敏感、公开教学数据可入库。**数据文件不进入 Git**,在 CI/CD 流程中从外部源下载或使用合成样本。

## 2. 技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| 语言/运行时 | Python 3.11 | 教学项目标准,数据分析与 ML 生态成熟 |
| Web 框架 | Streamlit | 快速构建交互式数据应用,天然支持表单/图表组件 |
| ML 建模 | scikit-learn (Logistic Regression / Random Forest) | 轻量、教学友好、支持分类与概率输出 |
| 测试 | pytest | Python 标准测试框架 |
| 格式/静态检查 | ruff | 快速、统一格式与 lint |
| 打包/运行 | Docker + Docker Compose | 容器化部署,环境一致 |
| CI/CD | GitHub Actions | 通用、可视化、适合教学与团队协作 |

## 3. 目录地图

```text
banksys_sy_monki/
├── standards/                  # AI 项目记忆与通用规范
├── data/                       # 数据目录(不进 Git,仅占位)
│   └── .gitkeep
├── app/                        # Streamlit 应用主目录
│   ├── pages/                  # 多页面(分析页、预测页)
│   ├── components/             # 可复用 UI 组件
│   └── app.py                  # 入口
├── model/                      # 模型训练相关
│   ├── train.py                # 离线训练脚本
│   ├── predict.py              # 预测逻辑
│   └── saved_models/           # 训练产物(不进 Git)
├── tests/                      # 测试目录
│   ├── test_analysis.py
│   ├── test_prediction.py
│   └── conftest.py
├── requirements.txt            # 生产运行依赖
├── requirements-dev.txt        # 本地/CI 检查依赖(dev)
├── Dockerfile                  # 容器构建
├── docker-compose.yml          # 部署编排(可选)
├── .github/workflows/
│   ├── ci.yml                  # PR/push 触发:格式+lint+测试+构建
│   └── cd.yml                  # main 合并触发:SSH 部署+健康检查
├── .gitignore
├── .dockerignore
├── README.md
└── LICENSE                     # 开源许可证
```

> 新增目录前先更新本节,避免项目越做越散。

## 4. 质量门槛

| 类型 | 本项目标准 |
|---|---|
| 格式检查 | `ruff format --check .` |
| 静态检查 | `ruff check .` |
| 单元测试 | `pytest -v` |
| 覆盖率 | `>= 80%` |
| 构建 | `docker build -t banksys_sy_monki .` 成功 |
| 业务/模型指标 | 模型 AUC >= 0.80(F1 >= 0.60);预测接口响应 < 2s |

## 5. 不变约束

- 密钥、密码、私钥、Token **绝不写进代码或文档**,只进 GitHub Secrets / 环境变量。
- 大文件、数据集、模型产物不进 Git(数据文件 + `.pkl`/`.joblib` 在 `.gitignore` 中排除)。
- `main` 分支受保护,日常开发必须走 feature 分支 + PR。
- CI 红灯不合并。
- 容器内端口固定 8888,主机端口在 8888-8898 区间自动回退。

## 6. 部署/CI 占位符取值

| 占位符 | 本项目取值 | 说明 |
|---|---|---|
| `<APP>` | `banksys_sy_monki` | 应用名/镜像名/容器名 |
| `<DEPLOY_DIR>` | `/opt/banksys_sy_monki` | 服务器部署目录 |
| `<PORT>` | `8888` | 服务端口(容器内固定) |
| `<PORT_MAX>` | `8898` | 主机端口回退上限 |
| `<PYVER>` | `3.11` | Python 版本 |
| `<HEALTHCHECK>` | `/health` | 健康检查地址 |
| `<SSH_USER>` | `root` 或 `deploy` | 部署用户 |
| `<SSH_HOST>` | 待定(部署时配置) | 服务器公网 IP 或域名 |