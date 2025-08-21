# PaperPlot

Matplotlib 样式与工具库，助力论文与科研绘图（IEEE 与中国国标 GB 风格）。

## 特性
- 内置两种样式：IEEE、GB
- 内置字体注册：SimSun（中文）、Times New Roman（英文）
- 出版级默认参数（字号、线宽、网格、矢量字体等）

## 安装（开发阶段）
```bash
pip install -e .[dev]
```

## 快速开始
```python
import matplotlib.pyplot as plt
from ppplt import apply_style

apply_style("IEEE")  # 或 "GB"
fig, ax = plt.subplots()
ax.plot([0, 1, 2], [0, 1, 0], label="示例 Example")
ax.set_xlabel("X 轴")
ax.set_ylabel("Y 轴")
ax.legend()
plt.show()
```

## 一键预设（样式 + 配色）
```python
from ppplt import apply_paper_preset

apply_paper_preset("ieee-modern")  # 等效于: apply_style("IEEE") + Modern Scientific 配色
```

可用预设（大小写不敏感）：
- ieee-modern / ieee-contrast1 / ieee-okabe / ieee-gray
- gb-modern / gb-contrast2 / gb-okabe / gb-gray

## 配色方案与选型建议
- 颜色集（部分）：Contrast Set 1/2、Muted Yet Bold、Refined Contrast、Modern Scientific、Extended Elegance、Pastel High Contrast、Softened Bold Colors
- 色盲友好：Okabe-Ito、Brewer-Qual-Soft
- 灰度安全：Grayscale-Safe（打印或复印友好）

判断灰度可区分（简易）：
```python
from ppplt import is_grayscale_discriminable
is_ok = is_grayscale_discriminable("Okabe-Ito")  # True/False
```

选型建议：
- 论文主图：Modern Scientific / Okabe-Ito（色盲友好）
- 打印灰度：使用预设 ieee-gray / gb-gray（Grayscale-Safe），或确保灰度差异充分
- 强对比场景：Contrast Set 1/2

## API
- apply_style(name: str, register_font: bool = True)
- available_styles() -> list[str]
- register_fonts()

## 兼容性
- Python 3.10–3.13
- Matplotlib >= 3.5

## 打包
使用 Hatch 构建；构建时将 styles/ 与 fonts/ 放入包内。

## 许可证
MIT
