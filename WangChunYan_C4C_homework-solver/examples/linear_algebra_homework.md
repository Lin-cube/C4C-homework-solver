# 线性代数与微分方程 作业（第 3 章·矩阵 + 第 6 章·常微分方程）

> 姓名：Wang ChunYan　｜　学号：2024XXXXXX　｜　日期：2026-07-17
> 说明：本作业为「线性代数 + 常微分方程」综合练习，用于验证 C4C 求解器在**非微积分极限**学科上的正确率。

---

## 第 1 题　计算行列式

设三阶方阵

$$
A = \begin{pmatrix} 3 & 1 & 1 \\ 1 & 3 & 1 \\ 1 & 1 & 3 \end{pmatrix}
$$

求行列式 $\det(A)$ 的值。

---

## 第 2 题　求逆矩阵

设矩阵

$$
A = \begin{pmatrix} 2 & 1 \\ 1 & 1 \end{pmatrix}
$$

判断 $A$ 是否可逆；若可逆，求其逆矩阵 $A^{-1}$。

---

## 第 3 题　求解线性方程组

求解线性方程组 $Ax = b$，其中

$$
A = \begin{pmatrix} 1 & 1 & 1 \\ 2 & -1 & 1 \\ 1 & 2 & -1 \end{pmatrix}, \quad
b = \begin{pmatrix} 6 \\ 3 \\ 2 \end{pmatrix}
$$

即：

$$
\begin{cases} x + y + z = 6 \\ 2x - y + z = 3 \\ x + 2y - z = 2 \end{cases}
$$

---

## 第 4 题　求特征值与特征向量

设矩阵

$$
A = \begin{pmatrix} 2 & 1 \\ 1 & 2 \end{pmatrix}
$$

求 $A$ 的全部特征值与对应的特征向量。

---

## 第 5 题　矩阵乘法

设

$$
A = \begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}, \quad
B = \begin{pmatrix} 5 & 6 \\ 7 & 8 \end{pmatrix}
$$

计算矩阵乘积 $AB$。

---

## 第 6 题　求矩阵的秩

设矩阵

$$
A = \begin{pmatrix} 1 & 2 & 3 \\ 4 & 5 & 6 \\ 7 & 8 & 9 \end{pmatrix}
$$

求 $\operatorname{rank}(A)$。

---

## 第 7 题　一阶线性微分方程（初值问题）

求解初值问题：

$$
y' + y = e^{x}, \qquad y(0) = 1
$$

---

## 第 8 题　二阶常系数齐次微分方程（初值问题）

求解初值问题：

$$
y'' - 3y' + 2y = 0, \qquad y(0) = 1, \quad y'(0) = 0
$$

---

## 第 9 题　证明题

证明：若 $n$ 阶方阵 $A$ 可逆，则

$$
\det(A^{-1}) = \frac{1}{\det(A)}
$$
