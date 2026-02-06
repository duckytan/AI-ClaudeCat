# -*- coding: utf-8 -*-
"""
AssetsLoader - 像素资源加载器
从 JSON 文件加载像素帧数据，转换为 pygame Surface
"""

import json
import os
from typing import Any, Dict, List, Tuple

try:
    import pygame
except Exception:
    pygame = None


class AssetsLoader:
    """资源加载器"""

    def __init__(self) -> None:
        if pygame is None:
            raise RuntimeError("请安装 pygame: pip install pygame")

    def load_frames(
        self, frames_json_path: str
    ) -> Tuple[int, int, List[List[List[Tuple[int, int, int, int]]]]]:
        """加载帧数据"""
        if not os.path.exists(frames_json_path):
            return 32, 32, [self._make_blank_frame(32, 32)]

        with open(frames_json_path, "r", encoding="utf-8") as f:
            obj: Dict[str, Any] = json.load(f)

        size = obj.get("size", [32, 32])
        w, h = int(size[0]), int(size[1])
        palette: Dict[str, List[int]] = obj.get("palette", {})
        frames_def = obj.get("frames", [])

        frames_rgba: List[List[List[Tuple[int, int, int, int]]]] = []
        for fr in frames_def:
            pixels = fr.get("pixels")
            if pixels is None:
                frames_rgba.append(self._make_blank_frame(w, h))
                continue
            frames_rgba.append(self._map_palette(pixels, palette, w, h))

        if not frames_rgba:
            frames_rgba.append(self._make_blank_frame(w, h))

        return w, h, frames_rgba

    def to_surfaces(
        self, frames_rgba: List[List[List[Tuple[int, int, int, int]]]]
    ) -> List["pygame.Surface"]:
        """转换为 pygame Surface 列表"""
        surfaces: List["pygame.Surface"] = []
        for frame in frames_rgba:
            h = len(frame)
            w = len(frame[0]) if h > 0 else 0
            surf = pygame.Surface((w, h), pygame.SRCALPHA, 32)

            for y in range(h):
                for x in range(w):
                    r, g, b, a = frame[y][x]
                    surf.set_at((x, y), (r, g, b, a))

            surfaces.append(surf)

        return surfaces

    def _make_blank_frame(
        self, w: int, h: int
    ) -> List[List[Tuple[int, int, int, int]]]:
        """生成透明占位帧"""
        row = [(0, 0, 0, 0)] * w
        return [list(row) for _ in range(h)]

    def _map_palette(
        self,
        pixels: List[List[str]],
        palette: Dict[str, List[int]],
        w_expected: int,
        h_expected: int,
    ) -> List[List[Tuple[int, int, int, int]]]:
        """将像素名称映射为 RGBA 值"""
        rgba_frame: List[List[Tuple[int, int, int, int]]] = []

        for y in range(h_expected):
            row_rgba: List[Tuple[int, int, int, int]] = []
            src_row = pixels[y] if y < len(pixels) else []

            for x in range(w_expected):
                name = src_row[x] if x < len(src_row) else "bg"
                rgba = palette.get(name, [0, 0, 0, 0])
                r, g, b, a = int(rgba[0]), int(rgba[1]), int(rgba[2]), int(rgba[3])
                row_rgba.append((r, g, b, a))

            rgba_frame.append(row_rgba)

        return rgba_frame
