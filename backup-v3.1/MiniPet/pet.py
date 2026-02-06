# -*- coding: utf-8 -*-
"""
PetAnimator - 像素宠物动画器
"""

import random
import os
from typing import List
from datetime import datetime

from PIL import Image, ImageTk

try:
    import pygame
except Exception:
    pygame = None

from assets_loader import AssetsLoader

# Debug 模式开关
DEBUG = True


def log(msg: str) -> None:
    """输出调试日志"""
    if DEBUG:
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [PetAnimator] {msg}")


class PetAnimator:
    """宠物动画器：管理帧动画与交互"""

    def __init__(self, frames_path: str, scale: float = 2.0) -> None:
        log(f"初始化: frames_path={frames_path}, scale={scale}")

        if pygame is None:
            log("ERROR: pygame 未安装!")
            raise RuntimeError("请安装 pygame: pip install pygame")

        # 检查文件是否存在
        if not os.path.exists(frames_path):
            log(f"ERROR: 文件不存在! {frames_path}")
            raise FileNotFoundError(f"宠物文件不存在: {frames_path}")

        log(f"文件大小: {os.path.getsize(frames_path)} bytes")

        # 先定义 _scale，再设置 scale（避免 setter 中访问未定义的 _scale）
        self._scale = scale  # 临时值，会被下面的 scale setter 覆盖
        self.scale = scale
        self.loader = AssetsLoader()

        log("开始加载帧数据...")
        self.raw_w, self.raw_h, frames_rgba = self.loader.load_frames(frames_path)
        log(f"帧数据加载完成: {self.raw_w}x{self.raw_h}, 共 {len(frames_rgba)} 帧")

        log("转换为 pygame Surface...")
        self.frames: List["pygame.Surface"] = self.loader.to_surfaces(frames_rgba)
        log(f"Surface 转换完成: {len(self.frames)} 个")

        self._idx = 0
        self._interact_ticks = 0

        # 预生成所有帧的 PhotoImage，保持引用防止被GC回收
        log("预生成 PhotoImage...")
        self._tk_images: List["ImageTk.PhotoImage"] = []
        self._generate_tk_images()
        log(f"PhotoImage 生成完成: {len(self._tk_images)} 个")

        log(f"初始化完成: w={self.w}, h={self.h}")

    def _generate_tk_images(self) -> None:
        """预生成所有帧的 PhotoImage"""
        log(f"生成 {len(self.frames)} 帧图片...")
        self._tk_images = []
        for i, surf in enumerate(self.frames):
            try:
                raw_str = pygame.image.tostring(surf, "RGBA", False)
                img = Image.frombytes("RGBA", (self.raw_w, self.raw_h), raw_str)

                if self.scale != 1:
                    new_w = int(self.raw_w * self.scale)
                    new_h = int(self.raw_h * self.scale)
                    img = img.resize((new_w, new_h), Image.NEAREST)

                tk_img = ImageTk.PhotoImage(img)
                self._tk_images.append(tk_img)
                log(f"  帧 {i}: {len(tk_img.__dict__.get('photo', '?'))} bytes")
            except Exception as e:
                log(f"ERROR 生成帧 {i}: {e}")

    @property
    def w(self) -> int:
        return int(self.raw_w * self.scale)

    @property
    def h(self) -> int:
        return int(self.raw_h * self.scale)

    @property
    def scale(self) -> float:
        return self._scale

    @scale.setter
    def scale(self, value: float) -> None:
        log(f"scale 设置: {self._scale} -> {value}")
        self._scale = value

    def next_frame(self) -> None:
        """下一帧"""
        if not self.frames:
            log("WARNING: 没有帧数据")
            return

        self._idx = (self._idx + 1) % len(self.frames)

    def interact(self) -> None:
        """触发互动动画"""
        self._interact_ticks = random.randint(8, 15)
        log(f"互动触发: {self._interact_ticks} ticks")

    def get_tk_image(self) -> "ImageTk.PhotoImage":
        """获取当前帧的 Tkinter 图像"""
        if not self._tk_images:
            log("WARNING: 没有预生成的图片")
            img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
            return ImageTk.PhotoImage(img)

        img = self._tk_images[self._idx]
        # log(f"获取帧 {self._idx}: {id(img)}")
        return img

    def set_scale(self, scale: float) -> None:
        """设置缩放比例并重新生成图片"""
        log(f"set_scale: {self.scale} -> {scale}")
        self.scale = scale
        log("重新生成图片...")
        self._generate_tk_images()
        log(f"完成: w={self.w}, h={self.h}")
