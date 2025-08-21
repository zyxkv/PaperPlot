"""
paper_plot (ppplt)

Matplotlib 样式与小工具，帮助生成符合论文规范（IEEE 与中国国标 GB）的出版级图表。

主要功能：
- 注册并应用内置字体（中文：SimSun；英文：Times New Roman）
- 一键应用内置样式："IEEE" 与 "GB"
"""
from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Iterable, List, Optional


def _pkg_dir() -> Path:
	# 包内目录（构建后的正式安装环境）
	return Path(__file__).resolve().parent


def _repo_root_fallback() -> Optional[Path]:
	# 可编辑安装或直接在仓库根运行时，styles/ 与 fonts/ 位于项目根目录
	p = _pkg_dir().parent  # project root if running from source layout
	# 兼容：当 ppplt 在项目根/ppplt 下时，p 即仓库根
	if (p / "styles").exists() or (p / "fonts").exists():
		return p
	return None


def styles_dir() -> Path:
	pkg = _pkg_dir() / "styles"
	if pkg.exists():
		return pkg
	repo = _repo_root_fallback()
	if repo and (repo / "styles").exists():
		return repo / "styles"
	return pkg  # 默认返回包内路径（即使不存在）


def fonts_dir() -> Path:
	pkg = _pkg_dir() / "fonts"
	if pkg.exists():
		return pkg
	repo = _repo_root_fallback()
	if repo and (repo / "fonts").exists():
		return repo / "fonts"
	return pkg


def available_styles() -> List[str]:
	d = styles_dir()
	if not d.exists():
		return []
	return [p.stem for p in d.glob("*.mplstyle")]


def register_fonts() -> None:
	"""将内置字体目录加入 Matplotlib 的字体搜索路径，并刷新字体缓存。

	内置字体：
	- SimSun (SimsunExtG.ttf)
	- Times New Roman (times.ttf)
	以及可选的 Nerd Font CN（MapleMono-NF-CN-Regular.ttf）
	"""
	import matplotlib
	from matplotlib import font_manager as fm

	fdir = fonts_dir()
	if not fdir.exists():
		return
	# 将目录加入 Matplotlib 字体路径并重建缓存
	fm.fontManager.addfont(str(fdir / "SimsunExtG.ttf")) if (fdir / "SimsunExtG.ttf").exists() else None
	fm.fontManager.addfont(str(fdir / "times.ttf")) if (fdir / "times.ttf").exists() else None
	# 可选开发用字体
	opt_font = fdir / "MapleMono-NF-CN-Regular.ttf"
	if opt_font.exists():
		fm.fontManager.addfont(str(opt_font))

	# 刷新缓存
	try:
		fm._load_fontmanager(try_read_cache=False)  # type: ignore[attr-defined]
	except Exception:
		# 兼容不同 Matplotlib 版本
		fm.fontManager.refresh_fonts()


def apply_style(name: str, *, register_font: bool = True) -> None:
	"""应用指定样式（"IEEE" 或 "GB"）。

	参数：
	- name: 样式名（不区分大小写），对应 styles 目录下的 .mplstyle 文件名
	- register_font: 在应用样式前是否注册内置字体
	"""
	import matplotlib as mpl
	from matplotlib import pyplot as plt

	if register_font:
		register_fonts()

	target = (styles_dir() / f"{name.upper()}.mplstyle")
	if not target.exists():
		raise ValueError(f"Style '{name}' not found. Available: {available_styles()}")

	mpl.style.use(str(target))


# Re-export color set utilities
from .colorset import list_color_sets, get_color_set, apply_color_set
from .presets import list_paper_presets, get_paper_preset, apply_paper_preset
from .colorset import is_grayscale_discriminable

__all__ = [
	"apply_style",
	"available_styles",
	"register_fonts",
	"styles_dir",
	"fonts_dir",
	"list_color_sets",
	"get_color_set",
	"apply_color_set",
	# presets
	"list_paper_presets",
	"get_paper_preset",
	"apply_paper_preset",
	# utility
	"is_grayscale_discriminable",
]

