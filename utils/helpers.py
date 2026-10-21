from datetime import date, datetime
from tkinter import ttk
import customtkinter as ctk


def center_window(window, width: int, height: int):
    """Căn giữa cửa sổ trên màn hình"""
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def format_date(val) -> str:
    if not val:
        return ""
    if isinstance(val, (date, datetime)):
        return val.strftime("%Y-%m-%d")
    return str(val)


def format_currency(amount) -> str:
    """Định dạng số tiền VNĐ"""
    try:
        val = float(amount or 0)
        return f"{val:,.0f} đ"
    except (ValueError, TypeError):
        return "0 đ"


def apply_treeview_style():
    """Tùy chỉnh giao diện bảng ttk.Treeview đồng bộ với CustomTkinter"""
    style = ttk.Style()
    style.theme_use("clam")

    mode = ctk.get_appearance_mode()
    if mode == "Dark":
        bg_color = "#2b2b2b"
        fg_color = "#f0f0f0"
        header_bg = "#1f538d"
        header_fg = "#ffffff"
        selected_bg = "#3b8ed0"
        row_alt = "#333333"
    else:
        bg_color = "#ffffff"
        fg_color = "#1a1a1a"
        header_bg = "#1f538d"
        header_fg = "#ffffff"
        selected_bg = "#3b8ed0"
        row_alt = "#f4f6f9"

    style.configure(
        "Custom.Treeview",
        background=bg_color,
        foreground=fg_color,
        fieldbackground=bg_color,
        rowheight=32,
        font=("Segoe UI", 11),
        borderwidth=0,
    )
    style.configure(
        "Custom.Treeview.Heading",
        background=header_bg,
        foreground=header_fg,
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        padding=(8, 6),
    )
    style.map(
        "Custom.Treeview",
        background=[("selected", selected_bg)],
        foreground=[("selected", "#ffffff")],
    )
    style.map(
        "Custom.Treeview.Heading",
        background=[("active", "#14375e")],
    )
    return row_alt


# ==========================================================
# Sửa lỗi chữ bị IN ĐẬM / NỔI LÊN khi gõ tiếng Việt trên Windows
# ----------------------------------------------------------
# Nguyên nhân: Khi gõ bằng bộ gõ có khung soạn chữ (IME composition),
# Tkinter không đặt font cho khung chữ đang gõ dở, nên Windows dùng font
# mặc định "System" (vốn in đậm, to hơn). Hàm dưới đây gọi Win32 API
# ImmSetCompositionFontW để khung chữ đang gõ dùng đúng font của ô nhập.
# ==========================================================
def enable_ime_font_fix(root):
    """Đồng bộ font của khung chữ đang gõ (IME) với font của ô nhập. Chỉ có tác dụng trên Windows."""
    import sys

    if sys.platform != "win32":
        return

    import ctypes
    from ctypes import wintypes

    class LOGFONTW(ctypes.Structure):
        _fields_ = [
            ("lfHeight", wintypes.LONG),
            ("lfWidth", wintypes.LONG),
            ("lfEscapement", wintypes.LONG),
            ("lfOrientation", wintypes.LONG),
            ("lfWeight", wintypes.LONG),
            ("lfItalic", ctypes.c_ubyte),
            ("lfUnderline", ctypes.c_ubyte),
            ("lfStrikeOut", ctypes.c_ubyte),
            ("lfCharSet", ctypes.c_ubyte),
            ("lfOutPrecision", ctypes.c_ubyte),
            ("lfClipPrecision", ctypes.c_ubyte),
            ("lfQuality", ctypes.c_ubyte),
            ("lfPitchAndFamily", ctypes.c_ubyte),
            ("lfFaceName", ctypes.c_wchar * 32),
        ]

    try:
        imm32 = ctypes.WinDLL("imm32")
        user32 = ctypes.WinDLL("user32")
    except OSError:
        return

    imm32.ImmGetContext.argtypes = [wintypes.HWND]
    imm32.ImmGetContext.restype = ctypes.c_void_p
    imm32.ImmSetCompositionFontW.argtypes = [ctypes.c_void_p, ctypes.POINTER(LOGFONTW)]
    imm32.ImmSetCompositionFontW.restype = wintypes.BOOL
    imm32.ImmReleaseContext.argtypes = [wintypes.HWND, ctypes.c_void_p]
    imm32.ImmReleaseContext.restype = wintypes.BOOL
    user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
    user32.GetAncestor.restype = wintypes.HWND

    GA_ROOT = 2
    FW_NORMAL = 400
    DEFAULT_CHARSET = 1
    CLEARTYPE_QUALITY = 5

    def _apply_ime_font(event):
        widget = event.widget
        try:
            hwnd = widget.winfo_id()
            font_spec = widget.cget("font")
            family = widget.tk.call("font", "actual", font_spec, "-family")
            size = int(widget.tk.call("font", "actual", font_spec, "-size"))
        except Exception:
            return

        # Kích thước âm = pixel, dương = point -> quy đổi sang pixel theo DPI màn hình
        if size < 0:
            pixel_height = -size
        else:
            pixel_height = round(size * widget.winfo_fpixels("1i") / 72)

        lf = LOGFONTW()
        lf.lfHeight = -pixel_height
        lf.lfWeight = FW_NORMAL  # Chữ thường, không in đậm
        lf.lfCharSet = DEFAULT_CHARSET
        lf.lfQuality = CLEARTYPE_QUALITY
        lf.lfFaceName = str(family)[:31]

        # Áp dụng cho cả ô nhập và cửa sổ cha (tùy bộ gõ gắn IME context vào đâu)
        targets = {hwnd}
        root_hwnd = user32.GetAncestor(hwnd, GA_ROOT)
        if root_hwnd:
            targets.add(root_hwnd)

        for target in targets:
            himc = imm32.ImmGetContext(target)
            if himc:
                imm32.ImmSetCompositionFontW(himc, ctypes.byref(lf))
                imm32.ImmReleaseContext(target, himc)

    # CTkEntry / CTkComboBox bên trong đều dùng tkinter.Entry -> bind theo class "Entry"
    root.bind_class("Entry", "<FocusIn>", _apply_ime_font, add="+")

