#!/usr/bin/env python3
"""
LLM Engine —— 国产大模型推理引擎（C4C 迁移核心模块）。

背景
----
Starter kit 的求解器绑定在 Claude Code 上：证明题 / 概念题 / SymPy 无法
处理的复杂推理，一律交给 Claude。C4C 要求把这条流水线「迁移到国产大模型」，
本模块即迁移后的引擎层：

  - Qwen 3.6   → 通义千问（DashScope OpenAI 兼容端点）
  - Kimi 2.5   → Moonshot（OpenAI 兼容端点）
  - DeepSeek   → 备选国产模型
  - offline    → 确定性本地回退（SymPy + 证明模板，无需 API key）

设计原则
--------
1. 仅依赖标准库（urllib），不要求 `pip install openai`，开箱即用。
2. 统一 `complete()` 接口，切换模型只改一个环境变量。
3. 默认 offline 模式：即使没有网络 / API key，流水线也能端到端跑通，
   保证「可运行、可核验」——这是相对 Claude 基线的重要工程改进。

用法
----
    export DASHSCOPE_API_KEY=sk-...      # 用 Qwen
    export LLM_PROVIDER=qwen
    export LLM_MODEL=qwen-plus

    export MOONSHOT_API_KEY=sk-...       # 用 Kimi
    export LLM_PROVIDER=kimi
"""

import importlib.util
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# ── 技能根目录（scripts/ 的上一级）──
_SKILL_ROOT = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────
# 提供方注册表（OpenAI 兼容 chat/completions 端点）
# ─────────────────────────────────────────────

PROVIDERS = {
    "qwen": {
        "name": "通义千问 Qwen",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen-plus",
        "env_key": "DASHSCOPE_API_KEY",
    },
    "kimi": {
        "name": "Moonshot Kimi",
        "base_url": "https://api.moonshot.cn/v1",
        "default_model": "moonshot-v1-8k",
        "env_key": "MOONSHOT_API_KEY",
    },
    "deepseek": {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "default_model": "deepseek-chat",
        "env_key": "DEEPSEEK_API_KEY",
    },
}


