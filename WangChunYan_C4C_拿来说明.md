# Wang ChunYan · C4C 拿来说明（从 starter kit 拿了什么 / 改了什么 / 知识源抽取记录）

> 原则：**拿来主义**——从 starter kit 出发，理解它怎么做的，再迁移改造；
> 清楚交代「拿了什么、改了什么、Claude 版与国产模型版有何差异、每个知识源抽取出什么」。

---

## 1. 从 starter kit 拿了什么（原样保留）

| 模块 | 拿了什么 | 用途 |
|---|---|---|
| `scripts/ingest.py` | Markdown 读取 + 分段逻辑 | Stage 1 基座 |
| `scripts/parse_problems.py` | 题号识别、子题识别、公式提取、关键词分类 | Stage 2 基座 |
| `scripts/solve.py` | `safe_parse`（LaTeX→SymPy）、极限/切线/ε-δ/方程/概念全套求解器、`_make_solution` 等辅助 | Stage 3 基座（极限域完整保留） |
| `scripts/classify.py` / `retrieve.py` | T-box 分类/检索骨架 | 多领域分类基座 |
| `scripts/render_latex.py` | LaTeX 模板、`clean_for_latex` 转义、编译逻辑 | Stage 4 基座 |
| `scripts/bootstrap.py` | 依赖自动安装 + `SKILL_ROOT` 解析 | 工程脚手架 |
| `domain_skills/calculus_limits.yaml` | 极限域完整本体 | 保留作为多领域之一 |
| `oracles/01–05` | 极限域的 5 份知识源 | **继承**（见 §5 抽取记录） |
| `references/`、`examples/`、`test_cases/` | 模板、示例、基线测试 | 参照与测试 |

## 2. 用了哪些外部库

| 库 | 拿来做什么 | 来源 |
|---|---|---|
| SymPy | 符号计算引擎（行列式/逆/特征值/秩/方程组/ODE/极限） | 开源，官方文档 |
| PyYAML | 领域知识 T-box 解析 | 开源 |
| matplotlib | **新增**：TeX-free PDF 生成 | 开源 |
| python-docx | **新增**：Word 摄入 | 开源 |
| pypdf / pdfplumber | **新增**（可选）：PDF 摄入 | 开源 |

## 3. 我改了 / 新增了什么

| 文件 | 改动 | 性质 |
|---|---|---|
| `scripts/llm_engine.py` | **新增**：Qwen/Kimi/DeepSeek 客户端 + 模板动态加载 + 领域知识上下文提示 | 迁移核心 |
| `scripts/solve.py` | 矩阵/ODE/证明求解器（原为三个空壳）+ 向量点积/叉积 + 结构化答案字段 + LLM 路由 | 扩展核心 |
| `scripts/classify.py` | 合并加载多领域 YAML + matrix/ode 特征 | 扩展 |
| `domain_skills/linear_algebra.yaml` | **新增** | 扩展 |
| `domain_skills/differential_equations.yaml` | **新增** | 扩展 |
| `oracles/06–09` | **新增 4 份知识源**（线性代数教材笔记 / 学习指南 / 教师指南 / ODE 知识源） | L3 知识增强 |
| `solver_templates/template_solvers/*.py` | **新增 9 个非计算题模板**（det 逆/乘法证明、特征向量无关、秩-零化度、可逆判据、解结构、ODE 存在唯一/解结构、迹-行列式对账） | L3 模板 |
| `scripts/render_pdf.py` | **新增**：matplotlib PDF（无需 TeX） | 扩展 |
| `scripts/verify.py` | **新增**：独立重算 + 代入核验 | 扩展 |
| `scripts/ingest.py` | 补 PDF / Word 摄入 | 扩展 |
| `scripts/render_latex.py` | ctex 中文 + 矩阵答案处理 | 增强 |
| `scripts/pipeline.py` | `--pdf`/`--provider`/核验集成 + GBK 兜底 | 增强 |

## 4. Claude 版本 vs 国产模型版本 —— 差异

