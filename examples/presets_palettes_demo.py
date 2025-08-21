from ppplt import (
    apply_paper_preset,
    apply_color_set,
    is_grayscale_discriminable,
)
import matplotlib.pyplot as plt

# 1) 一键预设：IEEE 样式 + Modern Scientific 配色
apply_paper_preset("ieee-gray")
# ieee-modern,ieee-contrast1,ieee-okabe,ieee-gray
# gb-modern,gb-contrast2,gb-okabe

# 2) 展示多套配色（含色盲友好与灰度安全）
color_sets = [
    "Modern Scientific",
    "Okabe-Ito",  # 色盲友好
    "Brewer-Qual-Soft",  # Brewer 定性组合（较友好）
    "Grayscale-Safe",  # 灰度安全（打印/复印友好）
]

x = [0, 1, 2, 3, 4]
y_sets = [
    [0.0, 0.8, 1.0, 0.6, 0.2],
    [0.1, 0.9, 1.1, 0.7, 0.3],
    [0.2, 1.0, 1.2, 0.8, 0.4],
]

fig, axs = plt.subplots(2, 2, figsize=(6.8, 4.0))
axs = axs.ravel()

for i, (ax, cs_name) in enumerate(zip(axs, color_sets)):
    # 为当前子图应用配色（全局设置亦可，示例中按子图依次设置）
    apply_color_set(cs_name)
    for j, ys in enumerate(y_sets):
        ax.plot(x, [v + 0.1 * j for v in ys], label=f"Series {j+1}")
    gray_ok = is_grayscale_discriminable(cs_name)
    ok_text = "Gray OK" if gray_ok else "Gray ?"
    ax.set_title(f"{cs_name} ({ok_text})")
    if i % 2 == 0:
        ax.set_ylabel("Value")
    ax.set_xlabel("X")

# 汇总图例放到下方居中，并预留空间避免截断
handles, labels = axs[-1].get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", ncol=len(y_sets), bbox_to_anchor=(0.5, -0.01))
fig.suptitle("Presets & Palettes Demo (IEEE + Multiple Color Sets)", y=0.98)
# 为顶部标题与底部图例预留空间
fig.tight_layout(rect=(0.0, 0.08, 1.0, 0.92))
plt.show()
