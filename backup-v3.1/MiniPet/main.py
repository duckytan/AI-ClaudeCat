# -*- coding: utf-8 -*-
"""
MiniPet - 轻量级桌面像素宠物
"""

import json
import os
import sys
import tkinter as tk
from pathlib import Path
from datetime import datetime

# Debug 模式开关
DEBUG = True


def log(msg: str) -> None:
    """输出调试日志"""
    if DEBUG:
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {msg}")


try:
    import win32con
    import win32gui
except Exception:
    win32con = None
    win32gui = None

from pet import PetAnimator


class MiniPet:
    """桌面像素宠物"""

    CONFIG_PATH = "config.json"
    MIN_SCALE = 0.5
    MAX_SCALE = 4.0

    def __init__(self) -> None:
        log("=== MiniPet 启动 ===")

        self.root = tk.Tk()
        self.root.withdraw()

        # 1. 加载配置
        log("开始加载配置...")
        self.config = self._load_config()
        log(f"配置加载完成: {self.config}")

        self.current_pet = self.config.get("current_pet", "pixel_dog")
        self.scale = self.config.get("scale", 2.0)
        self.pets_dir = Path(__file__).parent / "pets"

        log(f"当前宠物: {self.current_pet}")
        log(f"缩放比例: {self.scale}x")
        log(f"宠物目录: {self.pets_dir}")

        # 2. 创建悬浮窗
        log("创建悬浮窗...")
        self.top = tk.Toplevel(self.root)
        self.top.overrideredirect(True)
        self.top.attributes("-topmost", True)

        # 3. 透明背景设置
        log("设置透明背景...")
        self._setup_transparency()

        # 4. 初始化宠物动画
        log(f"加载宠物: {self.current_pet}...")
        self.pet_path = self.pets_dir / f"{self.current_pet}.json"
        log(f"宠物文件路径: {self.pet_path}")

        if not self.pet_path.exists():
            log(f"ERROR: 宠物文件不存在! {self.pet_path}")
            self.current_pet = None
            self.animator = None
        else:
            self.animator = PetAnimator(str(self.pet_path), scale=self.scale)
            log(f"宠物加载成功: {self.animator.w}x{self.animator.h} 像素")

        # 5. 创建画布
        if self.animator:
            w, h = self.animator.w, self.animator.h
        else:
            w, h = 64, 64
        log(f"创建画布: {w}x{h}")
        self.canvas = tk.Canvas(
            self.top,
            width=w,
            height=h,
            highlightthickness=0,
            bg=self.bg_color,
        )
        self.canvas.pack()

        # 拖拽状态
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._win_start_x = 0
        self._win_start_y = 0
        self._is_dragging = False

        # 绑定事件
        log("绑定鼠标事件...")
        self._bind_events()

        # 初始位置（屏幕右下角）
        log("设置初始位置...")
        self._move_to_corner()

        # 开始动画
        log("启动动画循环...")
        self._tick()

        log("=== MiniPet 启动完成 ===")
        print()
        print(f"MiniPet 已启动，当前宠物: {self.current_pet}，放大倍数: {self.scale}x")
        print("操作说明：")
        print("  - 拖拽宠物移动位置")
        print("  - 鼠标滚轮 调整大小（每次0.1）")
        print("  - 右键菜单切换宠物")
        print("  - 双击宠物切换到下一个宠物")
        print("  - 右键点击空白处退出")
        print()
        print("Debug 模式已开启，查看详细日志...")

        self.root.mainloop()

    def _load_config(self) -> dict:
        """加载配置"""
        log(f"检查配置文件: {self.CONFIG_PATH}")
        if os.path.exists(self.CONFIG_PATH):
            log("配置文件存在，正在读取...")
            with open(self.CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            log(f"配置读取成功: {data}")
            return data
        log("配置文件不存在，使用默认配置")
        return {"current_pet": "pixel_dog", "scale": 2.0}

    def _save_config(self) -> None:
        """保存配置"""
        log(f"保存配置: {self.config}")
        with open(self.CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
        log("配置保存成功")

    def _setup_transparency(self) -> None:
        """设置透明背景"""
        self.bg_color = "#00FEFE"
        log(f"透明色: {self.bg_color}")
        try:
            self.top.wm_attributes("-transparentcolor", self.bg_color)
            log("使用透明色模式")
        except Exception as e:
            log(f"透明色模式失败，使用Alpha模式: {e}")
            self.top.attributes("-alpha", 0.95)
            self.bg_color = "#000000"
        self.top.configure(bg=self.bg_color)

    def _bind_events(self) -> None:
        """绑定鼠标事件"""
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Double-Button-1>", self._next_pet)
        self.canvas.bind("<Button-3>", self._show_menu)
        self.top.bind("<Button-3>", self._show_menu)
        # 鼠标滚轮调整大小
        self.canvas.bind("<MouseWheel>", self._on_wheel)
        self.top.bind("<MouseWheel>", self._on_wheel)
        log("事件绑定完成")

    def _on_wheel(self, event: tk.Event) -> None:
        """鼠标滚轮调整放大倍数（每次0.1，范围0.5-4x）"""
        log(f"滚轮事件: delta={event.delta}")
        log(f"当前缩放: {self.scale}x")

        if event.delta > 0:
            # 向上滚，放大
            if self.scale < self.MAX_SCALE:
                self.scale = round(self.scale + 0.1, 1)
                log(f"放大 -> {self.scale}x")
            else:
                log(f"已达到最大缩放: {self.MAX_SCALE}x")
        else:
            # 向下滚，缩小
            if self.scale > self.MIN_SCALE:
                self.scale = round(self.scale - 0.1, 1)
                log(f"缩小 -> {self.scale}x")
            else:
                log(f"已达到最小缩放: {self.MIN_SCALE}x")

        # 保存配置
        self.config["scale"] = self.scale
        self._save_config()

        # 调整宠物大小
        log(f"调用 set_scale({self.scale})...")
        self._reload_pet()

    def _reload_pet(self) -> None:
        """调整当前宠物大小"""
        if not self.animator:
            log("ERROR: animator 为空!")
            return

        log(
            f"调整前: animator.scale={self.animator.scale}, w={self.animator.w}, h={self.animator.h}"
        )
        self.animator.set_scale(self.scale)
        log(
            f"调整后: animator.scale={self.animator.scale}, w={self.animator.w}, h={self.animator.h}"
        )

        w, h = self.animator.w, self.animator.h
        log(f"更新画布大小: {w}x{h}")
        self.canvas.configure(width=w, height=h)
        self._tick()
        log("大小调整完成")

    def _move_to_corner(self) -> None:
        """移动到屏幕右下角"""
        try:
            screen_w = self.top.winfo_screenwidth()
            screen_h = self.top.winfo_screenheight()

            if not self.animator:
                log("ERROR: animator 为空，无法计算位置")
                return

            w, h = self.animator.w, self.animator.h
            margin_right = 50
            margin_bottom = 80
            x = screen_w - w - margin_right
            y = screen_h - h - margin_bottom
            x, y = max(0, x), max(0, y)

            log(f"屏幕尺寸: {screen_w}x{screen_h}")
            log(f"宠物尺寸: {w}x{h}")
            log(f"窗口位置: +{x}+{y}")

            self.top.geometry(f"+{x}+{y}")
        except Exception as e:
            log(f"设置窗口位置失败: {e}")

    def _on_press(self, event: tk.Event) -> None:
        """拖拽起点"""
        log(f"鼠标按下: ({event.x_root}, {event.y_root})")
        self._is_dragging = False
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root
        self._win_start_x = self.top.winfo_x()
        self._win_start_y = self.top.winfo_y()

    def _on_drag(self, event: tk.Event) -> None:
        """拖拽移动"""
        dx = event.x_root - self._drag_start_x
        dy = event.y_root - self._drag_start_y

        if not self._is_dragging:
            if abs(dx) > 3 or abs(dy) > 3:
                self._is_dragging = True
                log("开始拖拽")

        if self._is_dragging:
            new_x = self._win_start_x + dx
            new_y = self._win_start_y + dy
            self.top.geometry(f"+{new_x}+{new_y}")

    def _on_release(self, event: tk.Event) -> None:
        """拖拽结束"""
        if not self._is_dragging:
            log("点击事件，触发互动")
            self._interact()
        else:
            log("拖拽结束")
        self._is_dragging = False

    def _interact(self) -> None:
        """点击互动"""
        if self.animator:
            self.animator.interact()
            log("互动触发")
        else:
            log("ERROR: animator 为空，无法互动")

    def _next_pet(self, event: tk.Event = None) -> None:
        """切换到下一个宠物"""
        pets = self._get_available_pets()
        if not pets:
            log("没有可用宠物")
            return

        current_idx = pets.index(self.current_pet) if self.current_pet in pets else 0
        next_idx = (current_idx + 1) % len(pets)
        next_pet = pets[next_idx]
        log(f"切换宠物: {self.current_pet} -> {next_pet}")
        self._switch_pet(next_pet)

    def _get_available_pets(self) -> list:
        """获取可用宠物列表"""
        pets = []
        if self.pets_dir.exists():
            for f in self.pets_dir.glob("*.json"):
                pets.append(f.stem)
        log(f"可用宠物: {pets}")
        return pets

    def _switch_pet(self, pet_name: str) -> None:
        """切换宠物"""
        log(f"开始切换到宠物: {pet_name}")

        self.current_pet = pet_name
        self.config["current_pet"] = pet_name
        self._save_config()

        pet_path = self.pets_dir / f"{pet_name}.json"
        log(f"宠物文件路径: {pet_path}")

        if not pet_path.exists():
            log(f"ERROR: 宠物文件不存在! {pet_path}")
            return

        self.animator = PetAnimator(str(pet_path), scale=self.scale)
        log(f"宠物加载成功: {self.animator.w}x{self.animator.h} 像素")

        self.canvas.configure(width=self.animator.w, height=self.animator.h)
        self._tick()

        log(f"切换完成: {pet_name}")

    def _show_menu(self, event: tk.Event) -> None:
        """显示右键菜单"""
        log(f"显示菜单 at ({event.x_root}, {event.y_root})")

        pets = self._get_available_pets()
        if not pets:
            log("没有可用宠物")
            return

        menu = tk.Menu(self.top, tearoff=0, bg="#333", fg="white")
        menu.add_command(label="切换宠物", state="disabled")

        for pet in pets:
            display_name = pet.replace("pixel_", "").replace("_", " ").title()
            if pet == self.current_pet:
                menu.add_command(
                    label=f"[x] {display_name}",
                    command=lambda p=pet: self._switch_pet(p),
                )
            else:
                menu.add_command(
                    label=f"[ ] {display_name}",
                    command=lambda p=pet: self._switch_pet(p),
                )

        menu.add_separator()
        menu.add_command(label=f"当前大小: {self.scale}x", state="disabled")
        menu.add_separator()
        menu.add_command(label="退出", command=self._quit)

        try:
            menu.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            log(f"菜单显示失败: {e}")

    def _quit(self) -> None:
        """退出程序"""
        log("用户请求退出")
        print("\n再见！")
        self.root.quit()

    def _tick(self) -> None:
        """动画帧更新"""
        if not self.animator:
            log("ERROR: animator 为空，停止动画")
            return

        self.animator.next_frame()
        self.photo = self.animator.get_tk_image()
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.photo, anchor="nw")
        self.top.after(120, self._tick)


def main() -> None:
    """入口"""
    # Windows 高 DPI 适配
    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(1)
    except Exception as e:
        log(f"DPI 适配失败: {e}")

    app = MiniPet()


if __name__ == "__main__":
    main()
