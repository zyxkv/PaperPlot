from ppplt import apply_style, apply_color_set
import matplotlib.pyplot as plt

# Choose a style and a color set
apply_style("IEEE")
apply_color_set("Modern Scientific")

x = [0, 1, 2, 3, 4]
y_sets = [
    [0, 1, 0, 1, 0],
    [0, 0.5, 1.2, 0.8, 0.4],
    [0.1, 0.9, 0.7, 1.1, 0.2],
]

fig, axs = plt.subplots(1, 3, figsize=(6.5, 2.2))
for i, ax in enumerate(axs):
    for j, ys in enumerate(y_sets):
        ax.plot(x, [v + 0.1 * j for v in ys], label=f"Line {j+1}")
    ax.set_title(f"Subplot {i+1}")
    if i == 0:
        ax.set_ylabel("Value")
    ax.set_xlabel("X")

handles, labels = axs[-1].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", ncol=len(y_sets), bbox_to_anchor=(0.5, 0.98))
# Reserve space at the top for the figure legend to avoid clipping
fig.tight_layout(rect=(0, 0, 1, 0.9))
plt.show()
