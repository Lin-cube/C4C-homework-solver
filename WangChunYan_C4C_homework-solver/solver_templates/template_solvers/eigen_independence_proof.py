"""
Solver Template: 不同特征值对应的特征向量线性无关
T-box concept: eigenvalue
Tool: template (proof)

Oracle source: oracles/08_linear_algebra_instructor_guide.md §1 范式 B（线性组合零化法）
               oracles/06_linear_algebra_textbook_notes.md §5.1
"""

TEMPLATE = {
    "id": "eigen_independence_proof",
    "name": "证明不同特征值对应的特征向量线性无关",
    "concept": "eigenvalue",
    "tool": "template",
    "source": "oracles/08_linear_algebra_instructor_guide.md#范式B",
    "match_any": ["线性无关", "linearly independent", "不同特征值", "distinct eigenvalue"],
    "steps": [
        r"设 $\lambda_1 \neq \lambda_2$ 是 $A$ 的两个不同特征值，$v_1, v_2$ 是对应的非零特征向量。",
        r"反设存在标量 $c_1, c_2$ 使 $c_1 v_1 + c_2 v_2 = 0$。$\quad$（**线性组合零化法**）",
        r"两边左乘 $A$，并用 $Av_i = \lambda_i v_i$：$\;c_1\lambda_1 v_1 + c_2\lambda_2 v_2 = 0$。",
        r"用第二式减去 $\lambda_2\times$（第一式）：$\;c_1(\lambda_1-\lambda_2)v_1 = 0$。",
        r"因 $\lambda_1\neq\lambda_2$ 且 $v_1\neq 0$，得 $c_1 = 0$；代回第一式得 $c_2 = 0$。",
        r"故 $v_1, v_2$ 线性无关。对多个不同特征值可归纳推广到整族。$\blacksquare$",
    ],
    "answer_latex": r"\text{不同特征值对应的特征向量线性无关}",
}


def solve(problem_text: str = "") -> dict:
    return {
        "solved": True,
        "steps": TEMPLATE["steps"],
        "answer": TEMPLATE["answer_latex"],
        "answer_latex": TEMPLATE["answer_latex"],
        "method": "template:eigen_independence_proof",
    }
