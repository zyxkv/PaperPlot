from ppplt import apply_style
import matplotlib.pyplot as plt

apply_style("IEEE")  # or "GB"

fig, ax = plt.subplots()
ax.plot([0, 1, 2], [0, 1, 0], label="示例 Example")
ax.set_xlabel("X 轴")
ax.set_ylabel("Y 轴")
ax.set_title("标题 Title")
ax.legend()
fig.tight_layout()
plt.show()
