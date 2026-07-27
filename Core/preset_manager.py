"""预设方案管理器 — 用 JSON 文件保存/加载 RoboCopy 配置方案。

预设文件路径：%APPDATA%/RoboCopy-GUI/presets.json（Windows）或 ~/.config/RoboCopy-GUI/presets.json（其他平台）
"""

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Optional


def _default_config_dir() -> Path:
    """返回与 robocopy-gui.py 一致的配置目录路径。"""
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
        return Path(appdata) / "RoboCopy-GUI"
    else:
        return Path.home() / ".config" / "RoboCopy-GUI"


class PresetManager:
    """管理 RoboCopy GUI 预设方案的保存、加载、列表和删除。"""

    def __init__(self) -> None:
        self._dir = _default_config_dir()
        self._file = self._dir / "presets.json"
        self._ensure_file()

    # ── 内部 ───────────────────────────────────────────────────────

    def _ensure_file(self) -> None:
        """确保预设目录与文件存在。"""
        self._dir.mkdir(parents=True, exist_ok=True)
        if not self._file.exists():
            self._file.write_text("{}", encoding="utf-8")

    def _read_all(self) -> dict:
        """读取全部预设到内存。JSON 损坏时保留原始内容并返回空字典。"""
        try:
            text = self._file.read_text(encoding="utf-8")
            return json.loads(text)
        except json.JSONDecodeError:
            # JSON 损坏 — 备份坏文件，避免静默丢失数据
            backup = self._file.with_suffix(".json.bak")
            try:
                shutil.copy2(self._file, backup)
            except OSError:
                pass
            return {}
        except OSError:
            return {}

    def _write_all(self, data: dict) -> None:
        """写入全部预设（先写临时文件再替换，防止写入中断损坏数据）。"""
        tmp = self._file.with_suffix(".json.tmp")
        try:
            tmp.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            tmp.replace(self._file)  # 原子替换（同分区）
        except OSError:
            # 写入失败时尝试清理临时文件
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass
            raise

    # ── API ───────────────────────────────────────────────────────

    def list_presets(self) -> list[str]:
        """返回所有已保存的预设名称列表（按名称排序）。"""
        return sorted(self._read_all().keys())

    def save_preset(self, name: str, data: dict) -> None:
        """保存一个预设。data 应为 {source, destination, options}。"""
        all_data = self._read_all()
        all_data[name] = data
        self._write_all(all_data)

    def load_preset(self, name: str) -> Optional[dict]:
        """加载指定预设，不存在时返回 None。"""
        return self._read_all().get(name)

    def delete_preset(self, name: str) -> bool:
        """删除指定预设，返回 True 表示成功，不存在返回 False。"""
        all_data = self._read_all()
        if name not in all_data:
            return False
        del all_data[name]
        self._write_all(all_data)
        return True