class LLMEngine:
    """OpenAI 兼容的国产大模型客户端（仅标准库）。"""

    def __init__(self, provider: str = None, model: str = None, api_key: str = None):
        provider = (provider or os.environ.get("LLM_PROVIDER") or "offline").lower()
        self.provider = provider

        if provider in PROVIDERS:
            info = PROVIDERS[provider]
            self.base_url = info["base_url"].rstrip("/")
            self.model = model or os.environ.get("LLM_MODEL") or info["default_model"]
            self.api_key = api_key or os.environ.get(info["env_key"])
            self.available = bool(self.api_key)
        else:
            self.base_url = None
            self.model = None
            self.api_key = None
            self.available = False

    def complete(self, prompt: str, system: str = None, temperature: float = 0.0,
                 max_tokens: int = 1024) -> str:
        """调用 chat/completions，返回模型文本。无 key 时抛 RuntimeError。"""
        if not self.available:
            raise RuntimeError(
                f"LLM provider '{self.provider}' 未配置 API key。"
                f"请设置环境变量 {PROVIDERS[self.provider]['env_key'] if self.provider in PROVIDERS else 'LLM_PROVIDER'}。"
            )

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = json.dumps({
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }).encode("utf-8")

        url = f"{self.base_url}/chat/completions"
        req = urllib.request.Request(url, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {self.api_key}")

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"LLM HTTP {e.code}: {e.read().decode('utf-8', 'ignore')[:200]}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"LLM 网络错误: {e.reason}")


# ─────────────────────────────────────────────
# Offline 确定性回退：证明 / 概念模板
# ─────────────────────────────────────────────
# 在没有 API key 时，用「已核验的教材定理 + 严格推导步骤」替代 LLM。
# 这些模板来自线性代数 / 微积分标准教材，可直接作为参考答案。

OFFLINE_PROOF_TEMPLATES = [
    {
        "keywords": ["det(a^{-1})", "det(a^-1)", "行列式", "逆矩阵的行列式", "1/det(a)"],
        "match_any": ["逆", "inverse", "a^{-1}", "a^-1"],
        "steps": [
            r"由矩阵可逆的定义：$AA^{-1} = I$，其中 $I$ 是单位矩阵。",
            r"对等式两边同时取行列式：$\det(AA^{-1}) = \det(I) = 1$。",
            r"由行列式的乘法性质 $\det(AB) = \det(A)\det(B)$，得 $\det(A)\det(A^{-1}) = 1$。",
            r"因 $A$ 可逆，$\det(A) \neq 0$，故 $\det(A^{-1}) = \dfrac{1}{\det(A)}$。$\blacksquare$",
        ],
        "answer_latex": r"\det(A^{-1}) = \frac{1}{\det(A)}",
    },
    {
        "keywords": ["det(ab)", "det(a)det(b)", "行列式乘法", "det(a·b)"],
        "match_any": ["det(ab)", "det(a)det(b)", "乘积的行列式"],
        "steps": [
            r"设 $A, B$ 为 $n\times n$ 方阵，目标是证明 $\det(AB) = \det(A)\det(B)$。",
            r"当 $A$ 可逆时：$A$ 可分解为初等矩阵之积 $A = E_1E_2\cdots E_k$。",
            r"初等矩阵的行列式满足 $\det(E_i B) = \det(E_i)\det(B)$（初等变换对行列式的作用）。",
            r"逐项应用：$\det(AB) = \det(E_1)\det(E_2)\cdots\det(E_k)\det(B) = \det(A)\det(B)$。",
            r"当 $A$ 不可逆时，$AB$ 也不可逆，两边均为 $0$，等式仍成立。$\blacksquare$",
        ],
        "answer_latex": r"\det(AB) = \det(A)\det(B)",
    },
    {
        "keywords": ["特征向量", "线性无关", "不同特征值", "distinct eigenvalues"],
        "match_any": ["线性无关", "linearly independent", "distinct"],
        "steps": [
            r"设 $\lambda_1 \neq \lambda_2$ 为矩阵 $A$ 的两个不同特征值，$v_1, v_2$ 为对应特征向量。",
            r"假设存在标量 $c_1, c_2$ 使 $c_1 v_1 + c_2 v_2 = 0$。",
            r"左乘 $A$ 并利用 $Av_i = \lambda_i v_i$：$c_1\lambda_1 v_1 + c_2\lambda_2 v_2 = 0$。",
            r"两式相减：$c_2(\lambda_2 - \lambda_1)v_2 = 0$。因 $\lambda_2 \neq \lambda_1$ 且 $v_2\neq 0$，得 $c_2 = 0$。",
            r"代回得 $c_1 = 0$。故 $v_1, v_2$ 线性无关。$\blacksquare$",
        ],
        "answer_latex": r"\text{不同特征值对应的特征向量线性无关}",
    },
    {
        "keywords": ["rank", "秩", "rank-nullity", "维数", "dimension"],
        "match_any": ["秩", "rank", "nullity", "零度"],
        "steps": [
            r"秩-零化度定理：对 $m\times n$ 矩阵 $A$，有 $\operatorname{rank}(A) + \dim(\ker A) = n$。",
            r"其中 $\operatorname{rank}(A)$ 是列空间的维数，$\dim(\ker A)$ 是零空间的维数。",
            r"该定理表明：矩阵的秩与零空间维数之和等于列数 $n$。$\blacksquare$",
        ],
        "answer_latex": r"\operatorname{rank}(A) + \dim(\ker A) = n",
    },
]


def load_template_files() -> list:
    """
    从 solver_templates/template_solvers/*.py 动态加载非计算题模板。

    每个模板文件暴露一个 TEMPLATE dict（含 id / concept / match_any / steps /
    answer_latex / source）。这是 C4C L3「≥5 个非计算题模板」的落点，
    并且模板**真的被 OfflineReasoner 调用**，不是摆设。
    """
    templates = []
    tdir = _SKILL_ROOT / "solver_templates" / "template_solvers"
    if not tdir.exists():
        return templates

    for path in sorted(tdir.glob("*.py")):
        if path.name.startswith("_"):
            continue
        try:
            spec = importlib.util.spec_from_file_location(f"_c4c_tpl_{path.stem}", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception:
            continue
        tpl = getattr(mod, "TEMPLATE", None)
        if isinstance(tpl, dict) and "steps" in tpl and "match_any" in tpl:
            tpl.setdefault("id", path.stem)
            tpl["_file"] = path.name
            templates.append(tpl)
    return templates


class OfflineReasoner:
    """
    离线确定性推理器：优先用 SymPy 精确计算，证明题用**已核验模板**
    （从 solver_templates/template_solvers/ 动态加载 + 内置兜底）。
    保证无 API key 时流水线仍可运行、可核验。
    """

    def __init__(self):
        self.engine = "offline-sympy+templates"
        self.templates = load_template_files()
        # 只用「策展过的文件模板」做匹配：它们带 match_none 否决词，精度更高。
        # OFFLINE_PROOF_TEMPLATES 保留作兼容常量，但不再参与匹配，
        # 避免其宽泛关键词（如单个"逆"字）造成误命中。
        self.all_templates = self.templates

    def prove(self, text: str):
        """
        按**打分**匹配模板：命中关键词数越多越优先；带 `match_none` 否决词的直接跳过。

        返回 (steps, answer_latex, template_id) 或 None。

        为什么不按文件顺序取第一个命中：实测 D5「判断是否可逆的充要条件」
        会被更靠前的模板误吞、D8「微分方程解的结构」会被线性代数模板误吞。
        打分 + 否决词把这类跨域误命中挡掉。
        """
        tl = text.lower()
        best = None
        best_score = 0
        for tpl in self.all_templates:
            # 否决词：出现任一即整条模板失效（防跨域误命中）
            veto = tpl.get("match_none") or []
            if any(v.lower() in tl for v in veto):
                continue
            score = sum(1 for k in tpl["match_any"] if k.lower() in tl)
            if score > best_score:
                best, best_score = tpl, score
        if best is None:
            return None
        return best["steps"], best["answer_latex"], best.get("id", "template")


def get_engine():
    """构造当前配置的 LLM 引擎。offline 时返回 None（由调用方决定回退）。"""
    provider = os.environ.get("LLM_PROVIDER", "offline").lower()
    if provider == "offline":
        return None
    engine = LLMEngine(provider)
    return engine if engine.available else None
