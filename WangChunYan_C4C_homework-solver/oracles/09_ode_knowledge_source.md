# Oracle 09 — 常微分方程知识源（ODE Knowledge Source）

> **来源类型**：textbook notes + study guide + worked example set（C4C 新增知识源 #4，starter kit 中没有）
> **权威性**：primary
> **参考书**：
> - 同济大学数学系《高等数学》上册·微分方程
> - W. E. Boyce & R. C. DiPrima, *Elementary Differential Equations*, 10th ed.
> **用途**：为 `domain_skills/differential_equations.yaml` 提供概念、方法、验算与常见错误。

---

## 1. 一阶微分方程

### 1.1 可分离变量
$$\frac{dy}{dx}=f(x)g(y)\;\Longrightarrow\;\int\frac{dy}{g(y)}=\int f(x)\,dx$$
**注意**：分离时需讨论 $g(y)=0$ 的**常数解**是否丢失。

### 1.2 一阶线性方程（积分因子法）
标准形：$\;y'+P(x)y=Q(x)$

**三步法**：
1. 化为标准形，读出 $P(x)$；
2. 积分因子 $\mu(x)=e^{\int P\,dx}$；
3. 通解 $\;y=\dfrac{1}{\mu(x)}\left(\int \mu(x)Q(x)\,dx+C\right)$。

**范例**：$y'+y=e^{x}$
- $P=1\Rightarrow\mu=e^{x}$；
- $y=\dfrac{1}{e^x}\left(\int e^x e^x dx+C\right)=e^{-x}\left(\tfrac12 e^{2x}+C\right)=\tfrac12 e^{x}+Ce^{-x}$；
- **验算**：$y'=\tfrac12e^x-Ce^{-x}$，$y'+y=e^x$ ✓。

### 1.3 常见错误
1. 未先化**标准形**（$y'$ 系数必须是 1）就读 $P(x)$；
2. 积分因子漏乘右端 $Q(x)$；
3. 忘记加常数 $C$。

---

## 2. 二阶常系数线性方程

### 2.1 齐次：$y''+ay'+by=0$
**特征方程** $r^2+ar+b=0$，按判别式分三种情形：

| 根型 | 通解 |
|---|---|
| 相异实根 $r_1\neq r_2$ | $y=C_1e^{r_1x}+C_2e^{r_2x}$ |
| 重根 $r$ | $y=(C_1+C_2x)e^{rx}$ |
| 共轭复根 $\alpha\pm\beta i$ | $y=e^{\alpha x}(C_1\cos\beta x+C_2\sin\beta x)$ |

### 2.2 初值问题：用初值定常数
**范例**：$y''-3y'+2y=0,\;y(0)=1,\;y'(0)=0$
- 特征方程 $r^2-3r+2=(r-1)(r-2)=0\Rightarrow r=1,2$；
- 通解 $y=C_1e^{x}+C_2e^{2x}$；
- $y(0)=C_1+C_2=1$，$y'(0)=C_1+2C_2=0$ $\Rightarrow C_1=2,\;C_2=-1$；
- **特解** $y=2e^{x}-e^{2x}$。
- **验算**：$y'=2e^x-2e^{2x}$，$y''=2e^x-4e^{2x}$，代入 $y''-3y'+2y=(2-6+4)e^x+(-4+6-2)e^{2x}=0$ ✓；
  且 $y(0)=2-1=1$ ✓，$y'(0)=2-2=0$ ✓。

### 2.3 常见错误
1. 把特征方程的符号搞反（用 $r^2-ar+b$）；
2. 重根情形漏掉 $x$ 因子；
3. 复根情形忘记 $e^{\alpha x}$ 前因子；
4. 初值代入时把 $y'$ 的方程写错（导数系数）。

---

## 3. 通用验算策略（→ `verify.py` 的 ODE 分支）

**任何** ODE 答案都可用**两条独立检验**判定对错，无需依赖求解器：

1. **残差检验**：把 $y(x)$ 代回方程，$\text{LHS}-\text{RHS}$ 化简必须恒为 0；
2. **初值检验**：把 $x_0$ 代入 $y,y',y''$，必须逐一等于给定初值。

> 这正是 C4C 要求的"输出可核验"。`verify.py` 对 P7/P8 执行的即此两步。

---

## 4. 分类线索（→ `classification_rules`）

| 线索 | 判定 |
|---|---|
| 出现 `y''`、`y'''`、"二阶" | 二阶常系数路径 |
| 出现 `y'`、`dy/dx`、"一阶"、"微分方程" | 一阶路径 |
| 出现 `y(0)=`、`y'(0)=`、"初值" | 叠加初值处理 |
| 结构化特征 `has_ode_expression` | ODE 域兜底规则 |

---

## 5. 解析陷阱（→ `solve.py::ode_to_eq` 的实现理由）

| 陷阱 | 例子 | 处理 |
|---|---|---|
| **隐式乘法** | `3y' + 2y` 中的 `3y'`、`2y` | 用 `implicit_multiplication_application` 转换 |
| **上标** | `e^{x}` 的花括号 | `^{...}` → `**(...)` |
| **同行初值** | `y'+y=e^{x},\qquad y(0)=1` | 先按 `,`/`\qquad` 切分再解析 |
| **行分隔符冲突** | LaTeX 矩阵 `\\` 与转义 | 解析前归一化 |

---

## 6. 该知识源产出的领域线索（供 YAML 落位）

| 抽取物 | 落到 `differential_equations.yaml` 的字段 |
|---|---|
| 一阶线性标准形 + 积分因子 | `concepts[first_order_ode].formal` |
| 二阶特征方程三情形 | `concepts[second_order_ode].formal` |
| 初值问题定常数流程 | `concepts[ode_ivp].formal` |
| 隐式乘法/上标/同行初值陷阱 | `solve.py::ode_to_eq` + `extract_ics` |
| 残差检验 + 初值检验 | `validation_rules[ode]` + `verify.py` |
| 一阶/二阶/初值分类线索 | `classification_rules[].pattern` |

---

## 7. ODE 证明/概念题模板（→ `solver_templates/template_solvers/`）

| 模板 | 内容 |
|---|---|
| `ode_existence_uniqueness.py` | 一阶 IVP 解的存在唯一性定理表述与适用条件 |
| `ode_solution_structure.py` | 齐次通解 + 非齐次特解 = 非齐次通解 的结构性说明 |

（与线性代数的 7 个模板合计 **9 个新模板**，≥ L3 要求的 5 个。）
