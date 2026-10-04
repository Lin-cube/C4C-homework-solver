"""
Solver Template: 特征值的迹-行列式对账（自检型模板）
T-box concept: eigenvalue
Tool: template (invariant check, 非计算题的"验算"型回答)

Oracle source: oracles/06_linear_algebra_textbook_notes.md §5.1（迹与行列式的桥）
               oracles/07_linear_algebra_study_guide.md §4 自查清单

用途：当题目问"验证你的特征值是否正确"或需要给出自检依据时使用。
"""

TEMPLATE = {
    "id": "trace_det_eigen_check",
    "name": "特征值的迹-行列式对账",
    "concept": "eigenvalue",
    "tool": "template",
    "source": "oracles/06_linear_algebra_textbook_notes.md#5.1",
    "match_any": ["验算特征值", "迹", "trace", "特征值之和", "特征值之积", "自检"],
    "steps": [
        r"**不变量 1（迹）**：$\displaystyle\sum_{i=1}^{n}\lambda_i = \operatorname{tr}(A) = \sum_i a_{ii}$。",
        r"**不变量 2（行列式）**：$\displaystyle\prod_{i=1}^{n}\lambda_i = \det(A)$。",
        r"这两条是“免费”的对账工具：算完特征值后立刻核对，可捕获绝大多数算术错误。",
        r"**注意**：重根按重数计（$\lambda=1$ 重数 2 则在和与积中各出现两次）。",
        r"**示例**：$A=\begin{bmatrix}2&1\\1&2\end{bmatrix}$，$\lambda=1,3$；"
        r"$\operatorname{tr}A=4=1+3$ ✓，$\det A=3=1\times3$ ✓。",
    ],
    "answer_latex": r"\sum\lambda_i=\operatorname{tr}(A),\qquad \prod\lambda_i=\det(A)",
}


def solve(problem_text: str = "") -> dict:
    return {
        "solved": True,
        "steps": TEMPLATE["steps"],
        "answer": TEMPLATE["answer_latex"],
        "answer_latex": TEMPLATE["answer_latex"],
        "method": "template:trace_det_eigen_check",
    }
