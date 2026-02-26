from __future__ import annotations

import os
import subprocess
import webbrowser
from pathlib import Path

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtGui import QAction, QCursor, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QStyle,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .config import AppConfig, get_config_path, load_config, save_config
from .hotkey import GlobalHotkeyListener, parse_hotkey
from .qr_decode import decode_qr_from_qimage
from .safety import analyze_url
from .snip_overlay import SnipOverlay
from .win_integration import is_hotkey_helper_running, signal_hotkey_helper_reload


class DecodeThread(QThread):
    decoded = Signal(object)
    failed = Signal(str)

    def __init__(self, image, parent=None) -> None:
        super().__init__(parent)
        self._image = image.copy()

    def run(self) -> None:
        try:
            result = decode_qr_from_qimage(self._image)
        except Exception as exc:  # pragma: no cover - defensive error boundary
            self.failed.emit(str(exc))
            return
        self.decoded.emit(result)


class MainWindow(QMainWindow):
    def __init__(
        self,
        start_in_snip_mode: bool = False,
        tray_enabled: bool = True,
        hotkey_override: str | None = None,
        disable_hotkey: bool = False,
    ) -> None:
        super().__init__()
        self.setWindowTitle("QR Screen Reader")
        self.resize(760, 580)

        self.config = load_config()
        self._overlay: SnipOverlay | None = None
        self._tray_enabled = tray_enabled
        self._cli_hotkey_override = hotkey_override
        self._cli_disable_hotkey = disable_hotkey
        self._helper_running = is_hotkey_helper_running()
        self._decode_thread: DecodeThread | None = None

        self.hotkey_listener = GlobalHotkeyListener(self._effective_hotkey())
        self.hotkey_listener.triggered.connect(self.start_snip_from_hotkey)
        self.hotkey_listener.registration_failed.connect(self._show_hotkey_registration_error)

        self._build_ui()
        self._bind_values_from_config()
        self._build_tray_if_enabled()
        self._apply_hotkey_settings(show_errors=False)
        if self._helper_running:
            self.scan_notes.setPlainText(
                "Native hotkey helper is running. Global hotkey is handled by helper process."
            )

        if start_in_snip_mode:
            self.start_snip()

    def closeEvent(self, event) -> None:
        if self._tray_enabled and self.tray_icon and self.tray_icon.isVisible():
            self.hide()
            event.ignore()
            return
        self.hotkey_listener.stop()
        super().closeEvent(event)

    def _build_ui(self) -> None:
        container = QWidget()
        layout = QVBoxLayout(container)

        title = QLabel("Scan QR codes from your screen")
        title.setStyleSheet("font-size: 20px; font-weight: 600;")
        layout.addWidget(title)

        action_row = QHBoxLayout()
        self.snip_btn = QPushButton("Snip QR")
        self.snip_btn.clicked.connect(self.start_snip)
        action_row.addWidget(self.snip_btn)

        self.decode_file_btn = QPushButton("Decode Image File")
        self.decode_file_btn.clicked.connect(self.decode_from_file)
        action_row.addWidget(self.decode_file_btn)
        layout.addLayout(action_row)

        result_box = QGroupBox("Last Scan")
        result_layout = QVBoxLayout(result_box)
        self.url_field = QLineEdit()
        self.url_field.setReadOnly(True)
        self.url_field.setPlaceholderText("Decoded QR content appears here")
        result_layout.addWidget(self.url_field)

        self.scan_notes = QTextEdit()
        self.scan_notes.setReadOnly(True)
        self.scan_notes.setFixedHeight(110)
        result_layout.addWidget(self.scan_notes)

        self.decode_progress = QProgressBar()
        self.decode_progress.setRange(0, 0)
        self.decode_progress.setVisible(False)
        result_layout.addWidget(self.decode_progress)

        result_actions = QHBoxLayout()
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.clicked.connect(self.copy_current_link)
        result_actions.addWidget(self.copy_btn)

        self.open_btn = QPushButton("Open")
        self.open_btn.clicked.connect(self.open_current_link)
        result_actions.addWidget(self.open_btn)

        layout.addWidget(result_box)
        result_layout.addLayout(result_actions)

        cfg_box = QGroupBox("Behavior")
        cfg_form = QFormLayout(cfg_box)

        self.auto_copy_chk = QCheckBox("Auto-copy decoded link")
        cfg_form.addRow(self.auto_copy_chk)

        self.auto_open_chk = QCheckBox("Auto-open decoded link")
        cfg_form.addRow(self.auto_open_chk)

        self.safety_chk = QCheckBox("Enable link safety checks")
        self.safety_chk.setToolTip("Disabling this can open unsafe links without warning.")
        cfg_form.addRow(self.safety_chk)

        self.hotkey_enabled_chk = QCheckBox("Enable global hotkey")
        cfg_form.addRow(self.hotkey_enabled_chk)

        self.hotkey_field = QLineEdit()
        self.hotkey_field.setPlaceholderText("Win+Shift+Q")
        cfg_form.addRow("Global hotkey", self.hotkey_field)

        self.browser_mode = QComboBox()
        self.browser_mode.addItems(["system", "custom"])
        self.browser_mode.currentTextChanged.connect(self._refresh_browser_inputs)
        cfg_form.addRow("Browser mode", self.browser_mode)

        browser_picker_row = QHBoxLayout()
        self.browser_path = QLineEdit()
        self.browser_path.setPlaceholderText("Path to browser executable")
        browser_picker_row.addWidget(self.browser_path)

        pick_browser_btn = QPushButton("Browse")
        pick_browser_btn.clicked.connect(self.pick_browser)
        browser_picker_row.addWidget(pick_browser_btn)

        browser_picker_wrap = QWidget()
        browser_picker_wrap.setLayout(browser_picker_row)
        cfg_form.addRow("Custom browser", browser_picker_wrap)

        self.save_cfg_btn = QPushButton("Save Settings")
        self.save_cfg_btn.clicked.connect(self.save_settings)
        cfg_form.addRow(self.save_cfg_btn)

        config_path_label = QLabel(f"Config file: {get_config_path()}")
        config_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        cfg_form.addRow(config_path_label)

        layout.addWidget(cfg_box)
        self.setCentralWidget(container)

    def _build_tray_if_enabled(self) -> None:
        self.tray_icon: QSystemTrayIcon | None = None
        if not self._tray_enabled:
            return

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.tray_icon.setToolTip("QR Screen Reader")

        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show_and_raise)

        snip_action = QAction("Snip QR", self)
        snip_action.triggered.connect(self.start_snip_from_hotkey)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.exit_app)

        from PySide6.QtWidgets import QMenu

        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(snip_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)

        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_and_raise()

    def _bind_values_from_config(self) -> None:
        self.auto_copy_chk.setChecked(self.config.auto_copy_link)
        self.auto_open_chk.setChecked(self.config.auto_open_url)
        self.safety_chk.setChecked(self.config.safety_checks_enabled)
        self.hotkey_enabled_chk.setChecked(self.config.hotkey_enabled)
        self.hotkey_field.setText(self._effective_hotkey())
        self.browser_mode.setCurrentText(self.config.browser_mode)
        self.browser_path.setText(self.config.custom_browser_path)
        self._refresh_browser_inputs()

        if self._cli_disable_hotkey:
            self.hotkey_enabled_chk.setChecked(False)
            self.hotkey_enabled_chk.setEnabled(False)
            self.hotkey_field.setEnabled(False)

        self._refresh_snip_button_text()

    def _refresh_browser_inputs(self) -> None:
        custom_enabled = self.browser_mode.currentText() == "custom"
        self.browser_path.setEnabled(custom_enabled)

    def _effective_hotkey(self) -> str:
        return self._cli_hotkey_override or self.config.hotkey

    def _refresh_snip_button_text(self) -> None:
        hotkey = self.hotkey_field.text().strip() or "Win+Shift+Q"
        self.snip_btn.setText(f"Snip QR ({hotkey})")

    def _apply_hotkey_settings(self, show_errors: bool) -> None:
        self.hotkey_listener.stop()

        if self._cli_disable_hotkey:
            return
        if self._helper_running:
            return

        if not self.hotkey_enabled_chk.isChecked():
            return

        selected_hotkey = self.hotkey_field.text().strip()
        self.hotkey_listener.set_hotkey(selected_hotkey)
        self.hotkey_listener.start()

        if show_errors:
            self.scan_notes.setPlainText(f"Global hotkey set to {selected_hotkey}.")

    def _show_hotkey_registration_error(self, message: str) -> None:
        self.scan_notes.setPlainText(message)
        QMessageBox.warning(self, "Hotkey Registration", message)

    def show_and_raise(self) -> None:
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def start_snip_from_hotkey(self) -> None:
        self.start_snip(hotkey_triggered=True)

    def start_snip(self, hotkey_triggered: bool = False) -> None:
        del hotkey_triggered  # Behavior is now consistent for button, tray, and hotkey launch.
        if self._decode_thread and self._decode_thread.isRunning():
            self.scan_notes.setPlainText("Please wait for current decode to finish.")
            return
        self.hide()

        QApplication.processEvents()
        screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
        if not screen:
            QMessageBox.critical(self, "Screen Error", "Unable to access display.")
            return

        screen_geometry = screen.geometry()
        screenshot = screen.grabWindow(
            0,
            screen_geometry.x(),
            screen_geometry.y(),
            screen_geometry.width(),
            screen_geometry.height(),
        )
        if screenshot.isNull():
            self.show_and_raise()
            self.scan_notes.setPlainText("Unable to capture the selected display.")
            QMessageBox.warning(self, "Screen Error", "Unable to capture the selected display.")
            return

        self._overlay = SnipOverlay(screenshot, screen_geometry)
        self._overlay.snip_captured.connect(self.handle_snip_image)
        self._overlay.snip_cancelled.connect(self.handle_snip_cancel)
        self._overlay.show()
        self._overlay.raise_()
        self._overlay.activateWindow()

    def handle_snip_cancel(self) -> None:
        self.scan_notes.setPlainText("Snip cancelled.")
        self.show_and_raise()

    def handle_snip_image(self, image) -> None:
        self.show_and_raise()
        self.scan_notes.setPlainText("Snip captured. Decoding QR...")
        self._set_decode_busy(True)
        self._decode_thread = DecodeThread(image, self)
        self._decode_thread.decoded.connect(self._on_decode_finished)
        self._decode_thread.failed.connect(self._on_decode_failed)
        self._decode_thread.finished.connect(self._on_decode_thread_finished)
        self._decode_thread.start()

    def _on_decode_finished(self, decoded: str | None) -> None:
        self._set_decode_busy(False)
        if not decoded:
            self.url_field.clear()
            self.scan_notes.setPlainText("No QR code could be detected in the selected area.")
            return

        self.url_field.setText(decoded)

        safety_notes = []
        safe_to_open = True
        if self.safety_chk.isChecked():
            result = analyze_url(decoded)
            if not result.is_safe:
                safe_to_open = False
                safety_notes.extend(result.warnings)

        if safety_notes:
            note_text = "Potential risks found:\n- " + "\n- ".join(safety_notes)
            self.scan_notes.setPlainText(note_text)
        else:
            self.scan_notes.setPlainText("Link checks passed.")

        if self.auto_copy_chk.isChecked():
            self.copy_current_link()

        if self.auto_open_chk.isChecked():
            if safe_to_open:
                self.open_current_link()
            else:
                self.confirm_and_open_unsafe(decoded, safety_notes)

    def _on_decode_failed(self, error: str) -> None:
        self._set_decode_busy(False)
        self.url_field.clear()
        self.scan_notes.setPlainText(f"Decode failed: {error}")
        QMessageBox.warning(self, "Decode Error", f"QR decode failed: {error}")

    def _on_decode_thread_finished(self) -> None:
        self._decode_thread = None

    def _set_decode_busy(self, busy: bool) -> None:
        self.decode_progress.setVisible(busy)
        self.snip_btn.setEnabled(not busy)
        self.decode_file_btn.setEnabled(not busy)
        if busy:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        else:
            while QApplication.overrideCursor() is not None:
                QApplication.restoreOverrideCursor()

    def decode_from_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            str(Path.home()),
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)",
        )
        if not file_path:
            return
        self.decode_from_path(file_path)

    def decode_from_path(self, file_path: str) -> None:
        from PySide6.QtGui import QImage

        image = QImage(file_path)
        if image.isNull():
            QMessageBox.warning(self, "Image Error", "Could not load that image file.")
            return
        self.handle_snip_image(image)

    def copy_current_link(self) -> None:
        link = self.url_field.text().strip()
        if not link:
            return
        QApplication.clipboard().setText(link)

    def open_current_link(self) -> None:
        link = self.url_field.text().strip()
        if not link:
            return

        if self.safety_chk.isChecked():
            safety = analyze_url(link)
            if not safety.is_safe:
                self.confirm_and_open_unsafe(link, safety.warnings)
                return

        self.open_link(link)

    def confirm_and_open_unsafe(self, link: str, warnings: list[str]) -> None:
        warning_text = "This link seems risky:\n\n- " + "\n- ".join(warnings)
        warning_text += "\n\nOpen anyway?"

        choice = QMessageBox.warning(
            self,
            "Safety Warning",
            warning_text,
            QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )

        if choice == QMessageBox.StandardButton.Open:
            self.open_link(link)

    def open_link(self, link: str) -> None:
        mode = self.browser_mode.currentText()
        browser = self.browser_path.text().strip()

        if mode == "custom" and browser:
            if not os.path.exists(browser):
                QMessageBox.warning(
                    self,
                    "Browser Path",
                    "Custom browser path does not exist. Falling back to system default.",
                )
                webbrowser.open(link)
                return
            subprocess.Popen([browser, link])
            return

        webbrowser.open(link)

    def pick_browser(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select Browser Executable", str(Path.home()))
        if path:
            self.browser_path.setText(path)

    def save_settings(self) -> None:
        selected_hotkey = self.hotkey_field.text().strip()
        try:
            parse_hotkey(selected_hotkey)
        except ValueError as exc:
            QMessageBox.warning(self, "Invalid Hotkey", str(exc))
            return

        new_cfg = AppConfig(
            auto_open_url=self.auto_open_chk.isChecked(),
            auto_copy_link=self.auto_copy_chk.isChecked(),
            safety_checks_enabled=self.safety_chk.isChecked(),
            browser_mode=self.browser_mode.currentText(),
            custom_browser_path=self.browser_path.text().strip(),
            hotkey_enabled=self.hotkey_enabled_chk.isChecked(),
            hotkey=selected_hotkey,
        )
        save_config(new_cfg)
        self.config = new_cfg

        self._refresh_snip_button_text()
        self._apply_hotkey_settings(show_errors=False)
        helper_reloaded = signal_hotkey_helper_reload()

        if not self.safety_chk.isChecked():
            QMessageBox.warning(
                self,
                "Safety Disabled",
                "Safety checks are OFF. Unsafe links may open without warnings.",
            )

        if self._helper_running:
            if helper_reloaded:
                QMessageBox.information(
                    self,
                    "Saved",
                    "Settings saved. Native hotkey helper reloaded your hotkey settings.",
                )
            else:
                QMessageBox.information(
                    self,
                    "Saved",
                    "Settings saved. Restart the hotkey helper for hotkey changes to take effect.",
                )
            return

        QMessageBox.information(self, "Saved", "Settings saved.")

    def exit_app(self) -> None:
        self.hotkey_listener.stop()
        if self.tray_icon:
            self.tray_icon.hide()
        QApplication.quit()
