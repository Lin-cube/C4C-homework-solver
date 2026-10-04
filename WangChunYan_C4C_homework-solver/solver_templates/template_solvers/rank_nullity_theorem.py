"""
Solver Template: 秩-零化度定理 rank(A) + dim ker(A) = n
T-box concept: matrix_rank
Tool: template (theorem statement + justification)

Oracle source: oracles/06_linear_algebra_textbook_notes.md §6.1
               oracles/08_linear_algebra_instructor_guide.md §1 范式 D（维数夹逼）
"""

TEMPLATE = {
    "id": "rank_nullity_theorem",
    "name": "秩-零化度定理",
    "concept": "matrix_rank",
    "tool": "template",
    "source": "oracles/06_linear_algebra_textbook_notes.md#6.1",
    "match_any": ["秩-零化度", "rank-nullity", "零空间维数", "nullity", "零度"],
    "steps": [
        r"设 $A$ 为 $m\times n$ 矩阵，$\ker A = \{\mathbf x : A\mathbf x = \mathbf 0\}$ 是零空间。",
        r"$\operatorname{rank}(A)$ 定义为列空间 $\operatorname{Col}A$ 的维数，$\dim\ker A$ 称为零化度。",
        r"由主元列与自由变量的计数：$n$ 列中，主元列数 $=\operatorname{rank}(A)$，自由变量数 $=\dim\ker A$。",
        r"两者之和恰为列数：$\operatorname{rank}(A) + \dim\ker(A) = n$。",
        r"即：$\boxed{\operatorname{rank}(A) + \dim\ker(A) = n}$（秩-零化度定理）。$\blacksquare$",
    ],
    "answer_latex": r"\operatorname{rank}(A) + \dim(\ker A) = n",
}


def solve(problem_text: str = "") -> dict:
    return {
        "solved": True,
        "steps": TEMPLATE["steps"],
        "answer": TEMPLATE["answer_latex"],
        "answer_latex": TEMPLATE["answer_latex"],
        "method": "template:rank_nullity_theorem",
    }