| 维度 | Claude 版（starter kit） | 国产模型版（本次） |
|---|---|---|
| LLM 依赖 | 绑定 Claude Code（无代码抽象） | 可插拔 `LLMEngine`（Qwen/Kimi/DeepSeek） |
| 提示词 | 无（由 Claude Code 隐式处理） | **结构化提示**：注入 T-box 领域知识作上下文 |
| 无 key 时 | 证明/概念题直接「未求解」 | 9 个离线定理模板兜底，仍可出答案 |
| 领域 | 仅微积分极限 | 极限 + 线性代数 + 微分方程 |
| 矩阵/ODE/证明求解器 | 三个空壳（学生扩展点） | 完整实现 |
| 非计算题模板 | `solver_templates/` 3 个（均为极限域） | **+9 个**（线代/ODE 域） |
| 知识源 | 5 份（极限域） | **+4 份**（线代/ODE 域） |
| PDF 输出 | 依赖本机 TeX Live | matplotlib 直接出 PDF，零 TeX 依赖 |
| 核验 | 无 | `verify.py` 独立代入核验 |
| 输入格式 | 仅 Markdown | Markdown + Word + PDF（OCR 可选） |
| 中文 LaTeX | 需手动 xelatex + CJK 字体 | 自动 `ctexart` |

---

## 5. 知识源抽取记录（来源 → 抽取物 → 落到哪里）

> 对应 CHALLENGE.md L3 的「For each source, document what was extracted:
> New concepts? New classification rules? New templates? Common errors?」

### 5.1 本次**新增**的知识源（4 份，满足 L3「≥2 additional beyond textbook + exemplars」）

| # | 来源文件 | 来源类型 | 抽取出什么 | 落到哪个字段 / 文件 |
|---|---|---|---|---|
| 06 | `oracles/06_linear_algebra_textbook_notes.md` | **textbook notes**（Lay Ch.1–5 + 同济第 1–5 章） | 6 个核心概念及形式化定义：矩阵运算、行列式、逆矩阵、线性方程组、特征值、秩；定理：$\det(AB)=\det A\det B$、$\det(A^{-1})=1/\det A$、2×2 逆公式、迹/行列式桥 | `domain_skills/linear_algebra.yaml` → `concepts[].id/.name/.formal/.keywords`（6 节点）、`solution_methods[].applies_when` |
| 07 | `oracles/07_linear_algebra_study_guide.md` | **study guide**（易错点/误解/学习顺序） | **10 条常见误解**（$\det(A+B)$、$AB\neq BA$、$\det=0$ 不可逆、$\operatorname{rank}(A+B)$、零特征向量、特征向量唯一、复特征值、$Ax=b$ 判据、$(AB)^T$ 反序、秩的定义）；**6 条自查清单**（形状/可逆性/代入/不变量/边界/表述） | ①**新分类规则 7 条** → `linear_algebra.yaml` → `classification_rules[]`；②**校验规则** → `validation_rules{}`；③自查清单 → `scripts/verify.py` 的核验分支 |
| 08 | `oracles/08_linear_algebra_instructor_guide.md` | **instructor guide**（证明范式/评分 rubric/考试陷阱） | **4 个证明范式**（A 两侧同施运算 / B 线性组合零化 / C 反例法 / D 维数夹逼）；**评分 rubric**（前提检查占 20%）；**5 类考试陷阱**；**可接受等价答案表** | ①**7 个新模板** → `solver_templates/template_solvers/{det_inverse_proof, det_product_proof, eigen_independence_proof, rank_nullity_theorem, matrix_invertibility_criteria, linear_system_structure, trace_det_eigen_check}.py`；②「前提检查」要求 → 模板 steps 首句强制写 Given；③等价答案表 → `verify.py` 用**代数化简**而非字符串比对 |
| 09 | `oracles/09_ode_knowledge_source.md` | **textbook notes + study guide + worked example set**（同济·微分方程 + Boyce） | 一阶线性积分因子三步法；二阶特征方程**三情形通解**；初值定常数流程；**4 类解析陷阱**（隐式乘法/上标/同行初值/行分隔符）；**残差+初值双重检验** | ①概念 → `differential_equations.yaml` → `concepts[first_order_ode / second_order_ode / ode_ivp].formal`；②**新分类规则 3 条** → `classification_rules[]`；③陷阱 → `scripts/solve.py::ode_to_eq / extract_ics` 的实现理由；④双重检验 → `validation_rules[ode]` + `verify.py` ODE 分支；⑤**2 个新模板** → `template_solvers/{ode_existence_uniqueness, ode_solution_structure}.py` |

**新增模板合计 9 个**（L3 要求 ≥5）：7 个线性代数 + 2 个 ODE。
**新增分类规则合计 10 条**（L3 要求 ≥3）：线性代数 7 条 + ODE 3 条。
**新增知识源合计 4 份**（L3 要求 ≥2，且均为 textbook/exemplars 之外的 study guide / instructor guide / 章节笔记类型）。

