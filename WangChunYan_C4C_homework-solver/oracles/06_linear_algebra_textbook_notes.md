# Oracle 06 — 线性代数教材章节笔记（Linear Algebra Textbook Notes）

> **来源类型**：textbook notes（教材章节笔记，C4C 新增知识源 #1，starter kit 中没有）
> **权威性**：primary
> **参考书**：
> - David C. Lay, *Linear Algebra and Its Applications*, 5th ed.（Ch. 1–5）
> - 同济大学数学系《线性代数》第六版（第 1–5 章）
> **用途**：为 `domain_skills/linear_algebra.yaml` 提供概念、方法、分类线索的原始知识。

---

## 1. 矩阵与运算（对应 Ch.1 / 同济第 2 章）

### 1.1 核心定义
- **矩阵**：$m\times n$ 数表 $A=(a_{ij})$；相等要求同型且逐元素相等。
- **加法 / 数乘**：同型矩阵逐元素运算。
- **乘法**：$A_{m\times k}B_{k\times n}=C_{m\times n}$，$c_{ij}=\sum_{p=1}^{k}a_{ip}b_{pj}$。
  - **不满足交换律**：一般 $AB\neq BA$。
  - **消去律不成立**：$AB=AC \not\Rightarrow B=C$（除非 $A$ 可逆）。
- **转置**：$(A^T)^T=A$，$(A+B)^T=A^T+B^T$，$\boxed{(AB)^T=B^TA^T}$（反序律）。
- **对称 / 反对称**：$A^T=A$ / $A^T=-A$。

### 1.2 方法要点（→ 分类线索）
| 题面线索 | 方法 | 工具 |
|---|---|---|
| "计算 AB"、"乘积"、"multiply" | 矩阵乘法（先验形状） | 逐元素求和 |
| "转置"、"transpose"、"$(AB)^T$" | 反序律 | 逐元素搬运 |
| "点积 / 内积 / dot" | $\mathbf u\cdot\mathbf v=\sum u_iv_i=\mathbf u^T\mathbf v$ | 向量乘法 |
| "叉积 / cross" | $\mathbf u\times\mathbf v$ 三阶行列式展开 | 行列式 |

### 1.3 常见错误
1. 把 $AB$ 与 $BA$ 混为一谈。
2. $(AB)^T$ 写成 $A^TB^T$（应为 $B^TA^T$）。
3. 形状不匹配仍强算（$A_{2\times3}B_{2\times3}$ 无定义）。

---

## 2. 行列式（对应 Ch.3 / 同济第 1 章）

### 2.1 核心定理
- **2×2**：$\det\begin{bmatrix}a&b\\c&d\end{bmatrix}=ad-bc$。
- **按行（列）展开**：$\det A=\sum_{j=1}^{n}a_{ij}A_{ij}$，$A_{ij}=(-1)^{i+j}M_{ij}$（代数余子式）。
- **三角矩阵**：$\det A=\prod_i a_{ii}$。
- **乘法性质**：$\boxed{\det(AB)=\det A\cdot\det B}$。
- **转置不变**：$\det A^T=\det A$。
- **可逆判据**：$A$ 可逆 $\iff \det A\neq 0$。
- **逆的行列式**：$\boxed{\det(A^{-1})=1/\det A}$（由 $\det(AA^{-1})=\det I=1$ 推出）。

### 2.2 方法要点
| 线索 | 方法 |
|---|---|
| "行列式"、"determinant"、"det(" | 直接展开或化为三角 |
| "利用行列式性质证明" | 用 $\det(AB)=\det A\det B$ 搭桥 |

### 2.3 常见错误
1. 认为 $\det(A+B)=\det A+\det B$（**错误**，行列式不是线性的）。
2. 忘记 $|A^{-1}|=1/|A|$ 的前提是 $A$ 可逆。
3. 展开时代数余子式符号 $(-1)^{i+j}$ 记错。

---

## 3. 逆矩阵（对应 Ch.2 / 同济第 2 章）

### 3.1 核心定理
- **定义**：$AA^{-1}=A^{-1}A=I$。
- **2×2 公式**：$\begin{bmatrix}a&b\\c&d\end{bmatrix}^{-1}=\dfrac{1}{ad-bc}\begin{bmatrix}d&-b\\-c&a\end{bmatrix}$。
- **伴随矩阵法**：$A^{-1}=\dfrac{1}{\det A}\operatorname{adj}(A)$。
- **可逆的等价条件**（同一命题的多种表述，考试常考）：
  $A$ 可逆 $\iff \det A\neq0 \iff \operatorname{rank}A=n \iff$ 列向量线性无关 $\iff Ax=0$ 只有零解 $\iff$ 0 不是特征值。

