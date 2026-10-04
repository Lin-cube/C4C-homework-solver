# Wang ChunYan · C4C Level 1：架构理解与单题逐步追踪

> 对应 CHALLENGE.md Level 1 的四项任务：跑通基线 ✓、回答领域知识三问 ✓、
> **单题逐步 trace（本文档）**、架构总结（本文档 §1）。
> 所有 trace 数据取自本次真实运行产物 `output/1_ingested.json`、`2_parsed.json`、`3_solutions.json`。

---

## 1. 架构总结（我自己的话）

### 1.1 一句话
> **这条流水线的本质是「把题目翻译成领域知识里已有的概念，再让该概念绑定的求解器去执行」。**

代码本身很薄；真正的能力装在 `domain_skills/*.yaml` 里。所以扩展能力的方式不是写更多正则，
而是**往本体里加概念/方法/规则**——这正是 starter kit 反复强调的「Solve rate = domain coverage」。

### 1.2 分层结构

| 层 | 组件 | 职责 | 我的改动 |
|---|---|---|---|
| 摄入层 | `ingest.py` | 任意格式 → 带分段边界的纯文本 | 补 PDF/Word |
| 解析层 | `parse_problems.py` | 题号/子题/公式抽取 | 未改 |
| **本体层** | `domain_skills/*.yaml` | 概念图 + 解法表 + 分类规则 + 校验规则 | **新增线性代数/ODE 两域** |
| **定向层** | `classify.py` | 题目特征 → 概念/解法（优先级规则） | 改为**多域合并加载** |
| 检索层 | `retrieve.py` | 概念 → 求解模板 | 未改 |
| **执行层** | `solve.py` | 按类型路由到求解器执行 | **补齐矩阵/ODE/证明** |
| 推理层 | `llm_engine.py` | SymPy 搞不定的证明/概念题 | **新增（迁移核心）** |
| 排版层 | `render_latex.py` / `render_pdf.py` | 解答 → .tex / .pdf | 加 ctex、加 TeX-free PDF |
| 核验层 | `verify.py` | 独立重算 + 代入检验 | **新增** |

### 1.3 设计原则（为什么它能工作）
1. **知识与实例分离**：题目是实例，本体是知识。换一份作业不用改代码，只要能匹配到概念。
2. **优先级定向**：分类规则带 `priority`，越具体的规则越先匹配（特征值 > 行列式 > 通用矩阵）。
3. **确定性优先**：能算的用 SymPy 精确算，只有推理型题目才上 LLM——把幻觉风险压到最小。
4. **可核验闭环**：求解器输出必须能通过独立代入检验（`verify.py`），否则说明定向错了。

---

## 2. Level 1 三问

### Q1：领域知识如何组织？关键结构是什么？
`calculus_limits.yaml` / `linear_algebra.yaml` / `differential_equations.yaml` 各含四个顶层键：

| 键 | 作用 | 例（linear_algebra.yaml） |
|---|---|---|
| `concepts` | 概念节点（含 `formal` 形式化定义、`prerequisites` 前置、`keywords`） | `matrix_determinant`、`eigenvalue` |
| `solution_methods` | 解法节点（含 `concept` 归属、`applies_when` 适用条件、`tool`、`solver_template`） | `eigen_solver` → SymPy |
| `classification_rules` | **优先级排序**的特征→概念映射（`pattern` 条件 + `maps_to` + `solver`） | `text_contains: ["特征值"]` → `eigenvalue` |
| `validation_rules` | 答案形式/正确性校验规则 | `A·A⁻¹ = I` |

`oracle_sources` 记录知识从哪来（教材/指南），把「知识」和「知识来源」也分开。

### Q2：求解器如何决定用哪个方法？
三步链：`_extract_features` → 按 `priority` 降序遍历 `classification_rules` → 命中即返回 `(concept, solver)`，
`classify_to_legacy_type` 再把 solver 名映射成 `solve.py` 的 `SOLVERS` 键（如 `eigen_solver → "matrix"`）。

