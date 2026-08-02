# banksys_sy_monki — 银行营销数据分析与认购预测系统

基于银行营销数据，提供交互式数据分析看板与在线认购预测的 Web 应用。

## 功能

1. **数据分析交互页面** — 数据概览、单变量/双变量分析、可视化图表、联动筛选
2. **在线预测系统** — 点选表单输入客户信息，实时预测是否认购定期存款及概率

## 技术栈

| 层 | 选型 |
|---|---|
| 语言 | Python 3.11 |
| Web 框架 | Streamlit |
| ML 建模 | scikit-learn (Pipeline) |
| 测试 | pytest |
| 格式/静态检查 | ruff |
| 容器化 | Docker |
| CI/CD | GitHub Actions |

## 快速开始

### 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 将数据文件放入 data/ 目录（train.csv / test.csv）
#    若无数据，应用会自动生成合成样本用于演示

# 3. 启动应用
streamlit run app/app.py --server.port 8888
```

### 模型训练

```bash
python model/train.py
```

### Docker 运行

```bash
docker build -t banksys_sy_monki .
docker run -d -p 8888:8888 --name banksys_sy_monki banksys_sy_monki
```

### 本地 CI 检查

```bash
pip install -r requirements-dev.txt
ruff format --check .
ruff check .
pytest --cov --cov-fail-under=80
```

## 环境变量

| 变量 | 说明 |
|---|---|
| `PIP_INDEX_URL` | pip 镜像源（国内使用可设清华源） |

## 数据

应用使用 UCI Bank Marketing 风格数据。数据文件放入 `data/` 目录：

- `train.csv` — 含 `subscribe` 标签列的训练数据
- `test.csv` — 无标签的预测数据

> 数据文件不进 Git，需自行放置。应用在数据缺失时自动使用合成样本演示。

## 许可证

[MIT License](LICENSE)