"""
Solver Template: 一阶初值问题解的存在唯一性
T-box concept: ode_ivp
Tool: template (theorem statement + applicability check)

Oracle source: oracles/09_ode_knowledge_source.md §3, §7
"""

TEMPLATE = {
    "id": "ode_existence_uniqueness",
    "name": "一阶 IVP 解的存在唯一性",
    "concept": "ode_ivp",
    "tool": "template",
    "source": "oracles/09_ode_knowledge_source.md#3",
    "match_any": ["存在唯一", "existence and uniqueness", "解是否唯一", "初值问题是否有解"],
    "steps": [
        r"**定理（Picard–Lindelöf）**：考虑初值问题 $y' = f(x,y),\; y(x_0)=y_0$。",
        r"若 $f$ 在矩形区域 $R$ 上**连续**，且对 $y$ 满足 **Lipschitz 条件**"
        r"（如 $\partial f/\partial y$ 连续且有界），",
        r"则存在 $\delta>0$，使该初值问题在 $|x-x_0|<\delta$ 上**存在且唯一**解。",
        r"**实用判据**：$f$ 与其偏导 $\partial f/\partial y$ 在 $(x_0,y_0)$ 邻域连续 $\Rightarrow$ 局部存在唯一。",
        r"**反例**：$y' = y^{2/3},\; y(0)=0$ 在 $y=0$ 处不满足 Lipschitz 条件，解不唯一。",
    ],
    "answer_latex": r"f,\ \partial f/\partial y \text{ 连续} \Rightarrow \text{IVP 局部存在且唯一}",
}


def solve(problem_text: str = "") -> dict:
    return {
        "solved": True,
        "steps": TEMPLATE["steps"],
        "answer": TEMPLATE["answer_latex"],
        "answer_latex": TEMPLATE["answer_latex"],
        "method": "template:ode_existence_uniqueness",
    }