### 5.2 **继承**的 starter kit 知识源（5 份，非本次新增，用途如实标注）

| # | 来源文件 | 来源类型 | 抽取出什么 | 落到的字段 / 文件 |
|---|---|---|---|---|
| 01 | `oracles/01_textbook_stewart.md` | textbook（Stewart Ch.2） | 极限定义、单侧极限、极限存在判据、夹逼定理、连续性 | `calculus_limits.yaml` → `concepts[limit_definition / one_sided_limit / limit_existence / squeeze_theorem / continuity]` |
| 02 | `oracles/02_study_guide.md` | study guide | GCSC 四关键词证明法、连续性三条件、L'Hôpital 前提、Newton 法、隐函数求导 | `calculus_limits.yaml` → `concepts[epsilon_delta_proof_method].oracle_insight`、`concepts[continuity]`；`solve.py::_match_conceptual_template` |
| 03 | `oracles/03_instructor_guide.md` | instructor guide | 间断点四类型、IVT 与不动点、增长层级 $\ln x \ll x^p \ll e^x$、代数工具箱 | `calculus_limits.yaml` → `concepts[discontinuity_types / intermediate_value_theorem / growth_hierarchy / limit_algebraic_strategies]` |
| 04 | `oracles/04_pedagogy_guide.md` | pedagogy guide | 博弈隐喻、$\delta=\min(1,\varepsilon/C)$ 记法、4 条常见错误、评分 40/60 | `calculus_limits.yaml` → `concepts[epsilon_delta_nonlinear].strategy_variants / .common_errors` |
| 05 | `oracles/05_exemplars.md` | exemplars（Berkeley Math 1A W3–4） | 真实题面与题型范例 | `calculus_limits.yaml` → `classification_rules[].pattern.text_contains`；`test_cases/` |

### 5.3 其他参照（不计入知识源）

| 文件 | 抽取出什么 | 落到哪里 |
|---|---|---|
| `references/sympy_cheatsheet.md`（继承） | SymPy 常用函数签名 | `solve.py` 的实现选型（`linsolve` / `eigenvects` / `dsolve` / `rref`） |
| `references/homework_template.tex`（继承） | LaTeX 作业模板骨架 | `render_latex.py::_build_preamble`（扩展 ctex 分支） |

### 5.4 抽取链路示意

```
oracles/06,07,08  ──抽取──▶  linear_algebra.yaml
                              ├── concepts[6]            ← 06 教材笔记
                              ├── solution_methods[6]    ← 06 教材笔记
                              ├── classification_rules[7] ← 07 学习指南
                              └── validation_rules       ← 07 学习指南
                                    │
                                    ├──▶ solver_templates/template_solvers/*.py (7) ← 08 教师指南
                                    └──▶ scripts/verify.py 核验分支              ← 07 自查清单 + 08 rubric

oracles/09        ──抽取──▶  differential_equations.yaml
                              ├── concepts[3]            ← 09 教材笔记
                              ├── classification_rules[3] ← 09 学习指南
                              └── validation_rules[ode]  ← 09 双重检验
                                    ├──▶ solve.py::ode_to_eq / extract_ics ← 09 解析陷阱
                                    ├──▶ template_solvers/*.py (2)         ← 09 结构定理
                                    └──▶ scripts/verify.py ODE 分支        ← 09 残差+初值
```

---

## 6. 关键「拿来」的心得

1. **架构比代码值钱**：starter kit 最有价值的是「本体驱动 + 五阶段分层」的架构思想，而不是某段具体代码。迁移时保留架构，替换/补齐实现。
2. **领域知识即能力**：`calculus_limits.yaml` 证明「解题率 = 领域覆盖率」。我照它的格式写线性代数/ODE 的 YAML，就自然获得了这两个领域的分类与求解能力——**扩展知识，而非写更多正则**。
3. **知识源的"形状"决定抽取物**：教材笔记 → 概念与定理；学习指南 → 分类规则与校验规则；教师指南 → 模板与评分要求。同一个领域知识库，从不同来源抽取的东西是**互补**的。
4. **确定性优先**：SymPy 是「拿来」的确定性引擎，LaTeX 模板是「拿来」的排版方案；国产 LLM 只负责 SymPy 不擅长的推理/证明，取长补短，而不是让 LLM 干所有事。