### 3.2 常见错误
1. 2×2 公式里忘记"主对角线互换、副对角线变号"的顺序。
2. 未先验证 $\det A\neq0$ 就套公式。

---

## 4. 线性方程组（对应 Ch.1 / 同济第 3 章）

### 4.1 解的结构
$Ax=b$：
- **唯一解** $\iff \operatorname{rank}A=\operatorname{rank}[A|b]=n$；
- **无穷多解** $\iff \operatorname{rank}A=\operatorname{rank}[A|b]<n$；
- **无解** $\iff \operatorname{rank}A<\operatorname{rank}[A|b]$。

### 4.2 方法：高斯消元
1. 写增广矩阵 $[A|b]$；
2. 初等行变换化为行阶梯形；
3. 回代（或继续化行最简形，直接读解）。

### 4.3 常见错误
1. 只比较 $\operatorname{rank}A$ 与 $n$，忘记比较 $\operatorname{rank}[A|b]$。
2. 行变换时把"倍加"误写成"倍乘"。

---

## 5. 特征值与特征向量（对应 Ch.5 / 同济第 4 章）

### 5.1 核心定义与定理
- **定义**：$A\mathbf v=\lambda\mathbf v$，$\mathbf v\neq\mathbf 0$。
- **特征方程**：$\det(A-\lambda I)=0$（特征多项式）。
- **迹与行列式的桥**：$\sum\lambda_i=\operatorname{tr}A$，$\prod\lambda_i=\det A$（**验算利器**）。
- **线性无关性**：不同特征值对应的特征向量线性无关。
- **可对角化**：$A$ 有 $n$ 个线性无关特征向量 $\iff A=PDP^{-1}$。

### 5.2 方法：求特征对的四步法
1. 解特征方程 $\det(A-\lambda I)=0$ 得全部 $\lambda$；
2. 对每个 $\lambda$ 解齐次方程 $(A-\lambda I)\mathbf v=\mathbf 0$；
3. 取基础解系作为特征向量；
4. 用 $\sum\lambda_i=\operatorname{tr}A$、$\prod\lambda_i=\det A$ 验算。

### 5.3 常见错误
1. 把特征向量写成含自由参数的整族（应取基础解系）。
2. 忘记"特征向量不能是零向量"。
3. 解 $(A-\lambda I)\mathbf v=0$ 时算错 $A-\lambda I$ 的对角元。

---

## 6. 秩（对应 Ch.2 / 同济第 3 章）

### 6.1 核心定理
- **定义**：非零子式的最高阶数 = 行阶梯形非零行数。
- **行秩 = 列秩 = rank**。
- **秩-零化度定理**：$\boxed{\operatorname{rank}A+\dim\ker A=n}$。
- **乘积的秩**：$\operatorname{rank}(AB)\le\min(\operatorname{rank}A,\operatorname{rank}B)$。

### 6.2 常见错误
1. 把"行阶梯形非零行数"与"非零元素个数"混淆。
2. 认为 $\operatorname{rank}(A+B)=\operatorname{rank}A+\operatorname{rank}B$（**错误**）。

---

## 7. 该知识源产出的领域线索（供 YAML 落位）

| 抽取物 | 落到 `linear_algebra.yaml` 的字段 |
|---|---|
| 矩阵/行列式/逆/方程组/特征值/秩 六大概念 | `concepts[].id` / `.name` / `.formal` |
| $\det(AB)=\det A\det B$、$\det(A^{-1})=1/\det A$ | `concepts[matrix_determinant].formal` + 证明模板 |
| 2×2 逆公式 | `solution_methods[matrix_inverse_solver].applies_when` |
| 高斯消元流程 | `solution_methods[linear_system_solver].applies_when` |
| 特征方程 + 迹/行列式验算 | `concepts[eigenvalue].formal` |
| 秩-零化度定理 | `concepts[matrix_rank].formal` + 证明模板 |
| 题面关键词（行列式/特征值/逆矩阵/秩/方程组） | `classification_rules[].pattern.text_contains` |
| 上述常见错误 | `oracles/07_linear_algebra_study_guide.md` → 校验规则 |
