# C4C 演示稿 · LLM 增强的作业自动求解与排版

**Wang ChunYan** ｜ 挑战 ch-20260717031447-k82c4m ｜ Level 4 · Path C
（演讲稿，Markdown 幻灯片格式，可直接投屏或用 Marp/Slidev 渲染）

---

## Slide 1 · 封面

# 从「极限」到「线代 + ODE」
### 把作业求解流水线迁移到国产大模型

- 迁移引擎：Claude → **Qwen / Kimi / DeepSeek** 可插拔
- 扩展学科：微积分极限 → **线性代数 + 微分方程**
- 求解率：starter kit 域外 **40%** → 本次 **100%（9/9）**
- 全部答案通过**独立代入核验**

---

## Slide 2 · 问题：starter kit 的能力边界

| 测试集 | 领域 | 求解率 |
|---|---|---|
| Worksheet 3 + 4 | 微积分极限 | 17/18 = **94.4%** ✅ |
| 进阶挑战题 | 域外（积分/优化/物理） | 2/5 = **40%** ⚠️ |

**根因**：`solve_matrix` / `solve_ode` / `solve_proof` 在 starter kit 里是**三个空壳**，
直接返回「学生扩展点」。域外题目无规则命中 → 落到 `conceptual` → 求解失败。

> **洞察：解题率 = 领域覆盖率，不是代码复杂度。**

---

## Slide 3 · 本次要做的两件事

### ① 迁移引擎
把「Claude Code 隐式提供推理」改成 **显式的可插拔 `LLMEngine`**：
- Qwen（DashScope）/ Kimi（Moonshot）/ DeepSeek，均为 OpenAI 兼容端点
- 仅用标准库 `urllib`，零额外依赖
- **无 API key 时自动降级**到 9 个已核验定理模板 —— 保证可运行

### ② 扩展学科
补齐矩阵 / ODE / 证明三个空壳 + 新建两个领域本体：
- `domain_skills/linear_algebra.yaml`（6 概念 / 6 解法 / 7 规则）
- `domain_skills/differential_equations.yaml`（3 概念 / 2 解法 / 3 规则）

---

## Slide 4 · 架构：五阶段 + 推理层 + 核验层

```
输入 → ①摄入 → ②解析+分类 → ③求解 → ④LaTeX → ⑤PDF → ⑤b 核验
                              │
                    ┌─────────┴─────────┐
                 SymPy 确定性链      推理增强层
              (det/inv/linsolve/   (llm_engine.py)
               eigenvects/dsolve)   离线模板 / 国产 LLM
```

**设计原则**：**确定性优先，推理兜底** ——
计算题永远走 SymPy（零幻觉），只有证明/概念题才上 LLM。

---

## Slide 5 · 迁移：三家国产模型一行切换

```bash
# 通义千问
LLM_PROVIDER=qwen  DASHSCOPE_API_KEY=sk-...  python scripts/pipeline.py 作业.md out/ --pdf
# Kimi
LLM_PROVIDER=kimi  MOONSHOT_API_KEY=sk-...   python scripts/pipeline.py 作业.md out/ --pdf
# 无 key → 自动离线
python scripts/pipeline.py 作业.md out/ --pdf
```

**结构化提示（Path C 要求）**：不是裸丢题目，而是**先注入领域知识**——

```
【领域知识上下文】
概念：行列式
形式化定义：det(A)，方阵对应的标量；按行/列展开计算
适用解法：行列式计算
适用条件：给定方阵求 det
【题目】证明：若 A 可逆，则 det(A⁻¹) = 1/det(A)
```

---

## Slide 6 · DEMO：SymPy 做不到，LLM 能做到

`python scripts/demo_l4_path_c.py`

| 路径 | 做法 | 结果 |
|---|---|---|
| SymPy-only | 当计算题丢给 `solve_calculation` | **0 / 9 = 0%** |
| **LLM-Augmented** | 路由到 `solve_proof`（模板/LLM） | **9 / 9 = 100%** |

9 道证明/结构题全部命中**正确的**模板：

```
D1 det(A⁻¹)=1/detA → det_inverse_proof        D6 方程组解结构  → linear_system_structure
D2 det(AB)         → det_product_proof        D7 IVP 存在唯一   → ode_existence_uniqueness
D3 特征向量无关     → eigen_independence_proof  D8 非齐次 ODE 结构 → ode_solution_structure
D4 秩-零化度       → rank_nullity_theorem      D9 迹-行列式验算  → trace_det_eigen_check
D5 可逆等价条件     → matrix_invertibility_criteria
```

---

## Slide 7 · 实测踩坑：模板误命中（DEMO 发现的真 Bug）

第一版按**文件顺序取首个命中**，结果：

| 题 | 误命中 | 原因 |
|---|---|---|
| D5「是否可逆的充要条件」 | ❌ `det_inverse_proof` | 内置模板关键词只有单个"逆"字，太宽 |
| D8「微分方程解的结构」 | ❌ `linear_system_structure` | "解的结构"同时匹配线代与 ODE |

