#!/usr/bin/env python3
"""
L4 Path C 演示：SymPy-only  vs  LLM-Augmented（证明 / 推理题）

目的
----
Path C 的第三个 checkbox 要求「Show this solves problems that SymPy alone cannot」。
本脚本对同一批**非计算题**跑两条路径，输出对比表：

  Path A（SymPy-only）   ：把它当计算题丢给 SymPy 计算链 —— 无表达式可算 → 未解
  Path B（LLM-Augmented）：路由到 solve_proof —— 离线走已核验定理模板；配置 key 后走 Qwen/Kimi

同时打印注入 LLM 提示的**领域知识上下文**（T-box 检索结果），
对应 Path C 的第二个 checkbox「structured LLM prompting that uses domain knowledge as context」。

用法:
    python demo_l4_path_c.py                 # 离线模板路径
    python demo_l4_path_c.py --provider qwen --api-key sk-xxx   # 真 LLM 路径
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent))

from solve import solve_calculation, solve_proof, _domain_context  # noqa: E402
from llm_engine import get_engine, load_template_files  # noqa: E402


# ── 非计算题测试集（证明 / 概念 / 结构定理）────────────────
PROOF_PROBLEMS = [
    {"id": "D1", "text": "证明：若 $n$ 阶方阵 $A$ 可逆，则 $\\det(A^{-1}) = \\frac{1}{\\det(A)}$",
     "math_expressions": [], "type": "proof", "sub_problems": []},
    {"id": "D2", "text": "证明行列式的乘法性质：$\\det(AB) = \\det(A)\\det(B)$",
     "math_expressions": [], "type": "proof", "sub_problems": []},
    {"id": "D3", "text": "证明：矩阵不同特征值对应的特征向量线性无关。",
     "math_expressions": [], "type": "proof", "sub_problems": []},
    {"id": "D4", "text": "叙述秩-零化度定理（rank-nullity theorem）并说明其含义。",
     "math_expressions": [], "type": "proof", "sub_problems": []},
    {"id": "D5", "text": "判断一个方阵是否可逆，有哪些等价的充要条件？",
     "math_expressions": [], "type": "proof", "sub_problems": []},
    {"id": "D6", "text": "线性方程组 $Ax=b$ 解的结构如何判定？说明无解与无穷多解的区别。",
     "math_expressions": [], "type": "proof", "sub_problems": []},
    {"id": "D7", "text": "一阶初值问题解的存在唯一性条件是什么？",
     "math_expressions": [], "type": "proof", "sub_problems": []},
    {"id": "D8", "text": "非齐次线性微分方程解的结构是什么？通解怎么由齐次通解与特解组成？",
     "math_expressions": [], "type": "proof", "sub_problems": []},
    {"id": "D9", "text": "如何用迹和行列式验算特征值？请说明这两个不变量。",
     "math_expressions": [], "type": "proof", "sub_problems": []},
]


def sympy_only(problem: dict) -> dict:
    """Path A：只用 SymPy 计算链（模拟未接入 LLM/模板的 starter kit 行为）。"""
    p = dict(problem)
    p["type"] = "calculation"
    return solve_calculation(p)


def llm_augmented(problem: dict) -> dict:
    """Path B：LLM 增强路径（离线定理模板 → 国产 LLM）。"""
    return solve_proof(problem)


def main():
    ap = argparse.ArgumentParser(description="L4 Path C 能力对比演示")
    ap.add_argument("--provider", choices=["qwen", "kimi", "deepseek"], help="国产大模型提供商")
    ap.add_argument("--model", help="模型名")
    ap.add_argument("--api-key", help="API key")
    ap.add_argument("--json", help="把对比结果写入 JSON")
    args = ap.parse_args()

    if args.provider:
        os.environ["LLM_PROVIDER"] = args.provider
        if args.model:
            os.environ["LLM_MODEL"] = args.model
        if args.api_key:
            env_key = {"qwen": "DASHSCOPE_API_KEY", "kimi": "MOONSHOT_API_KEY",
                       "deepseek": "DEEPSEEK_API_KEY"}[args.provider]
            os.environ[env_key] = args.api_key

    engine = get_engine()
    engine_name = f"{engine.provider} / {engine.model}" if engine else "offline（离线定理模板）"
    templates = load_template_files()

    print("=" * 78)
    print("L4 Path C 演示：SymPy-only  vs  LLM-Augmented")
    print(f"  LLM 引擎: {engine_name}")
    print(f"  已加载模板: {len(templates)} 个 —— " + ", ".join(t["id"] for t in templates))
    print("=" * 78)
    print()

    rows = []
    a_solved = b_solved = 0
    for p in PROOF_PROBLEMS:
        ra = sympy_only(p)
        rb = llm_augmented(p)
        a_ok = bool(ra.get("solved"))
        b_ok = bool(rb.get("solved"))
        a_solved += a_ok
        b_solved += b_ok
        rows.append({
            "id": p["id"],
            "sympy_only_solved": a_ok,
            "sympy_only_reason": ra.get("reason", "") if not a_ok else "",
            "llm_solved": b_ok,
            "llm_solver": rb.get("solver", ""),
            "llm_answer": rb.get("answer_latex", ""),
        })
        mark_a = "✅" if a_ok else "❌"
        mark_b = "✅" if b_ok else "❌"
        print(f"{p['id']}  SymPy-only {mark_a}   LLM-augmented {mark_b}  [{rb.get('solver','')}]")
        if not a_ok:
            print(f"     ↳ SymPy-only 失败原因: {ra.get('reason','')[:70]}")
        if b_ok:
            print(f"     ↳ 解出: {rb.get('answer_latex','')[:70]}")
        print()

    n = len(PROOF_PROBLEMS)
    print("=" * 78)
    print(f"SymPy-only    求解率: {a_solved}/{n} = {100*a_solved//n}%")
    print(f"LLM-Augmented 求解率: {b_solved}/{n} = {100*b_solved//n}%")
    print("=" * 78)
    print()
    print("── 领域知识上下文示例（注入 LLM 提示的内容，D1）──")
    print(_domain_context(PROOF_PROBLEMS[0]) or "（无匹配）")

    if args.json:
        Path(args.json).write_text(json.dumps({
            "engine": engine_name,
            "templates": [t["id"] for t in templates],
            "sympy_only_solved": a_solved,
            "llm_augmented_solved": b_solved,
            "total": n,
            "rows": rows,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n对比结果已写入: {args.json}")


if __name__ == "__main__":
    main()
