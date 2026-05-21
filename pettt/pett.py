#!/usr/bin/env python3
# encoding: utf-8

import sys
import os
import math
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QWidget,
    QSystemTrayIcon, QMenu
)
from PySide6.QtGui import (
    QPainter, QPixmap, QTransform,
    QAction, QIcon
)
from PySide6.QtCore import Qt, QTimer, QPoint


class DesktopPet(QWidget):
    def __init__(self, image_root):
        super().__init__()

        # ===== 窗口属性 =====
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # ===== 基本参数 =====
        self.pet_size = 64
        self.resize(self.pet_size, self.pet_size)

        # ===== 状态 =====
        self.state = "FOLLOWING"   # FOLLOWING / DRAGGING / RETURNING
        self.drag_offset = QPoint()
        self.angle = 0

        # ===== 加载动画 =====
        self.animations = {
            "FOLLOWING": self.load_animation(os.path.join(image_root, "follow")),
            "DRAGGING":  self.load_animation(os.path.join(image_root, "drag")),
            "RETURNING": self.load_animation(os.path.join(image_root, "return")),
        }

        if not self.animations["FOLLOWING"]:
            raise RuntimeError("follow 动画不能为空")

        self.current_frames = self.animations["FOLLOWING"]
        self.frame_index = 0

        # ===== 定时器 =====
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_pet)
        self.timer.start(80)

        # ===== 托盘 =====
        self.init_tray()

        self.show()

    # ---------- 动画加载 ----------
    def load_animation(self, folder):
        frames = []
        if not os.path.exists(folder):
            return frames

        files = sorted(
            f for f in os.listdir(folder)
            if f.lower().endswith(".png")
        )
        for f in files:
            frames.append(QPixmap(os.path.join(folder, f)))
        return frames

    # ---------- 状态切换 ----------
    def set_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            frames = self.animations.get(new_state)
            if frames:
                self.current_frames = frames
            else:
                self.current_frames = self.animations["FOLLOWING"]
            self.frame_index = 0

    # ---------- 托盘 ----------
    def init_tray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon(self.animations["FOLLOWING"][0]))
        self.tray.setToolTip("桌宠")

        menu = QMenu()
        exit_action = QAction("退出桌宠", self)
        exit_action.triggered.connect(QApplication.quit)
        menu.addAction(exit_action)

        self.tray.setContextMenu(menu)
        self.tray.show()

    # ---------- 巡航路径 ----------
    def get_target_pos(self):
        now = datetime.now()
        seconds = now.hour * 3600 + now.minute * 60 + now.second
        ratio = seconds / 86400

        screen = QApplication.primaryScreen().geometry()
        sw, sh = screen.width(), screen.height()

        total = 2 * (sw + sh)
        offset = total * 0.5 - sw / 2
        dist = (ratio * total - offset) % total

        if dist < sw:
            return dist, 0, 0
        if dist < sw + sh:
            return sw - self.pet_size, dist - sw, 270
        if dist < 2 * sw + sh:
            return sw - (dist - sw - sh), sh - self.pet_size, 180
        return 0, sh - (dist - 2 * sw - sh), 90

    # ---------- 更新逻辑 ----------
    def update_pet(self):
        tx, ty, ta = self.get_target_pos()
        cx, cy = self.x(), self.y()

        if self.state == "DRAGGING":
            pass

        elif self.state == "RETURNING":
            dx = tx - cx
            dy = ty - cy
            dist = math.hypot(dx, dy)

            if dist < 6:
                self.set_state("FOLLOWING")
            else:
                speed = 10
                self.move(
                    cx + int(dx / dist * speed),
                    cy + int(dy / dist * speed)
                )
                self.angle = math.degrees(math.atan2(-dy, dx))

        else:  # FOLLOWING
            self.move(int(tx), int(ty))
            self.angle = ta

        # 动画帧
        self.frame_index = (
            self.frame_index + 1
        ) % len(self.current_frames)

        self.update()

    # ---------- 绘制 ----------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        pix = self.current_frames[self.frame_index]

        transform = QTransform()
        transform.translate(self.pet_size / 2, self.pet_size / 2)
        transform.rotate(self.angle)
        transform.translate(-self.pet_size / 2, -self.pet_size / 2)

        painter.setTransform(transform)
        painter.drawPixmap(0, 0, self.pet_size, self.pet_size, pix)

    # ---------- 鼠标事件 ----------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_offset = (
                event.globalPosition().toPoint() - self.pos()
            )
            self.set_state("DRAGGING")

    def mouseMoveEvent(self, event):
        if self.state == "DRAGGING":
            self.move(
                event.globalPosition().toPoint() - self.drag_offset
            )

    def mouseReleaseEvent(self, event):
        if self.state == "DRAGGING":
            self.set_state("RETURNING")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    if not os.path.exists("pet_images"):
        print("缺少 pet_images 文件夹")
        sys.exit(0)

    pet = DesktopPet("pet_images")
    sys.exit(app.exec())