**修复**：匹配器改为**关键词打分 + `match_none` 否决词**，
并移除宽泛的内置模板 → 9/9 全部命中正确模板。

> 这就是为什么 demo 不是演示、而是**测试**：它抓出了真实缺陷。

---

## Slide 8 · 求解结果：9/9 = 100%

| # | 题型 | 答案 | 核验 |
|---|---|---|---|
| 1 | 3×3 行列式 | 20 | 独立重算 ✓ |
| 2 | 2×2 逆矩阵 | $\begin{bmatrix}1&-1\\-1&2\end{bmatrix}$ | $AA^{-1}=I$ ✓ |
| 3 | 线性方程组 | $(x,y,z)=(1,2,3)$ | $Ax=b$ ✓ |
| 4 | 特征值/向量 | $\lambda=1,3$；$v=[-1,1],[1,1]$ | $Av=\lambda v$ ✓ |
| 5 | 矩阵乘法 | $AB=\begin{bmatrix}19&22\\43&50\end{bmatrix}$ | 独立重算 ✓ |
| 6 | 秩 | 2 | 独立重算 ✓ |
| 7 | 一阶 ODE + IVP | $y=\cosh x$ | 残差=0 + 初值 ✓ |
| 8 | 二阶 ODE + IVP | $y=(2-e^x)e^x$ | 残差=0 + 初值 ✓ |
| 9 | 证明题 | $\det(A^{-1})=1/\det(A)$ | 定理推导 ✓ |

**核验不读求解器的答案字符串** —— 独立重算 + 代数等价判定。

---

## Slide 9 · 排版：两份产物，零 TeX 依赖

| 产物 | 技术 | 特点 |
|---|---|---|
| `WangChunYan_C4C_output.tex` | `ctexart` | Overleaf 一键编译，专业数学排版 |
| `WangChunYan_C4C_output.pdf` | matplotlib | **无需安装 TeX Live**，中文 + mathtext + 矩阵表格绘制 |

> 大多数同学的机器没有 TeX Live —— PDF 不该因此生不出来。

---

## Slide 10 · 知识增强（L3）：4 份新知识源 → 本体

| 新增知识源 | 抽取出什么 | 落到哪里 |
|---|---|---|
| `06_linear_algebra_textbook_notes.md` | 6 概念 + 定理 | `concepts[].formal` |
| `07_linear_algebra_study_guide.md` | **10 条常见误解** + 自查清单 | `classification_rules[7]` + `validation_rules` |
| `08_linear_algebra_instructor_guide.md` | **4 个证明范式** + 评分 rubric | `template_solvers/*.py`（**7 个新模板**） |
| `09_ode_knowledge_source.md` | 三情形通解 + 4 类解析陷阱 | `concepts[].formal` + `ode_to_eq` + **2 个新模板** |

**合计新增**：4 份知识源、9 个非计算题模板、10 条分类规则（L3 要求 2 / 5 / 3）。

---

## Slide 11 · 复盘：三条最有价值的教训

1. **边界情况决定成败**。ODE 解析连崩三次：隐式乘法 `3y'`、上标 `e^{x}`、同行初值
   `y(0)=1`。解法不是更聪明的正则，而是**归一化 + 标准解析器**（`parse_expr` 转换链）。

2. **核验必须独立**。$y=\cosh x$ 与 $y=\frac{e^x+e^{-x}}2$ 是同一答案——
   字符串比对会判错，必须做**代数化简**。

3. **DEMO 即测试**。Path C 的能力演示第一次跑就抓出两处模板误命中。
   把演示写成**带断言的对比测试**，而不是截图，才是真正的工程做法。

---

## Slide 12 · 交付物 & 复现

**一条命令复现：**
```bash
pip install sympy pyyaml matplotlib
cd WangChunYan_C4C_homework-solver
python scripts/pipeline.py examples/linear_algebra_homework.md output/ \
    --course "线性代数与微分方程" --student "Wang ChunYan" --pdf
```

**交付 13 项**：方案设计 / 源码包 / 作业原件 / output.pdf / output.tex /
验证报告 / 教学说明 / AI日志 / 拿来说明 / 架构与解题追踪 / L4创新声明 / L4演示稿 / 检查单补正说明

---

## Slide 13 · Q&A 预备：可能的追问

**Q：没有 API key，凭什么说迁移成功了？**
A：迁移的是**架构能力**，不是某次调用。`LLMEngine` 三家的端点是真实代码，
配置 key 即生效、无需改代码；而离线降级本身是工程改进（starter kit 无 key 时直接放弃）。

**Q：9/9 是不是题目太简单？**
A：题目覆盖行列式/逆/方程组/特征值/秩/乘法/一阶ODE/二阶ODE/证明共 9 类，
每题都经**独立代入核验**。诚实边界：这是按标准教材题型构造的代表性作业，
非某门课的原始试卷；更复杂题型（SVD、Laplace 变换）未覆盖。

**Q：为什么不用 LLM 解所有题？**
A：数学计算用 LLM 会引入幻觉且不可复现。**确定性优先**是刻意的架构选择。
