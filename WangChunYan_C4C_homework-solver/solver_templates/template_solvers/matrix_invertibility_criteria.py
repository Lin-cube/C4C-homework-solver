"""
Solver Template: 矩阵可逆的等价条件（清单式定理）
T-box concept: matrix_inverse
Tool: template (theorem statement)

Oracle source: oracles/06_linear_algebra_textbook_notes.md §3.1（可逆的等价条件）
               oracles/08_linear_algebra_instructor_guide.md §1 范式 D
"""

TEMPLATE = {
    "id": "matrix_invertibility_criteria",
    "name": "矩阵可逆的等价条件",
    "concept": "matrix_inverse",
    "tool": "template",
    "source": "oracles/06_linear_algebra_textbook_notes.md#3.1",
    "match_any": ["可逆的等价", "可逆的充要", "何时可逆", "判断是否可逆", "invertible iff",
                  "充要条件", "等价条件", "等价的充要", "是否可逆"],
    "steps": [
        r"设 $A$ 为 $n$ 阶方阵。下列命题**两两等价**（Invertible Matrix Theorem）：",
        r"(1) $A$ 可逆；$\quad$(2) $\det(A) \neq 0$；$\quad$(3) $\operatorname{rank}(A) = n$；",
        r"(4) $A$ 的 $n$ 个列向量线性无关；$\quad$(5) $A\mathbf x = \mathbf 0$ 只有零解；",
        r"(6) 对任意 $\mathbf b$，$A\mathbf x = \mathbf b$ 有唯一解；$\quad$(7) $0$ 不是 $A$ 的特征值。",
        r"若以上任一条**不成立**，则 $A$ 不可逆（奇异），此时 $\det(A)=0$ 且 $\operatorname{rank}(A)<n$。",
    ],
    "answer_latex": r"A \text{ 可逆} \iff \det(A)\neq 0 \iff \operatorname{rank}(A)=n \iff \text{列向量线性无关}",
}


def solve(problem_text: str = "") -> dict:
    return {
        "solved": True,
        "steps": TEMPLATE["steps"],
        "answer": TEMPLATE["answer_latex"],
        "answer_latex": TEMPLATE["answer_latex"],
        "method": "template:matrix_invertibility_criteria",
    }