> **关键**：如果所有规则都不命中，默认落到 `conceptual`——这是「安全默认」，不会乱算，但会求解失败。
> 所以我扩展时必须**同时补规则和补 solver**，否则规则命中却无 solver 可跑。

### Q3：oracle 源起什么作用？
oracle 是**知识的出处与权威背书**。本体里的每条 `formal`、每条分类关键词、每条常见错误，
都能回溯到某个 oracle（教材章节 / 学习指南 / 教师指南 / 范例卷）。
它不参与运行，但决定了本体是否「有据可依」，也是 L3「知识增强」的评估对象。

---

## 3. 单题逐步追踪：第 8 题（二阶常系数 ODE + 初值）

选它的理由：它贯穿了**文本 → 公式 → 分类 → 解析 → 求解 → 排版 → 核验**的全链路，
且包含了 ODE 解析的全部陷阱（隐式乘法、上标、同行初值）。

### Stage 1 — 摄入（`ingest.py`）
输入 Markdown 中「第 8 题」所在小节被切为一个 section：
```
sections[8].title = "第 8 题　二阶常系数齐次微分方程（初值问题）"
```
**为什么**：`split_into_sections` 按 Markdown 标题（`##`）切段，每段自带边界——
这样 Stage 2 才能在段内定位题目，而不会跨题串行。

### Stage 2 — 解析 + 分类（`parse_problems.py` + `classify.py`）
产出（真实数据）：
```json
{
  "id": "8",
  "text": "二阶常系数齐次微分方程（初值问题）\n\n求解初值问题：\n\n$$\ny'' - 3y' + 2y = 0, \\qquad y(0) = 1, \\quad y'(0) = 0\n$$\n\n---",
  "math_expressions": [
    {"type": "display", "latex": "y'' - 3y' + 2y = 0, \\qquad y(0) = 1, \\quad y'(0) = 0"}
  ],
  "type": "ode",
  "sub_problems": []
}
```
**逐步为什么**：
1. `###` 标题（"第 8 题…"）先试 `detect_problem_start`，未命中题号模式 → 跳过该行；
2. 正文行 `8.` 不存在（本例题号由标题承载），实际由 `## 第 8 题` 段内首行内容进入 `current_lines`；
3. `$$...$$` 由 `extract_math_expressions` 以 DOTALL 正则整体抽取为 **1 条 display 公式**——
   注意初值 `y(0)=1` 与 ODE **在同一条公式里**，这是后面必须切分的原因；
4. `_classify` 走 T-box：`differential_equations.yaml` 的 priority 95 规则命中
   `text_contains: ["y''", "二阶"]` → `maps_to: second_order_ode`，`solver: ode_second_order_solver`；
5. `SOLVER_TYPE_MAP["ode_second_order_solver"] = "ode"` → 最终 `type = "ode"`。

> **若无这条规则**：会落到 priority 80 的 `has_ode_expression: true` 兜底，仍归 ode，但概念更泛；
> 若两条都没有 → 落到 `conceptual` → 求解失败。这印证了 Q2 的「安全默认」。

### Stage 3 — 求解（`solve.py::solve_ode`）
1. 在 `math_expressions` 中找到含 `y''` 的那条 → `ode_str = "y'' - 3y' + 2y = 0, \qquad y(0) = 1, \quad y'(0) = 0"`；
2. **切分初值**：`re.split(r",|\\qquad|\\quad")[0]` → `"y'' - 3y' + 2y = 0"`；
3. **`extract_ics`** 扫原文：`y(0)=1` → `{y(0): 1}`；`y'(0)=0` → `{Subs(Derivative(y(x),x),x,0): 0}`；
4. **`ode_to_eq`** 归一化：
   - `y'''→Y3`、`y''→Y2`、`y'→Y1`（**先长后短**，避免 `y''` 被 `y'` 抢先）；
   - 裸 `y`（含 `2y` 这种数字紧跟的）→ `Y0`（用负向断言而非 `\by\b`，因为 `2y` 里没有词边界）；
   - `Y0/Y1/Y2` 经 `parse_expr(local_dict=…)` 映射为 `y(x) / diff(y(x),x) / diff(y(x),x,2)`，
     并用 `implicit_multiplication_application` 处理 `3Y1`、`2Y0` 这类隐式乘法；
   - 等号两侧相减 → `Eq(…, 0)`；
