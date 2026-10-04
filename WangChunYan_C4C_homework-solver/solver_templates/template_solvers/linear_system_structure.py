"""
Solver Template: 线性方程组解的结构（唯一 / 无穷多 / 无解）
T-box concept: linear_system
Tool: template (case analysis on ranks)

Oracle source: oracles/06_linear_algebra_textbook_notes.md §4.1
               oracles/07_linear_algebra_study_guide.md §2 误解 #8
"""

TEMPLATE = {
    "id": "linear_system_structure",
    "name": "线性方程组解的结构判据",
    "concept": "linear_system",
    "tool": "template",
    "source": "oracles/06_linear_algebra_textbook_notes.md#4.1",
    "match_any": ["解的结构", "唯一解", "无穷多解", "无解", "讨论解的", "解的个数"],
    "match_none": ["微分方程", "ode", "differential equation", "特征值"],
    "steps": [
        r"设 $A\mathbf x = \mathbf b$，增广矩阵 $[A\mid \mathbf b]$，$A$ 为 $m\times n$。",
        r"**无解** $\iff \operatorname{rank}(A) < \operatorname{rank}[A\mid \mathbf b]$。",
        r"**唯一解** $\iff \operatorname{rank}(A) = \operatorname{rank}[A\mid \mathbf b] = n$。",
        r"**无穷多解** $\iff \operatorname{rank}(A) = \operatorname{rank}[A\mid \mathbf b] < n$，自由度为 $n - \operatorname{rank}(A)$。",
        r"**常见错误**：只比较 $\operatorname{rank}(A)$ 与 $n$，忘记比较 $\operatorname{rank}[A\mid \mathbf b]$——",
        r"后者才能区分“无解”与“无穷多解”。",
    ],
    "answer_latex": r"\text{无解} \iff r(A)<r([A|b]);\quad \text{唯一解} \iff r(A)=r([A|b])=n",
}


def solve(problem_text: str = "") -> dict:
    return {
        "solved": True,
        "steps": TEMPLATE["steps"],
        "answer": TEMPLATE["answer_latex"],
        "answer_latex": TEMPLATE["answer_latex"],
        "method": "template:linear_system_structure",
    }
