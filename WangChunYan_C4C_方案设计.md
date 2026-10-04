# Wang ChunYan · C4C 方案设计文档

> 挑战：C4C 作业自动求解与排版 ｜ 姓名：Wang ChunYan ｜ 日期：2026-07-17
> 一句话：把 Claude 版 starter kit 的「微积分极限」求解流水线，迁移到**国产大模型**，并扩展到**线性代数 + 微分方程**，端到端产出可核验的 PDF。

---

## 1. 目标与范围

| 项 | 内容 |
|---|---|
| 迁移引擎 | 把流水线从「Claude Code 绑定」改为**国产大模型可插拔**（Qwen / Kimi / DeepSeek + 离线确定性回退） |
| 扩展学科 | 从「微积分极限」扩展到**线性代数**（行列式、逆矩阵、特征值、秩、方程组、矩阵乘法）与**常微分方程**（一阶/二阶、初值问题） |
| 目标课程 | 线性代数与微分方程（**非微积分极限**，满足 Level 3 要求） |
| 验证 | 9 道真实题型，独立代入核验 9/9 通过，自动求解率 **100%** |
| 交付形态 | 可运行源码包 + 排版规范的 `.tex` + 无需 TeX 的 `.pdf` |

## 2. 整体架构（五阶段流水线 + 两个增强）

在 starter kit 的 5 阶段骨架上做增量改造，不推翻、可对照：

```
输入 (md/pdf/docx/图片)
   │  Stage 1  ingest        文档摄入（扩展了 PDF/Word）
   ▼
   │  Stage 2  parse+classify 题目解析（多领域 T-box 分类）
   ▼
   │  Stage 3  solve         求解（SymPy 确定性 + 国产 LLM 推理回退）
   ▼
   │  Stage 4  render_latex  LaTeX 排版（ctex 中文 + 矩阵答案）
   ▼
   │  Stage 5  render_pdf     PDF 生成（matplotlib，无需 TeX）
   ▼
   │  Stage 5b verify        独立核验（代入检验 / 独立重算）
```

**两个关键增强（相对 starter kit）：**

1. **`llm_engine.py`（迁移核心）**——统一 `complete()` 接口，支持 Qwen（DashScope）、Kimi（Moonshot）、DeepSeek 的 OpenAI 兼容端点，仅用标准库 `urllib`，无需 `pip install openai`。没有 API key 时自动落到 `OfflineReasoner`（SymPy + 已核验的教材定理模板），保证流水线**离线可跑、可核验**。

2. **`render_pdf.py`（TeX-free 排版）**——starter kit 的 PDF 编译依赖本机 TeX Live，很多机器没有。改用 matplotlib 直接生成 PDF（中文字体 + mathtext 数学 + 矩阵表格绘制），**零 LaTeX 依赖**；同时仍输出 `homework.tex` 供 Overleaf 做专业排版。

## 3. 国产大模型选型

| 模型 | 数学推理 | 中文 | API | 结论 |
|---|---|---|---|---|
| **Qwen 3.6（通义千问）** | 强（尤其数学/物理） | 极好 | DashScope OpenAI 兼容 | ✅ **首选** |
| Kimi 2.5（Moonshot） | 长上下文、代码强 | 好 | Moonshot OpenAI 兼容 | 备选 |
| DeepSeek | 代码+数学强 | 好 | DeepSeek OpenAI 兼容 | 备选 |

**选择 Qwen 的理由**：本任务以**数学求解为主**，Qwen 的数学推理与中文符号表达最契合；其 DashScope 提供与 OpenAI 完全兼容的 `chat/completions` 端点，迁移成本最低。代码里三者都已实现，切换只需改一个环境变量：

```bash
# Qwen
export LLM_PROVIDER=qwen  DASHSCOPE_API_KEY=sk-...
# Kimi
export LLM_PROVIDER=kimi  MOONSHOT_API_KEY=sk-...
```

> 诚实说明：本次开发环境无可用 API key，实际运行走 `offline` 确定性回退（SymPy 精确计算 + 教材定理模板）。LLM 引擎是**真代码、真端点**，接入 key 即生效；离线回退则是「可运行、可核验」的工程保障。

## 4. 目标课程与求解策略

**目标课程：线性代数与微分方程**（避开微积分极限，直击 starter kit 的 40% 域外短板）。

**求解策略——「确定性优先 + 推理兜底」分层路由：**

| 题型 | 引擎 | 为什么 |
|---|---|---|
| 行列式 / 逆矩阵 / 秩 / 方程组 / 矩阵乘法 | SymPy 确定性 | 精确、免费、可复现 |
| 特征值 / 特征向量 | SymPy `eigenvects` | 精确，含重数 |
| 一阶/二阶 ODE + 初值 | SymPy `dsolve` | 精确通解/特解 |
| 证明题 / 概念题 | 国产 LLM（离线用定理模板） | 需要多步推理，SymPy 不擅长 |

**核心创新点**：不是「所有题都交给 LLM」或「全交给 SymPy」，而是**按题型自动路由**——计算题走 SymPy（确定性、零幻觉），推理题走 LLM（补齐推理短板），两者互补。

## 5. 关键设计决策与取舍

1. **多领域 T-box**：把 starter kit 的 `calculus_limits.yaml` 扩展为「多领域知识库」（新增 `linear_algebra.yaml`、`differential_equations.yaml`），分类器合并加载所有 YAML。遵循 SKILL.md 的哲学——「解题率 = 领域覆盖率，扩展领域知识而非写更多正则」。

2. **结构化矩阵答案**：求解结果新增 `answer_type` / `answer_matrix` / `answer_plain` 字段，让 LaTeX 渲染器用 `\begin{bmatrix}`、PDF 渲染器用表格，各取所需，互不妥协。

3. **ODE 解析的隐式乘法**：`y''-3y'+2y=0` 里的 `3y'`、`2y` 是隐式乘法，普通 `sympify` 会报 SyntaxError，改用 `parse_expr + implicit_multiplication_application` 转换。

4. **Windows GBK 兼容**：starter kit 在 Windows 终端打印 emoji 会崩（GBK 编码），给脚本加 `sys.stdout.reconfigure(utf-8)` 兜底。

## 6. 里程碑

| 阶段 | 产出 |
|---|---|
| Day 1–2 理解基线 | 读通 starter kit 5 阶段 + 本体架构，跑通 17/18 基线 |
| Day 2–6 迁移+扩展 | `llm_engine.py` + 矩阵/ODE 求解器 + 多领域 YAML + PDF/Word 摄入 |
| Day 6–7 验证 | 9 题线性代数+ODE 测试，100% 求解，独立核验 9/9 通过 |
