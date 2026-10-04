# Wang ChunYan · C4C AI 使用日志（开发全过程）

> 说明：本挑战要求「AI-First 原则」——用 AI 解题、用 AI 排版、开发过程 AI 驱动。
> 本日志记录我（以 DeepSeek 驱动的编码 Agent）从理解基线到交付的完整迭代过程，
> 含每一轮的实际做法、prompt 要点、踩坑与修正。所有中间结果可复核。

---

## 环境与角色

- **开发 AI**：DeepSeek（deepseek-v4-pro）编码 Agent，运行于 DSH Harness。
- **被迁移目标**：Qwen 3.6 / Kimi 2.5 / DeepSeek（代码已实现，本机无 key 时走 offline 确定性回退）。
- **工作流**：单 Agent 多轮迭代（每轮「读代码 → 改代码 → 跑测试 → 读报错 → 修正」），不 fan-out、不并行子代理——因为各模块强依赖、需要即时反馈。

---

## Round 0 — 理解 Claude 基线（约 30 min）

**做了什么**：通读 `SKILL.md`、`README.md`、`pipeline.py`、`ingest.py`、`parse_problems.py`、`classify.py`、`retrieve.py`、`solve.py`、`render_latex.py`、`bootstrap.py`、`domain_skills/calculus_limits.yaml`。

**关键认知**：
1. 这是「本体驱动的求解器」——领域知识（YAML）+ 分类器 + 检索器 + 求解器分层，**解题率 = 领域覆盖率**。
2. `solve_matrix` / `solve_ode` / `solve_proof` 三个函数是**空壳**（直接返回「学生扩展点」），这正是我要填的坑。
3. 分类器 `classify.py` 只加载 `calculus_limits.yaml`，矩阵/ODE 题会被归到「conceptual」→ 不会路由到正确求解器。

**复跑基线**：本机实测 starter kit 在 Worksheet 3+4 上得 **17/18 = 94.4%**，与文档一致——基线可信。

---

## Round 1 — 迁移引擎设计（llm_engine.py）

**prompt 要点**（自我拆解）："把流水线的 LLM 依赖从 Claude 解耦，做成 OpenAI 兼容的国产模型客户端，仅用标准库；无 key 时必须能离线跑"。

**实现**：
- `LLMEngine`：`qwen`（DashScope）、`kimi`（Moonshot）、`deepseek` 三个 provider，`urllib` 直连 `chat/completions`，无需 `openai` 库。
- `OfflineReasoner`：离线证明模板（行列式逆、det 乘法、特征向量线性无关、秩-零化度定理）。
- `get_engine()`：无 key 返回 None，由调用方回退。

**决策**：离线回退不是「偷懒」，而是**「可运行、可核验」的工程保障**——评审时不能因为没 key 就跑不起来。

---

## Round 2 — 多领域 T-box + 分类器改造（classify.py + 两个新 YAML）

**做了什么**：
- 新建 `linear_algebra.yaml`、`differential_equations.yaml`（concept / solution_method / classification_rules）。
- `classify.py`：`__init__` 改为**合并加载 `domain_skills/*.yaml`**；新增 `has_matrix_expression` / `has_ode_expression` 特征与条件；`SOLVER_TYPE_MAP` / `CONCEPT_TYPE_MAP` 补 matrix/ode 映射。

**踩坑**：合并多个 YAML 时规则按 priority 全局排序，要保证「特征值/行列式/逆矩阵」等专用规则优先于通用规则，否则会被 `has_matrix_expression:true`（priority 70）抢先。

---

## Round 3 — 矩阵求解器（solve_matrix）

**实现**：`parse_matrix_latex` + `extract_matrices`（支持一个公式含多个矩阵）+ 六类运算（det / inv / linsolve / eigen / rank / matmul / transpose）。

**踩坑（重要）**：第 3 题「解方程组」和第 5 题「矩阵乘法」的题干里 **A、b 两个矩阵写在同一个 `$$...$$` 里**，`re.search` 只取第一个矩阵。修正为 `re.finditer` 取全部。

**踩坑**：第 9 题证明题含 `det(`/`逆` 关键词，被分类器误判为 matrix 类型。修正：`solve_matrix` 在「无矩阵 + 含证明关键词」时**转交 `solve_proof`**。

---

## Round 4 — ODE 求解器（solve_ode）——本轮 bug 最多

**第一版**：`ode_to_eq` 用 `sympy.sympify` 解析。
- ❌ Bug 1：初值条件 `y(0)=1` 与 ODE 在同一行，被当成方程一部分 → TokenError。
  → 修：先按 `,`/`\qquad`/`\quad` 切分，只取 ODE 主体。
- ❌ Bug 2：`y'' - 3y' + 2y = 0` 中 `2y`（隐式乘法）没被 `\by\b` 替换 → SyntaxError。
  → 修：`\by\b` 改为负向断言 `(?<![A-Za-z_])y(?![A-Za-z_'])`。
- ❌ Bug 3：`3Y1`、`2Y0` 仍是隐式乘法，`sympify` 不认。
  → 修：改用 `parse_expr(..., transformations=TRANSFORMATIONS)`（含 `implicit_multiplication_application`）。

**最终**：第 7 题 $y' + y = e^x,\ y(0)=1$ → $y=\cosh x$；第 8 题 $y''-3y'+2y=0,\ y(0)=1,\ y'(0)=0$ → $y=(2-e^x)e^x$，与手算一致。

---

## Round 5 — PDF 渲染器（render_pdf.py）+ LaTeX 中文（render_latex.py）

**决策**：starter kit 的 PDF 依赖 TeX Live，本机无。改用 **matplotlib 直接出 PDF**（中文字体 + mathtext 数学 + 矩阵表格绘制），零 LaTeX 依赖；同时 `homework.tex` 自动用 `ctexart` 支持中文。

