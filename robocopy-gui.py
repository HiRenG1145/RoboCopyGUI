"""RoboCopy GUI — 应用入口，负责日志配置与启动。"""

import os
import sys
from pathlib import Path

# ── 必须在 import Qt 之前：抑制字体数据库调试刷屏 ─────────────────
# 这些消息是 HarfBuzz 在检查每种字体的 OpenType 脚本表，属于 dbg 诊断信息
os.environ.setdefault("QT_LOGGING_RULES", "qt.text.font.db=false")

# ── Windows 控制台中文输出编码修复 ────────────────────────────────
# 确保 sys.stderr 以 UTF-8 模式写入，避免中文乱码
if sys.platform == "win32":
    # 让 Python 内部 I/O 使用 UTF-8（PEP 540）
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from loguru import logger

# ── 日志配置 ───────────────────────────────────────────────────────
# 移除默认 handler
logger.remove()

# 控制台输出（彩色）
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="DEBUG",
    colorize=True,
)

# 文件输出（保留最近 7 天）
if sys.platform == "win32":
    log_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "RoboCopy-GUI"
else:
    log_dir = Path.home() / ".config" / "RoboCopy-GUI"
log_dir.mkdir(parents=True, exist_ok=True)
logger.add(
    log_dir / "robocopy-gui.log",
    rotation="1 MB",
    retention="7 days",
    encoding="utf-8",
    level="DEBUG",
)

logger.info("RoboCopy GUI 启动中...")


# ── 启动 ───────────────────────────────────────────────────────────
def main() -> None:
    """日志已配置完毕，启动应用。"""
    import main

    main.main()


if __name__ == "__main__":
    main()