5. **`dsolve(eq, y(x), ics=…)`** → 解；
6. 产出（真实数据）：
```json
"solver": "sympy_dsolve",
"steps": [
  "微分方程：$2 y(x) - 3 \\frac{d}{dx} y(x) + \\frac{d^{2}}{dx^{2}} y(x) = 0$",
  "初值条件：$\\left. \\frac{d}{dx} y(x) \\right|_{x=0} = 0$",
  "初值条件：$y(0) = 1$",
  "解：$y(x) = \\left(2 - e^{x}\\right) e^{x}$"
],
"answer_latex": "y(x) = \\left(2 - e^{x}\\right) e^{x}"
```
**为什么** `(2-e^x)e^x` 就等于手算的 `2e^x - e^{2x}`：展开即 `2e^x - e^{2x}`——**代数等价**，
所以核验不能做字符串比对（见 Stage 5b）。

### Stage 4 — 排版（`render_latex.py` / `render_pdf.py`）
- **LaTeX**：题目原文 + 4 条 steps + `\[\boxed{y(x) = \left(2 - e^{x}\right) e^{x}}\]`；
  文档类自动切到 `ctexart`（检测到中文）。
- **PDF**：`render_pdf.py` 把 steps 的 LaTeX 转可读文本，答案用 mathtext 渲染在圆角框里；
  一页装不下时自动换页（`_ensure_space`）。

### Stage 5b — 独立核验（`verify.py`）
```
✅ Problem 8: ODE 残差 = 0; 初值匹配
```
两步独立检验：
1. 把解代回方程左端 `2y - 3y' + y''`，`simplify()` 后**必须恒为 0**；
2. 代入初值：`y(0)=1` ✓、`y'(0)=0` ✓。

> 注意核验**不读求解器的答案字符串**，而是重新 `dsolve` 并用代数等价判定——
> 这才叫「不自证」。

---

## 4. 第二个追踪：第 3 题（线性方程组，多矩阵分支）

| Stage | 发生了什么 |
|---|---|
| 1 摄入 | `## 第 3 题　求解线性方程组` 独立成段 |
| 2 解析 | 两条 display 公式：第一条含 **A 与 b 两个矩阵**，第二条是 `\begin{cases}` 形式；分类命中 `linear_system_solver` → type `matrix` |
| 3 求解 | `extract_matrices` 用 **`finditer` 取全部矩阵**（不是 `search` 只取第一个）→ `A(3×3)`、`b(3×1)`；判定 `is_system and len(mats)>=2 and b.cols==1` → `linsolve((A,b), x,y,z)` → `(1,2,3)`；步骤里额外给出**增广矩阵行最简形** |
| 4 排版 | 答案 `x = 1, y = 2, z = 3` 走 mathtext 圆角框 |
| 5b 核验 | `A·x - b` 逐分量化简为 0 ✓ |

> **这里踩过的坑**：最初用 `re.search` 只解析出 A、丢了 b，导致被误判「形状不匹配」。
> 改用 `finditer` 后修复——这也是「一个公式可含多个矩阵」这一边界情况的处理。

---

## 5. 关键洞察

1. **solvable 与 unsolvable 的分界**：题目能被「特征提取 → 规则命中 → solver 存在」三步接住就可解；
   任一步断裂即不可解。starter kit 的 40% 域外求解率，就是因为**后两步在矩阵/ODE 上完全缺失**。
2. **补能力的位置**：补 `classification_rules`（定向）+ 补 `SOLVERS`（执行），两者必须成对。
3. **语料的"干净度"直接决定成败**：ODE 题里 `3y'`、`2y`、`e^{x}`、同行初值——每一个都曾让解析崩掉。
   工程上的解法不是"更聪明的正则"，而是**归一化 + 标准化解析器**（`parse_expr` 转换链）。
4. **核验要独立**：等价形式（`cosh x` vs `(e^x+e^-x)/2`）决定了核验必须做代数化简而非字符串比对。