**踩坑**：
- `\boxed{\begin{bmatrix}...\end{bmatrix}}` 在 LaTeX 里与矩阵环境可能冲突 → 矩阵答案走 `answer_type=="matrix"` 分支，单独 display 不 boxed。
- `_build_preamble` 的字符串拼接用了「变量 + 字符串字面量」隐式拼接 → SyntaxError → 改为显式 `+`。

---

## Round 6 — 独立核验（verify.py）

**思路**：核验不能「自说自话」，要**从题目原文独立重算 + 代入检验**（$A\cdot A^{-1}=I$、$Ax=b$、$Av=\lambda v$、ODE 残差=0、初值匹配）。

**踩坑**：verify.py 里 `Y(x)` 引用了不存在的 `x`（import 时改名成了 `X_SYM`）→ `name 'x' is not defined` → 统一用 `X_SYM`。

**结果**：9/9 通过。

---

## Round 7 — 健壮性与打包

- Windows GBK 终端打印 emoji 崩溃 → 各脚本加 `sys.stdout.reconfigure(utf-8, errors="replace")`。
- `pipeline.py` 增加 `--pdf` / `--provider` / `--model` / `--api-key` / `--no-verify`。
- `ingest.py` 补 PDF（pypdf→pdfplumber→stdlib 兜底）与 Word 摄入。

---

## Round 8 — 应对第三方静态核对检查单（补正轮）

**触发**：拿到一份第三方静态核对检查单（`WangChunYan_C4C_交付物完整性检查单.md`），
判定 L1 ⚠ 部分、L2 ✓ 达标、**L3 ⚠ 部分（4/7）**、**L4 未申报**，并列出 3 项会实际扣分的问题。

**逐条补正**：

| 检查单问题 | 补正动作 | 新增产物 |
|---|---|---|
| L3#1「新增知识源不成立」（oracles 五份与 starter 逐字节相同） | 新写 **4 份**线代/ODE 知识源（教材笔记 / 学习指南 / 教师指南 / ODE 知识源） | `oracles/06–09*.md` |
| L3#2「逐源抽取记录缺失」 | 在 `拿来说明.md` 新增 §5「知识源抽取记录」：**来源 → 抽取物 → 落到哪个字段** 三列表 + 链路示意图 | `拿来说明.md` §5 |
| L3#4「`solver_templates/` 零新增」 | 新写 **9 个**非计算题模板，并接入 `OfflineReasoner` **动态加载**（真被调用） | `solver_templates/template_solvers/*.py` |
| L4「未申报」 | 正式申报 **Path C**，并补 demo + 演示稿 | `L4创新声明.md`、`L4演示稿.md`、`demo_l4_path_c.py` |
| L1「单题逐步 trace 无独立文档」 | 写独立追踪文档（含 P8/P3 两题全链路真实分阶段数据） | `架构理解与解题追踪.md` |
| `__pycache__` 9 个 .pyc 打进包 | 删除两处 `__pycache__` | — |

**本轮踩坑（由 DEMO 抓出的真 Bug）**：

1. ❌ 三个新模板文件**语法错误**导致静默加载失败（只加载到 6/9）：
   - `linear_system_structure.py`：raw 字符串里嵌了 ASCII 双引号 `"无解"` → 字符串提前闭合；
   - `ode_solution_structure.py` / `trace_det_eigen_check.py`：`solve()` 多了一个 `}`。
   → 修：中文引号改全角 `“”`；删多余花括号。**教训：动态加载用 try/except 静默吞异常，
   必须配一个"加载数量自检"**，否则 6/9 也能"跑通"。

2. ❌ **模板跨域误命中**（demo 第一次跑就暴露）：
   - D5「判断是否可逆的充要条件」→ 误命中 `det_inverse_proof`（内置模板关键词只有单个"逆"字）；
   - D8「微分方程解的结构」→ 误命中 `linear_system_structure`（"解的结构"跨域同形）。
   → 修：匹配器从"按文件顺序取首个命中"改为**关键词打分 + `match_none` 否决词**，
   并移除宽泛的内置模板。修后 9/9 全部命中正确模板。

**本轮的关键认知**：把 demo 写成**带断言的对比测试**（0/9 vs 9/9），而不是截图——
它一次性抓出了"模板静默加载失败"和"跨域误命中"两类在正常流水线上**看不出来**的问题。

---

## 迭代统计与反思

| 维度 | 记录 |
|---|---|
| 迭代轮次 | 9 轮（Round 0–8） |
| 关键 prompt 优化 | 「迁移引擎解耦」「矩阵多实例解析」「ODE 隐式乘法」「核验不自证」「模板打分+否决词」 |
| 失败次数 | 11 次（ODE×3、矩阵多实例×1、GBK×1、verify 命名×1、LaTeX 拼接×1、模板语法×3、模板误命中×1） |
| 失败价值 | 每一次失败都定位到一个**通用工程边界**（隐式乘法、多矩阵、编码、命名空间、静默异常、跨域同形），修正后成为鲁棒性卖点 |

**工作流设计**：采用「确定性优先 + 推理兜底」的分层路由，而非一刀切把题全丢给 LLM；采用「独立重算 + 代入检验」的核验，而非让求解器自证——这两点直接决定了求解质量与可信度。

**如果重做**：我会先写 `verify.py`（测试驱动）再写求解器，把「代入检验」作为验收门禁；ODE 解析一开始就统一走 `parse_expr + implicit_multiplication_application`，省掉 3 次往返；模板加载器一开始就配"数量自检"，并把 demo 写成断言测试而非截图——本轮两类隐蔽 bug（静默加载失败、跨域误命中）都能提前抓出。
