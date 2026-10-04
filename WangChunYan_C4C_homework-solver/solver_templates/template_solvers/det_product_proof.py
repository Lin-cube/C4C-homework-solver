"""
Solver Template: det(AB) = det(A)·det(B)
T-box concept: matrix_determinant
Tool: template (proof)

Oracle source: oracles/06_linear_algebra_textbook_notes.md §2.1 (乘法性质)
               oracles/08_linear_algebra_instructor_guide.md §1 范式 A
"""

TEMPLATE = {
    "id": "det_product_proof",
    "name": "证明 det(AB) = det(A)det(B)",
    "concept": "matrix_determinant",
    "tool": "template",
    "source": "oracles/06_linear_algebra_textbook_notes.md#2.1",
    "match_any": ["det(ab)", "det(a)det(b)", "行列式的乘法", "乘积的行列式"],
    "steps": [
        r"设 $A, B$ 为 $n\times n$ 方阵，目标是证明 $\det(AB) = \det(A)\det(B)$。",
        r"当 $A$ 可逆时：$A$ 可分解为初等矩阵之积 $A = E_1E_2\cdots E_k$。",
        r"初等矩阵满足 $\det(E_i B) = \det(E_i)\det(B)$（三类初等变换对行列式的作用分别是：倍乘提因子、互换变号、倍加不变）。",
        r"逐项应用：$\det(AB) = \det(E_1)\cdots\det(E_k)\det(B) = \det(A)\det(B)$。",
        r"当 $A$ 不可逆时，$AB$ 也不可逆，两边同为零，等式仍成立。$\blacksquare$",
    ],
    "answer_latex": r"\det(AB) = \det(A)\det(B)",
}


def solve(problem_text: str = "") -> dict:
    return {
        "solved": True,
        "steps": TEMPLATE["steps"],
        "answer": TEMPLATE["answer_latex"],
        "answer_latex": TEMPLATE["answer_latex"],
        "method": "template:det_product_proof",
    }
