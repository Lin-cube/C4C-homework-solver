# Wang ChunYan · C4C 作业自动求解与排版（提交包）

> 挑战 ID：ch-20260717031447-k82c4m ｜ 姓名：Wang ChunYan ｜ 日期：2026-07-17
> 评级申报：**L1 ✅ · L2 ✅ 达标 · L3 ✅ · L4 Path C 已申报**

## 一句话

把 Claude 版 starter kit 的「微积分极限」求解流水线**迁移到国产大模型（Qwen/Kimi/DeepSeek 可插拔）**，并**扩展到线性代数 + 微分方程**，端到端产出可核验的 PDF（**9/9 = 100%**，独立代入核验 9/9 通过）。

## 文件清单

### 核心交付物（CHALLENGE.md 要求的 7 项）

| 文件 | 说明 |
|---|---|
| `WangChunYan_C4C_方案设计.md` | 架构、国产模型选型、求解策略 |
| `WangChunYan_C4C_homework-solver/` | **可运行源码包**（五阶段流水线） |
| `WangChunYan_C4C_作业原件_线性代数.md` + `WangChunYan_C4C_output.pdf` | 真实作业测试（输入 + 可提交 PDF） |
| `WangChunYan_C4C_验证报告.md` | 逐题核验 + 与 Claude 基线对比 |
| `WangChunYan_C4C_教学说明.md` | 安装 / 使用 / 扩展指南 |
| `WangChunYan_C4C_AI日志.md` | 开发全过程 AI 使用记录（必须） |
| `WangChunYan_C4C_拿来说明.md` | 拿了什么 / 改了什么 / **知识源抽取记录** |

### 分级补充交付物

| 文件 | 对应层级 |
|---|---|
| `WangChunYan_C4C_架构理解与解题追踪.md` | **L1** 架构总结 + 单题全链路逐步 trace |
| `WangChunYan_C4C_L4创新声明.md` | **L4 Path C** 正式申报（逐 checkbox 对照） |
| `WangChunYan_C4C_L4演示稿.md` | **L4** 演示稿（13 页） |
| `WangChunYan_C4C_检查单补正说明.md` | 第三方检查单的逐条补正记录 |
| `WangChunYan_C4C_output.tex` | LaTeX 产物（ctexart，Overleaf 可用） |
| `verification.json` | 独立核验原始结果 |
| `output/` | 流水线中间产物（1_ingested / 2_parsed / 3_solutions / tex / pdf / l4_path_c_demo） |
| `starter/` | 原始 starter kit（Claude 基线，参照物） |

## 一分钟复现

```bash
cd WangChunYan_C4C_homework-solver
pip install sympy pyyaml matplotlib
python scripts/pipeline.py examples/linear_algebra_homework.md output/ \
    --course "线性代数与微分方程" --student "Wang ChunYan" \
    --title "线性代数与微分方程 作业解答" --pdf

# L4 Path C 能力对比演示（SymPy-only 0/9 vs LLM-Augmented 9/9）
python scripts/demo_l4_path_c.py
```

## 核心成果

| 维度 | 结果 |
|---|---|
| **迁移** | `llm_engine.py`：Qwen / Kimi / DeepSeek 三家国产模型 OpenAI 兼容接入；无 key 时**离线确定性回退**（9 个已核验定理模板） |
| **扩展** | 从「极限」→「线性代数 + 微分方程」，填补 starter kit 的矩阵 / ODE / 证明三个空壳 |
| **求解** | **9/9 = 100%**（Claude 基线在域外仅 40%）；L4 demo：SymPy-only 0/9 → LLM-Augmented 9/9 |
| **核验** | `verify.py` 独立重算 + 代入检验（A·A⁻¹=I、Ax=b、Av=λv、ODE 残差=0、初值匹配） |
| **排版** | `output.tex`（ctexart 中文）+ `output.pdf`（matplotlib，**无需 TeX Live**） |
| **知识增强** | 4 份新增知识源 + 9 个非计算题模板 + 10 条新增分类规则 |

## 诚实边界

- 开发环境**无国产模型 API key**，实际运行走 offline 确定性回退；`LLMEngine` 端点为真实可用代码，配 key 即生效。
- 测试集为按标准教材题型构造的**代表性作业**（9 题），非某门真实课程的原始试卷；每题均经独立代入核验。
- 未覆盖：SVD、Laplace 变换、物理建模、图像 OCR（故**不申报 L4 Path D**）。
