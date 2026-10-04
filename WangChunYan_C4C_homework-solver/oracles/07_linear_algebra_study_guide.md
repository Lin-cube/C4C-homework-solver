# Oracle 07 — 线性代数学习指南（Linear Algebra Study Guide）

> **来源类型**：study guide（学习指南，C4C 新增知识源 #2，starter kit 中没有）
> **权威性**：primary
> **性质**：面向学生的**易错点 / 误解 / 学习顺序 / 自查清单**汇编，由教材与历年作业错题归纳
> **用途**：为分类器提供"陷阱线索"，为求解器提供**答案自检规则**（validation rules）。

---

## 1. 学习顺序（依赖链）

```
矩阵基本运算
   └─→ 行列式 ──→ 逆矩阵 ──→ 线性方程组（唯一解判据）
          │            │
          └─→ 秩 ──────┴─→ 特征值与特征向量 ──→ 可对角化
```

**含义**：求解器若在"行列式"上出错，会连带影响"逆矩阵""特征值"。因此本领域把
$\det$ 作为**最高优先级的自检点**。

---

## 2. 十大常见误解（→ 求解器校验规则）

| # | 误解 | 纠正 | 是否可自动检测 |
|---|---|---|---|
| 1 | $\det(A+B)=\det A+\det B$ | 行列式非线性，此式**错误** | ✗（概念） |
| 2 | $AB=BA$ | 矩阵乘法不交换 | ✓（算两种顺序不一致即报警） |
| 3 | $\det A=0$ 时也能求逆 | 必须 $\det A\neq0$ | ✓（求逆前先算 det） |
| 4 | $\operatorname{rank}(A+B)=\operatorname{rank}A+\operatorname{rank}B$ | 只有 $\le$ 关系 | ✗（概念） |
| 5 | 特征向量可以是零向量 | 定义要求 $\mathbf v\neq\mathbf 0$ | ✓（剔除零解） |
| 6 | 特征向量唯一 | 只有一个方向，整族任意倍数 | ✓（输出基础解系） |
| 7 | 特征值一定是实数 | 实矩阵也可有复特征值 | ✓（保留复根） |
| 8 | $Ax=b$ 有解 $\iff$ $\operatorname{rank}A=n$ | 还需 $\operatorname{rank}A=\operatorname{rank}[A\lvert b]$ | ✓（比较两个秩） |
| 9 | $(AB)^T=A^TB^T$ | 应为 $B^TA^T$ | ✓（可重算验证） |
| 10 | 秩就是"非零元素个数" | 是行阶梯形非零**行数** | ✓（用 rref 统计） |

> **给求解器的指令**：第 2/3/5/6/8/9/10 条都可以在求解后自动触发**代入或重算校验**；
> 第 1/4/7 条属于概念题，走概念/证明模板回答。

---

## 3. 高频失分动作（复盘自真实作业）

1. **忘记验算**：算完特征值不与 $\operatorname{tr}A$、$\det A$ 对账。
   → 自检：$\sum\lambda_i=\operatorname{tr}A$ 且 $\prod\lambda_i=\det A$。
2. **逆矩阵的 2×2 口诀记反**：应为"主对调、副变号、除以 det"。
3. **消元时漏比较秩**：直接判断"有唯一解"却没看 $[A\lvert b]$。
4. **符号错误**：代数余子式 $(-1)^{i+j}$；副对角线元素变号。
5. **不写过程**：只给答案，缺"列式—化简—结论"三步。
   → **本求解器强制输出 steps**，正是对冲这一失分点。

---

## 4. 自查清单（Checklist，可机械执行）

对**任何**线性代数答案，依次问：

- [ ] **量纲/形状**：结果形状是否与题目要求一致？（标量 / 向量 / 矩阵）
- [ ] **可逆性**：涉及逆、除法、$P^{-1}$ 的，$\det\neq0$ 是否成立？
- [ ] **代入回代**：逆→$AA^{-1}=I$；方程组→$A\mathbf x=b$；特征对→$A\mathbf v=\lambda\mathbf v$。
- [ ] **对账不变量**：$\operatorname{tr}A=\sum\lambda_i$，$\det A=\prod\lambda_i$。
- [ ] **边界**：$\det=0$、形状不匹配、无解/无穷多解是否被显式处理？
- [ ] **表述**：特征向量是否以"基础解系"给出而非参数族？

> 这 6 条直接对应 `domain_skills/linear_algebra.yaml` 的 `validation_rules` 与
> `scripts/verify.py` 的核验分支。

---

## 5. 由本知识源新增的分类规则（→ `classification_rules`）

| 新增规则 | 触发关键词 | 理由 |
|---|---|---|
| 特征对优先于一般矩阵题 | 特征值 / 特征向量 / eigenvalue | 特征对是"矩阵"域里最具体、最易误判的题型 |
| 行列式优先于逆矩阵 | 行列式 / determinant / `det(` | 题干常同时出现两者，须先定主问 |
| 逆矩阵优先于一般矩阵运算 | 逆矩阵 / inverse / 可逆 | 避免被"矩阵"泛词吞掉 |
| 秩 | 秩 / rank | 独立方法路径 |
| 方程组 | 方程组 / linear system / 解方程组 | 需要 $A,b$ 两个对象 |
| 矩阵运算兜底 | 矩阵 / 转置 / 乘积 | 泛化兜底 |

（共 7 条，见 `linear_algebra.yaml` 的 `classification_rules`。）

---

## 6. 由本知识源新增的校验规则（→ `validation_rules`）

```yaml
validation_rules:
  matrix_determinant:  "det(A)·det(A^{-1}) = 1"
  matrix_inverse:      "A·A^{-1} = I"
  linear_system:       "解代入 Ax=b 恒成立"
  eigenvalue:          "对每个 λ 存在非零 v 使 Av=λv；且 Σλ=trA, Πλ=detA"
```
