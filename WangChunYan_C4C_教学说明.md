# Wang ChunYan · C4C 教学说明（安装 / 使用 / 扩展）

> 技能包目录：`WangChunYan_C4C_homework-solver/`
> 目标读者：想复现、想换一门课、想扩展新学科的任何人。

---

## 1. 环境要求

- Python 3.10+（本机 3.13 验证通过）
- 必需：`sympy`、`pyyaml`、`matplotlib`
- 可选：`python-docx`（Word 摄入）、`pypdf`/`pdfplumber`（PDF 摄入）

```bash
pip install sympy pyyaml matplotlib
# 可选
pip install python-docx pypdf
```

## 2. 一条命令跑通

```bash
cd WangChunYan_C4C_homework-solver
python scripts/pipeline.py examples/linear_algebra_homework.md output/ \
    --course "线性代数与微分方程" \
    --student "Wang ChunYan" \
    --title "线性代数与微分方程 作业解答" \
    --pdf
```

产出（`output/`）：

| 文件 | 说明 |
|---|---|
| `1_ingested.json` | Stage 1 摄入结果 |
| `2_parsed.json` | Stage 2 解析与分类 |
| `3_solutions.json` | Stage 3 求解结果（含步骤与答案） |
| `homework.tex` | Stage 4 LaTeX 排版（中文自动用 ctexart） |
| `homework.pdf` | Stage 5 PDF（matplotlib，**无需 TeX**） |
| `verification.json` | Stage 5b 独立核验 |

## 3. 分步运行（理解每个 Stage）

```bash
python scripts/ingest.py        作业.md output/1_ingested.json
python scripts/parse_problems.py output/1_ingested.json output/2_parsed.json
python scripts/solve.py          output/2_parsed.json output/3_solutions.json
python scripts/render_latex.py   output/3_solutions.json output/homework.tex
python scripts/render_pdf.py     output/3_solutions.json output/homework.pdf \
    --course "课程" --student "姓名" --title "标题"
python scripts/verify.py         output/2_parsed.json output/3_solutions.json output/verification.json
```

## 4. 支持哪些课程

| 领域 | 已支持题型 |
|---|---|
| 线性代数 | 行列式、逆矩阵、秩、特征值/特征向量、矩阵乘法、转置、线性方程组 |
| 常微分方程 | 一阶线性、二阶常系数齐次、初值问题 |
| 微积分（继承自 starter kit） | 极限、切线、ε-δ、求导/积分、方程求解、概念题 |

## 5. 输入格式约定

- **题号**：`Problem 1` / `题 1` / `1.` / `1)` / `Q1` / `Exercise 1`
- **矩阵**：`\begin{pmatrix} ... \end{pmatrix}`（也支持 bmatrix/vmatrix）
- **ODE**：`y' + y = e^{x}` 或 `y'' - 3y' + 2y = 0`，初值写成 `y(0)=1`
- **文件**：`.md` / `.txt`（直接读）、`.docx`（python-docx）、`.pdf`（pypdf/pdfplumber/兜底）、图片（OCR，可选）

## 6. 启用国产大模型（迁移关键）

```bash
# 通义千问 Qwen
python scripts/pipeline.py 作业.md out/ --pdf --provider qwen --api-key sk-xxxx --model qwen-plus

# 或环境变量方式
export LLM_PROVIDER=qwen DASHSCOPE_API_KEY=sk-xxxx
python scripts/pipeline.py 作业.md out/ --pdf
```

未提供 key 时自动走**离线确定性回退**（SymPy + 定理模板），保证任何环境都能跑。

## 6.5 运行 L4 Path C 能力演示（SymPy-only vs LLM-Augmented）

```bash
# 离线定理模板路径
python scripts/demo_l4_path_c.py --json ../output/l4_path_c_demo.json

# 真国产大模型路径
python scripts/demo_l4_path_c.py --provider qwen --api-key sk-xxxx
```

预期输出：`SymPy-only 0/9 = 0%` → `LLM-Augmented 9/9 = 100%`，
并列出 9 道证明/结构题各自命中的模板（`det_inverse_proof`、`rank_nullity_theorem` 等）。

**新增非计算题模板的位置与约定**：`solver_templates/template_solvers/*.py`，
每个文件暴露一个 `TEMPLATE` dict：

```python
TEMPLATE = {
    "id": "your_template_id",
    "name": "模板名",
    "concept": "对应 T-box 概念 id",
    "tool": "template",
    "source": "oracles/0X_*.md#锚点",   # 知识来源（可追溯）
    "match_any": ["关键词1", "关键词2"],  # 命中任一即加分
    "match_none": ["否决词"],            # 出现即整条模板失效（防跨域误命中）
    "steps": ["步骤1（LaTeX）", "步骤2"],
    "answer_latex": "答案 LaTeX",
}
```

模板由 `llm_engine.load_template_files()` **自动发现并加载**，`OfflineReasoner`
按「关键词打分 + 否决词」匹配——改完文件即可生效，无需注册。

## 7. 如何扩展到一门新学科

遵循「扩展领域知识，而非写正则」：

1. **新建领域 YAML**：`domain_skills/你的学科.yaml`，定义 concept / solution_method / classification_rules（照抄 `linear_algebra.yaml` 的模板）。
2. **实现求解器**：在 `scripts/solve.py` 增加 `solve_xxx()`，并在 `SOLVERS` 字典注册路由类型。
3. **（可选）LLM 求解器**：对 SymPy 处理不了的证明/概念题，在 `_llm_solve()` 里路由到国产模型。
4. **分类映射**：在 `scripts/classify.py` 的 `SOLVER_TYPE_MAP` / `CONCEPT_TYPE_MAP` 补一条映射。

示例（新增「概率统计」）：

```yaml
# domain_skills/probability.yaml
- id: normal_distribution
  type: concept
  name: "正态分布"
  ...
classification_rules:
  - priority: 90
    pattern: {text_contains: ["正态分布", "normal distribution", "z-score"]}
    maps_to: normal_distribution
    solver: normal_distribution_solver
```

## 8. 常见问题

| 问题 | 解决 |
|---|---|
| 中文显示为方块 | 确认已装中文字体（Windows 自带微软雅黑/黑体） |
| PDF 里数学不如 LaTeX 精致 | 上传 `homework.tex` 到 overleaf.com，用 XeLaTeX 编译 |
| 想用真 LaTeX 编译 | 装 MiKTeX/TeX Live 后加 `--compile` |
| 矩阵答案在 PDF 里显示 | 矩阵以表格 + 方括号绘制，`answer_matrix` 字段承载 |
