# PaperPlot

Matplotlib 样式与工具库，助力论文与科研绘图（IEEE 与中国国标 GB 风格）。

## 特性
- 内置两种样式：IEEE、GB
- 内置字体注册：SimSun（中文）、Times New Roman（英文）
- 出版级默认参数（字号、线宽、网格、矢量字体等）
- 函数式流水线 + 可链式 (>>)：init -> set_style/preset -> draw / draw_grid -> save
- 预设 (样式 + 配色) 一键应用，含色盲友好 / 灰度安全方案
- 颜色集注册与灰度可区分性检测
- 高阶多子图/网格绘制辅助：自动列宽、标题批量、图例区域自动扩展
- 多格式一次性保存 (PNG / PDF / ...)

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

## 函数式流水线 & 链式用法

核心调用序列：

```python
from ppplt import init, set_style, draw, save
init()                      # 初始化日志/主题
set_style(preset='ieee-modern')
fig = draw(lambda f, ax: ax.plot([1,2,3]))
save('demo', formats=['png','pdf'])
```

链式 (>>)，适合脚本一气呵成：

```python
from ppplt import init_step, style_step, draw_step, save_step

( init_step(log_time=False)
	>> style_step(preset='ieee-modern')
	>> draw_step(plot_fn=lambda f,a: a.plot([1,2,3]))
	>> save_step('chain_example', formats=['png','pdf'])
).run()
```

阶段顺序由内部有限状态机 (UNINITIALIZED -> INITIALIZED -> STYLE_SET -> DRAWN -> SAVED) 保障，违规调用会抛出 `PaperPlotException`。

## 高级绘制：多子图 / 网格

`draw_grid` 为论文常见子图组合提供便捷：自动推导单/双栏宽度、按行列索引回调、批量标题、自动收集曲线生成全局图例并调整 figure 高度。

最小示例：

```python
from ppplt import init, set_style
from ppplt.draw import draw_grid, LegendConfig
import numpy as np

init(); set_style(preset='ieee-modern')
data = {'x': np.arange(20)}
data['curves'] = [data['x'], data['x']**1.2, data['x']**1.5]

def cell(ax, r, c, idx, data):
		labels = ['a','b','c'] if (r==0 and c==0) else ['_nolegend_']*3
		for y, lab in zip(data['curves'], labels):
				ax.plot(data['x'], y, label=lab)
		if r==1: ax.set_xlabel(f'x_{c+1}')
		if c==0: ax.set_ylabel(f'y_{r+1}')

fig = draw_grid(cell, grid=(2,3), legend=LegendConfig(loc='lower center'), titles=[f'({chr(97+i)})' for i in range(6)])
```

要点：
- 回调签名兼容旧版：`cell(ax, r, c, idx)` 或新增 `cell(ax, r, c, idx, data)`
- `LegendConfig` 自动估算图例占用行数并扩展 figure 高度，保证正文区域紧凑
- `col_span=1/2` 可快速切换单/双栏尺寸

## 保存与多格式输出

`save('figure', formats=['png','pdf','svg'])` 会生成 `figure.png / figure.pdf / figure.svg`。

若仅给出拓展名：`save('figure.png')` 等价于只输出该格式。内部使用最后一次 `draw / draw_grid` 的缓存 figure。

## 示例脚本

`examples/` 目录包含：

| 文件 | 说明 |
|------|------|
| `quickstart.py` | 基础使用示例 |
| `colorset_demo.py` | 配色方案列举与切换 |
| `presets_palettes_demo.py` | 预设 + 多调色板演示 |
| `matplot_subplot_demo.py` | 原生 Matplotlib 子图布局参考实现 |
| `draw_grid.py` | 使用 `draw_grid` + `LegendConfig` 的网格绘制与多格式保存 |
| `subplot.py` | 衍生子图示例 (可能用于对比/测试) |

建议结合示例快速复制结构到项目中。

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
核心：
- `init(debug=False, theme='dark', preset='ieee-modern')`
- `destroy()`
- `set_style(style=..., preset=..., register_font=True)`
- `apply_style(name, register_font=True)`
- `apply_paper_preset(name)` / `list_paper_presets()` / `get_paper_preset(name)`
- `list_color_sets()` / `get_color_set(name)` / `apply_color_set(name)`
- `is_grayscale_discriminable(colorset_name)`
- `draw(plot_fn=None, subplots=(1,1), figsize=None, tight=True)`
- `draw_grid(plot_cell, grid=(r,c), col_span=1, legend=LegendConfig(...), titles=[...], data=...)`
- `save(path_or_stem, formats=None, dpi=None)`
- `last_figure()` / `last_axes()`

链式步骤（延迟执行，用 `>>` 连接，最终 `.run()`）：
- `init_step(...)`, `style_step(...)`, `draw_step(...)`, `draw_grid_step(...)`, `save_step(...)`

数据回调约定：
- `draw` 中 `plot_fn(fig, axes, **kwargs)`
- `draw_grid` 中 `plot_cell(ax, row, col, idx [, data])`

## 兼容性
- Python 3.10–3.13
- Matplotlib >= 3.5

## 打包
使用 Hatch 构建；构建时将 styles/ 与 fonts/ 放入包内。

## 开发者提示
- 所有公共 API 尽量保持幂等或显式状态推进；状态错误会抛 `PaperPlotException`
- 颜色集与样式查找在包内或可编辑安装根目录自动解析
- `draw_grid` 的尺寸推导策略可在后续版本开放自定义策略对象
- 如需要 3D / GPU 加速，可基于注释依赖扩展 (PyOpenGL / pyglet / numba 等) 后在 `cell` 中插入已渲染图像（当前暂未内置）

## 许可证
MIT
