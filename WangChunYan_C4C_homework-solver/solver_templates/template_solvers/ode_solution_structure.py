"""
Solver Template: 非齐次线性微分方程解的结构
T-box concept: second_order_ode
Tool: template (structure theorem)

Oracle source: oracles/09_ode_knowledge_source.md §2, §7
"""

TEMPLATE = {
    "id": "ode_solution_structure",
    "name": "非齐次方程解的结构（通解 = 齐次通解 + 特解）",
    "concept": "second_order_ode",
    "tool": "template",
    "source": "oracles/09_ode_knowledge_source.md#2",
    "match_any": ["通解的结构", "齐次通解", "特解", "非齐次的解", "解的结构", "微分方程"],
    "match_none": ["方程组", "矩阵"],
    "steps": [
        r"设二阶线性非齐次方程 $y'' + a y' + b y = g(x)$。",
        r"**结构定理**：非齐次方程的通解 = 对应**齐次方程的通解** + 非齐次方程的**任一特解**：",
        r"$\quad y = y_h + y_p$，其中 $y_h = C_1y_1 + C_2y_2$（$y_1,y_2$ 是齐次方程的基础解系）。",
        r"**齐次通解三情形**（特征方程 $r^2+ar+b=0$）：相异实根 $C_1e^{r_1x}+C_2e^{r_2x}$；"
        r"重根 $(C_1+C_2x)e^{rx}$；复根 $e^{\alpha x}(C_1\cos\beta x+C_2\sin\beta x)$。",
        r"**叠加原理**：若 $g = g_1+g_2$，可分别求 $y_{p1},y_{p2}$ 再相加。",
    ],
    "answer_latex": r"y = y_h + y_p \quad (y_h \text{ 为齐次通解}, y_p \text{ 为非齐次特解})",
}


def solve(problem_text: str = "") -> dict:
    return {
        "solved": True,
        "steps": TEMPLATE["steps"],
        "answer": TEMPLATE["answer_latex"],
        "answer_latex": TEMPLATE["answer_latex"],
        "method": "template:ode_solution_structure",
    }
