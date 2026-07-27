"""RoboCopy 执行器 — 用 QProcess 异步运行 robocopy.exe，信号推送实时输出。"""

import locale

from PySide6.QtCore import QObject, QProcess, Signal


class RoboCopyRunner(QObject):
    """封装 QProcess 调用 robocopy。"""

    log_line = Signal(str)    # 每行 stdout/stderr 实时发出
    finished = Signal(int)    # 进程结束，携带退出码

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._proc: QProcess | None = None
        # robocopy.exe 在中文 Windows 上输出为 GBK(cp936)，
        # 在英文 Windows 上为 cp1252，使用系统首选编码解码
        self._encoding = locale.getpreferredencoding(do_setlocale=False)

    # ── API ───────────────────────────────────────────────────────

    def start(self, source: str, dest: str, options: dict) -> None:
        """启动 robocopy。

        Args:
            source: 源文件夹路径
            dest: 目标文件夹路径
            options: RoboCopyOptions.to_dict() 返回的字典
        """
        if self._proc and self._proc.state() != QProcess.NotRunning:
            self.log_line.emit("[警告] 已有任务在运行，请先停止当前任务。")
            return

        args = [source, dest] + self._build_args(options)

        self._proc = QProcess(self)
        self._proc.setProgram("robocopy")
        self._proc.setArguments(args)
        self._proc.setProcessChannelMode(QProcess.MergedChannels)

        self._proc.readyReadStandardOutput.connect(self._on_ready_read)
        self._proc.finished.connect(self._on_finished)
        self._proc.errorOccurred.connect(self._on_error)

        self.log_line.emit(f"> robocopy {' '.join(args)}")
        self._proc.start()

    def stop(self) -> None:
        """终止正在运行的 robocopy。"""
        if self._proc and self._proc.state() != QProcess.NotRunning:
            self._proc.kill()
            self.log_line.emit("[已终止]")

    def is_running(self) -> bool:
        """返回是否正在执行。"""
        return self._proc is not None and self._proc.state() != QProcess.NotRunning

    # ── 内部 ───────────────────────────────────────────────────────

    def _build_args(self, options: dict) -> list[str]:
        """将选项字典转为 robocopy 命令行参数列表。"""
        args: list[str] = []

        # 复选框 → 开关
        if options.get("mirror"):
            args.append("/MIR")  # 隐含 /E + /PURGE
        elif options.get("empty_dirs"):
            args.append("/E")
        if options.get("copy_all"):
            args.append("/COPYALL")
        if options.get("restartable"):
            args.append("/Z")

        # 数字 → 参数
        threads = options.get("threads", 8)
        args.append(f"/MT:{threads}")

        retries = options.get("retries", 3)
        if retries > 0:
            args.append(f"/R:{retries}")

        wait = options.get("wait", 5)
        if wait > 0:
            args.append(f"/W:{wait}")

        # 详细日志输出
        args.append("/TEE")  # 同时输出到控制台
        args.append("/V")    # 详细模式：显示跳过的文件、额外信息
        args.append("/TS")   # 源文件时间戳
        args.append("/FP")   # 完整路径
        args.append("/ETA")  # 预计完成时间

        return args

    def _on_ready_read(self) -> None:
        """读取进程输出的新数据。"""
        if self._proc:
            data = self._proc.readAllStandardOutput()
            text = bytes(data).decode(self._encoding, errors="replace")
            for line in text.splitlines():
                stripped = line.strip()
                if stripped:
                    self.log_line.emit(stripped)

    def _on_finished(self, exit_code: int) -> None:
        """进程结束。"""
        self.log_line.emit(f"[完成] robocopy 退出码: {exit_code}")
        self.finished.emit(exit_code)

    def _on_error(self, error: QProcess.ProcessError) -> None:
        """进程启动/执行出错。"""
        msg = {
            QProcess.FailedToStart: "无法启动 robocopy.exe，请确认它已安装在 PATH 中。",
            QProcess.Crashed: "RoboCopy 进程崩溃。",
            QProcess.Timedout: "RoboCopy 进程超时。",
            QProcess.WriteError: "向 robocopy 写入时出错。",
            QProcess.ReadError: "从 robocopy 读取时出错。",
            QProcess.UnknownError: "未知错误。",
        }
        self.log_line.emit(f"[错误] {msg.get(error, str(error))}")
        # 发射 finished 信号，避免 UI 按钮永远锁死
        self.finished.emit(-1)
