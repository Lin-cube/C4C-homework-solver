"""
Solver Template: det(A^{-1}) = 1/det(A)
T-box concept: matrix_inverse / matrix_determinant
Tool: template (proof, no computation needed)

Oracle source: oracles/08_linear_algebra_instructor_guide.md §1 范式 A
               oracles/06_linear_algebra_textbook_notes.md §2.1

Precondition check is MANDATORY (instructor guide §2 rubric: 前提条件检查 20%).
"""

TEMPLATE = {
    "id": "det_inverse_proof",
    "name": "证明 det(A⁻¹) = 1/det(A)",
    "concept": "matrix_inverse",
    "tool": "template",
    "source": "oracles/08_linear_algebra_instructor_guide.md#范式A",
    "match_any": ["a^{-1}", "a^-1", "逆矩阵的行列式", "det(a^{-1})"],
    "steps": [
        r"由矩阵可逆的定义：$AA^{-1} = I$，其中 $I$ 是单位矩阵。",
        r"对等式两边同时取行列式：$\det(AA^{-1}) = \det(I) = 1$。",
        r"由行列式的乘法性质 $\det(AB) = \det(A)\det(B)$，得 $\det(A)\det(A^{-1}) = 1$。",
        r"因 $A$ 可逆，$\det(A) \neq 0$，故 $\det(A^{-1}) = \dfrac{1}{\det(A)}$。$\blacksquare$",
    ],
    "answer_latex": r"\det(A^{-1}) = \frac{1}{\det(A)}",
}


def solve(problem_text: str = "") -> dict:
    return {
        "solved": True,
        "steps": TEMPLATE["steps"],
        "answer": TEMPLATE["answer_latex"],
        "answer_latex": TEMPLATE["answer_latex"],
        "method": "template:det_inverse_proof",
    }
