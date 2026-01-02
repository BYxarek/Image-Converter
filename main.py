import json
import math
import time
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except Exception:  # Optional dependency
    DND_FILES = None
    TkinterDnD = None


FORMATS = ["PNG", "WEBP", "JPEG", "BMP", "TIFF", "GIF"]
QUALITY_PRESETS = {
    "lossless": {"WEBP": {"lossless": True, "quality": 100, "method": 6}},
    "high": {"WEBP": {"lossless": False, "quality": 90, "method": 6}, "JPEG": {"quality": 90}},
    "balanced": {"WEBP": {"lossless": False, "quality": 80, "method": 4}, "JPEG": {"quality": 80}},
    "compact": {"WEBP": {"lossless": False, "quality": 70, "method": 4}, "JPEG": {"quality": 70}},
}
CHUNK_SIZE = 1024 * 256
CONFIG_PATH = Path("settings.json")
STRINGS_PATH = Path("strings.json")
WINDOW_SIZE = (720, 720)
COLORS = {
    "bg": "#0b1220",
    "card": "#111827",
    "accent": "#22d3ee",
    "accent_2": "#38bdf8",
    "text": "#e5e7eb",
    "muted": "#94a3b8",
    "button": "#22c55e",
    "button_hover": "#16a34a",
}


def suggest_output_path(input_path: str, fmt: str) -> str:
    path = Path(input_path)
    return str(path.with_suffix(f".{fmt.lower()}"))


def convert_image(input_path: str, output_path: str, fmt: str) -> None:
    with Image.open(input_path) as im:
        save_kwargs = {}

        if fmt == "WEBP":
            save_kwargs.update(lossless=True, method=6, quality=100)
        elif fmt == "JPEG":
            save_kwargs.update(quality=95, subsampling=0, optimize=True)
        elif fmt == "PNG":
            save_kwargs.update(optimize=True)
        elif fmt == "TIFF":
            save_kwargs.update(compression="tiff_lzw")
        elif fmt == "GIF":
            save_kwargs.update(save_all=False)

        if fmt in {"JPEG", "BMP"} and im.mode in {"RGBA", "LA", "P"}:
            im = im.convert("RGB")

        im.save(output_path, format=fmt, **save_kwargs)


def main() -> None:
    if TkinterDnD:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    root.title("Image Converter")
    root.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")
    root.resizable(True, True)
    root.minsize(680, 500)
    root.configure(bg=COLORS["bg"])

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(
        "Card.TFrame",
        background=COLORS["card"],
    )
    style.configure(
        "Card.TLabel",
        background=COLORS["card"],
        foreground=COLORS["text"],
        font=("Segoe UI", 10),
    )
    style.configure(
        "Title.TLabel",
        background=COLORS["card"],
        foreground=COLORS["text"],
        font=("Segoe UI Semibold", 18),
    )
    style.configure(
        "Muted.TLabel",
        background=COLORS["card"],
        foreground=COLORS["muted"],
        font=("Segoe UI", 9),
    )
    style.configure(
        "Accent.TButton",
        background=COLORS["button"],
        foreground="#0b1220",
        font=("Segoe UI Semibold", 11),
        padding=(18, 8),
        borderwidth=0,
    )
    style.map(
        "Accent.TButton",
        background=[("active", COLORS["button_hover"]), ("disabled", "#334155")],
        foreground=[("disabled", "#94a3b8")],
    )
    style.configure(
        "Ghost.TButton",
        background=COLORS["card"],
        foreground=COLORS["accent"],
        font=("Segoe UI", 10),
        padding=(12, 6),
        borderwidth=1,
        relief="solid",
    )
    style.map(
        "Ghost.TButton",
        background=[("active", "#0f172a")],
    )
    style.configure(
        "Path.TEntry",
        fieldbackground="#0f172a",
        foreground=COLORS["text"],
        padding=6,
        borderwidth=0,
    )
    style.configure(
        "Format.TCombobox",
        fieldbackground="#0f172a",
        foreground=COLORS["text"],
        padding=4,
        borderwidth=0,
    )
    style.map(
        "Format.TCombobox",
        fieldbackground=[("readonly", "#0f172a")],
        foreground=[("readonly", COLORS["text"])],
        selectforeground=[("readonly", COLORS["text"])],
        selectbackground=[("readonly", "#0f172a")],
    )
    style.configure(
        "Card.TRadiobutton",
        background=COLORS["card"],
        foreground=COLORS["text"],
        font=("Segoe UI", 9),
    )
    style.map(
        "Card.TRadiobutton",
        foreground=[("disabled", COLORS["muted"])],
    )

    def load_strings() -> dict:
        try:
            return json.loads(STRINGS_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {"en": {}}

    strings = load_strings()

    def load_settings() -> dict:
        defaults = {
            "lang": "en",
            "format": FORMATS[0],
            "quality": "lossless",
            "output_dir": "",
        }
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return defaults
            lang = data.get("lang", defaults["lang"])
            fmt = data.get("format", defaults["format"])
            quality = data.get("quality", defaults["quality"])
            out_dir = data.get("output_dir", defaults["output_dir"])
            if lang not in {"ru", "en"}:
                lang = defaults["lang"]
            if fmt not in FORMATS:
                fmt = defaults["format"]
            if quality not in QUALITY_PRESETS:
                quality = defaults["quality"]
            if not isinstance(out_dir, str):
                out_dir = defaults["output_dir"]
            return {
                "lang": lang,
                "format": fmt,
                "quality": quality,
                "output_dir": out_dir,
            }
        except Exception:
            return defaults

    def save_settings() -> None:
        data = {
            "lang": lang_var.get(),
            "format": format_var.get(),
            "quality": quality_key["value"],
            "output_dir": out_dir_var.get().strip(),
        }
        try:
            CONFIG_PATH.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    settings = load_settings()

    def tr(key: str, **kwargs) -> str:
        lang = lang_var.get()
        text = strings.get(lang, {}).get(key) or strings.get("en", {}).get(key) or key
        return text.format(**kwargs)

    input_path_var = tk.StringVar(value="")
    info_var = tk.StringVar(value="")
    status_var = tk.StringVar(value="")
    format_var = tk.StringVar(value=settings["format"])
    quality_var = tk.StringVar(value="")
    out_dir_var = tk.StringVar(value=settings["output_dir"])
    name_mode_var = tk.StringVar(value="auto")
    file_count_var = tk.StringVar(value="")
    lang_var = tk.StringVar(value=settings["lang"])
    preview_photo: dict[str, ImageTk.PhotoImage | None] = {"image": None}
    status_key = {"value": "ready"}
    quality_key = {"value": settings["quality"]}
    file_count_state = {"value": 0}
    cancel_flag = {"stop": False}

    bg_canvas = tk.Canvas(root, bg=COLORS["bg"], highlightthickness=0)
    bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

    circle_1 = bg_canvas.create_oval(
        40, 40, 260, 260, fill="#0f2038", outline=""
    )
    circle_2 = bg_canvas.create_oval(
        430, 180, 700, 450, fill="#122646", outline=""
    )

    def animate_background() -> None:
        t = time.perf_counter()
        dx = math.sin(t * 0.6) * 18
        dy = math.cos(t * 0.8) * 12
        bg_canvas.coords(circle_1, 40 + dx, 40 + dy, 260 + dx, 260 + dy)

        dx2 = math.cos(t * 0.4) * 14
        dy2 = math.sin(t * 0.7) * 16
        bg_canvas.coords(circle_2, 430 + dx2, 180 + dy2, 700 + dx2, 450 + dy2)

        root.after(40, animate_background)

    def set_status(key: str, **kwargs) -> None:
        status_key["value"] = key
        status_var.set(tr(key, **kwargs))

    def update_file_count(count: int) -> None:
        file_count_state["value"] = count
        file_count_var.set(tr("files_count", count=count))

    def set_info_default() -> None:
        info_var.set(tr("file_none"))

    def choose_input() -> None:
        path = filedialog.askopenfilename(
            title=tr("pick_image"),
            filetypes=[
                (tr("images_label"), "*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.tif;*.tiff;*.gif"),
                (tr("all_files"), "*.*"),
            ],
        )
        if path:
            add_files([path])

    def clear_input() -> None:
        input_path_var.set("")
        set_info_default()
        set_status("ready")
        files_list.delete(0, tk.END)
        update_file_count(0)
        preview_label.configure(image="")
        preview_photo["image"] = None

    def add_files(paths: list[str]) -> None:
        added = 0
        for p in paths:
            p = p.strip().strip('"')
            if not p:
                continue
            path = Path(p)
            if not path.exists():
                continue
            if p not in files_list.get(0, tk.END):
                files_list.insert(tk.END, p)
                added += 1
        if added:
            update_selected_info()
            update_file_count(files_list.size())

    def on_drop(event) -> None:
        raw = event.data
        files = root.tk.splitlist(raw)
        add_files(list(files))

    def update_selected_info(event=None) -> None:
        selection = files_list.curselection()
        if not selection:
            set_info_default()
            preview_label.configure(image="")
            preview_photo["image"] = None
            return
        path = files_list.get(selection[0])
        input_path_var.set(path)
        try:
            with Image.open(path) as im:
                info_var.set(f"{im.format} • {im.size[0]}x{im.size[1]} • {im.mode}")
                preview = im.copy()
                preview.thumbnail((140, 140))
                preview_photo["image"] = ImageTk.PhotoImage(preview)
                preview_label.configure(image=preview_photo["image"])
        except Exception:
            info_var.set(tr("read_failed"))
            preview_label.configure(image="")
            preview_photo["image"] = None

    def remove_selected() -> None:
        selection = list(files_list.curselection())
        if not selection:
            return
        for idx in reversed(selection):
            files_list.delete(idx)
        update_file_count(files_list.size())
        update_selected_info()

    def choose_output_dir() -> None:
        path = filedialog.askdirectory(title=tr("output_folder"))
        if path:
            out_dir_var.set(path)
            save_settings()

    def get_output_path(input_path: str, fmt: str) -> str:
        base = Path(input_path).stem
        suffix = f".{fmt.lower()}"
        out_dir = out_dir_var.get().strip()
        if out_dir:
            return str(Path(out_dir) / f"{base}{suffix}")
        return str(Path(input_path).with_suffix(suffix))

    def get_file_size(path: str) -> int:
        try:
            size = Path(path).stat().st_size
            return size if size > 0 else 1
        except Exception:
            return 1

    def read_with_progress(path: str, total_read: int, total_bytes: int) -> int:
        try:
            with open(path, "rb") as handle:
                while True:
                    if cancel_flag["stop"]:
                        break
                    chunk = handle.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    total_read += len(chunk)
                    progress_bar.configure(value=total_read)
                    percent = min(100, int((total_read / total_bytes) * 100))
                    set_status("processing", percent=percent)
                    root.update_idletasks()
        except Exception:
            return total_read
        return total_read

    def build_save_kwargs(fmt: str, preset: str) -> dict:
        save_kwargs = {}
        if fmt == "WEBP":
            save_kwargs.update(lossless=True, method=6, quality=100)
        elif fmt == "JPEG":
            save_kwargs.update(quality=95, subsampling=0, optimize=True)
        elif fmt == "PNG":
            save_kwargs.update(optimize=True)
        elif fmt == "TIFF":
            save_kwargs.update(compression="tiff_lzw")
        elif fmt == "GIF":
            save_kwargs.update(save_all=False)

        preset_map = QUALITY_PRESETS.get(preset, {})
        override = preset_map.get(fmt)
        if override:
            save_kwargs.update(override)
            if fmt == "JPEG":
                save_kwargs.setdefault("subsampling", 0)
                save_kwargs.setdefault("optimize", True)
        return save_kwargs

    def convert_single(input_path: str, output_path: str, fmt: str, preset: str) -> None:
        with Image.open(input_path) as im:
            if fmt in {"JPEG", "BMP"} and im.mode in {"RGBA", "LA", "P"}:
                im = im.convert("RGB")
            save_kwargs = build_save_kwargs(fmt, preset)
            im.save(output_path, format=fmt, **save_kwargs)

    def do_convert() -> None:
        if files_list.size() == 0:
            messagebox.showwarning(tr("no_file_title"), tr("no_files"))
            return

        fmt = format_var.get()
        preset = get_quality_key()
        save_settings()
        cancel_flag["stop"] = False
        errors: list[tuple[str, str]] = []
        files = list(files_list.get(0, tk.END))
        total_bytes = sum(get_file_size(p) for p in files)
        total_read = 0

        convert_button.configure(state="disabled")
        browse_button.configure(state="disabled")
        clear_button.configure(state="disabled")
        remove_button.configure(state="disabled")
        cancel_button.configure(state="normal")
        set_status("processing", percent=0)
        progress_bar.configure(maximum=total_bytes, value=0)
        root.update_idletasks()

        try:
            for i, input_path in enumerate(files):
                if cancel_flag["stop"]:
                    set_status("canceled")
                    break
                file_size = get_file_size(input_path)
                output_path = get_output_path(input_path, fmt)
                if name_mode_var.get() == "ask":
                    output_path = filedialog.asksaveasfilename(
                        title=tr("save_as"),
                        initialfile=Path(suggest_output_path(input_path, fmt)).name,
                        defaultextension=f".{fmt.lower()}",
                        filetypes=[(fmt, f"*.{fmt.lower()}"), ("Все файлы", "*.*")],
                    )
                    if not output_path:
                        total_read += file_size
                        progress_bar.configure(value=total_read)
                        set_status("skipping", done=i + 1, total=len(files))
                        root.update_idletasks()
                        continue
                total_read = read_with_progress(input_path, total_read, total_bytes)
                if cancel_flag["stop"]:
                    set_status("canceled")
                    break
                try:
                    convert_single(input_path, output_path, fmt, preset)
                except Exception as exc:
                    errors.append((input_path, str(exc)))
                set_status("done_count", done=i + 1, total=len(files))
                root.update_idletasks()
        except Exception as exc:
            set_status("error")
            messagebox.showerror(tr("error_title"), tr("convert_failed", error=exc))
            convert_button.configure(state="normal")
            browse_button.configure(state="normal")
            clear_button.configure(state="normal")
            remove_button.configure(state="normal")
            cancel_button.configure(state="disabled")
            return

        convert_button.configure(state="normal")
        browse_button.configure(state="normal")
        clear_button.configure(state="normal")
        remove_button.configure(state="normal")
        cancel_button.configure(state="disabled")
        if cancel_flag["stop"]:
            messagebox.showinfo(tr("cancel_title"), tr("cancel_msg"))
        else:
            set_status("done")
            if errors:
                log_dir = out_dir_var.get().strip() or str(Path.cwd())
                log_path = Path(log_dir) / "conversion_errors.log"
                try:
                    with open(log_path, "w", encoding="utf-8") as handle:
                        for path, err in errors:
                            handle.write(f"{path} | {err}\n")
                except Exception:
                    log_path = None
                if log_path:
                    messagebox.showwarning(
                        tr("warn_errors_title"),
                        tr("warn_errors_msg", path=log_path),
                    )
                else:
                    messagebox.showwarning(
                        tr("warn_errors_title"),
                        tr("warn_errors_msg_no_log"),
                    )
            else:
                messagebox.showinfo(tr("success_title"), tr("success"))

    card = ttk.Frame(root, style="Card.TFrame", padding=24)
    card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)

    title = ttk.Label(card, text="", style="Title.TLabel")
    title.pack(anchor="w")
    subtitle = ttk.Label(
        card,
        text="",
        style="Muted.TLabel",
    )
    subtitle.pack(anchor="w", pady=(6, 16))

    path_row = ttk.Frame(card, style="Card.TFrame")
    path_row.pack(fill="x", pady=(0, 8))
    browse_button = ttk.Button(
        path_row, text="", style="Ghost.TButton", command=choose_input
    )
    browse_button.pack(side="left")
    remove_button = ttk.Button(
        path_row, text="", style="Ghost.TButton", command=remove_selected
    )
    remove_button.pack(side="left", padx=(8, 0))
    clear_button = ttk.Button(
        path_row, text="", style="Ghost.TButton", command=clear_input
    )
    clear_button.pack(side="left", padx=(8, 0))
    file_count_label = ttk.Label(
        path_row, textvariable=file_count_var, style="Muted.TLabel"
    )
    file_count_label.pack(side="right")

    list_row = ttk.Frame(card, style="Card.TFrame")
    list_row.pack(fill="both", expand=True, pady=(0, 10))
    files_list = tk.Listbox(
        list_row,
        height=6,
        bg="#0f172a",
        fg=COLORS["text"],
        highlightthickness=0,
        selectbackground=COLORS["accent_2"],
        selectforeground="#0b1220",
        activestyle="none",
    )
    files_list.pack(side="left", fill="both", expand=True)
    files_list.bind("<<ListboxSelect>>", update_selected_info)
    preview_label = ttk.Label(list_row, style="Card.TLabel")
    preview_label.pack(side="left", padx=(10, 0))

    info_label = ttk.Label(card, textvariable=info_var, style="Muted.TLabel")
    info_label.pack(anchor="w", pady=(0, 12))

    format_row = ttk.Frame(card, style="Card.TFrame")
    format_row.pack(fill="x")
    format_label = ttk.Label(format_row, text="", style="Card.TLabel")
    format_label.pack(side="left")
    format_combo = ttk.Combobox(
        format_row,
        textvariable=format_var,
        values=FORMATS,
        state="readonly",
        style="Format.TCombobox",
        width=12,
    )
    format_combo.pack(side="left", padx=(12, 0))
    quality_label = ttk.Label(format_row, text="", style="Card.TLabel")
    quality_label.pack(side="left", padx=(18, 0))
    quality_combo = ttk.Combobox(
        format_row,
        textvariable=quality_var,
        values=[],
        state="readonly",
        style="Format.TCombobox",
        width=16,
    )
    quality_combo.pack(side="left", padx=(8, 0))
    lang_label = ttk.Label(format_row, text="", style="Card.TLabel")
    lang_label.pack(side="left", padx=(18, 0))
    lang_combo = ttk.Combobox(
        format_row,
        textvariable=lang_var,
        values=["ru", "en"],
        state="readonly",
        style="Format.TCombobox",
        width=6,
    )
    lang_combo.pack(side="left", padx=(8, 0))

    output_row = ttk.Frame(card, style="Card.TFrame")
    output_row.pack(fill="x", pady=(10, 0))
    out_label = ttk.Label(output_row, text="", style="Card.TLabel")
    out_label.pack(side="left")
    out_entry = ttk.Entry(
        output_row, textvariable=out_dir_var, style="Path.TEntry", state="readonly"
    )
    out_entry.pack(side="left", fill="x", expand=True, padx=(8, 0))
    out_button = ttk.Button(
        output_row, text="", style="Ghost.TButton", command=choose_output_dir
    )
    out_button.pack(side="left", padx=(8, 0))

    name_row = ttk.Frame(card, style="Card.TFrame")
    name_row.pack(fill="x", pady=(8, 0))
    name_label = ttk.Label(name_row, text="", style="Card.TLabel")
    name_label.pack(side="left")
    ttk.Radiobutton(
        name_row,
        text="",
        variable=name_mode_var,
        value="auto",
        style="Card.TRadiobutton",
    ).pack(side="left", padx=(8, 0))
    ttk.Radiobutton(
        name_row,
        text="",
        variable=name_mode_var,
        value="ask",
        style="Card.TRadiobutton",
    ).pack(side="left", padx=(8, 0))

    note = ttk.Label(
        card,
        text="",
        style="Muted.TLabel",
    )
    note.pack(anchor="w", pady=(12, 8))

    actions = ttk.Frame(card, style="Card.TFrame")
    actions.pack(fill="x", pady=(6, 0))
    convert_button = ttk.Button(
        actions, text="", style="Accent.TButton", command=do_convert
    )
    convert_button.pack(side="left")
    cancel_button = ttk.Button(
        actions,
        text="",
        style="Ghost.TButton",
        command=lambda: cancel_flag.update(stop=True),
        state="disabled",
    )
    cancel_button.pack(side="left", padx=(12, 0))
    status_label = ttk.Label(actions, textvariable=status_var, style="Muted.TLabel")
    status_label.pack(side="right")

    progress_bar = ttk.Progressbar(
        card, mode="determinate", length=520, maximum=1, value=0
    )
    progress_bar.pack(fill="x", pady=(10, 0))

    def update_language(event=None) -> None:
        root.title(tr("title"))
        title.configure(text=tr("title"))
        subtitle.configure(text=tr("subtitle"))
        browse_button.configure(text=tr("add_files"))
        remove_button.configure(text=tr("remove"))
        clear_button.configure(text=tr("clear"))
        format_label.configure(text=tr("format"))
        quality_label.configure(text=tr("quality"))
        out_label.configure(text=tr("output_dir"))
        out_button.configure(text=tr("choose"))
        name_label.configure(text=tr("names"))
        convert_button.configure(text=tr("convert"))
        cancel_button.configure(text=tr("cancel"))
        lang_label.configure(text=tr("lang"))
        note.configure(text=tr("note"))
        radiobuttons = [w for w in name_row.winfo_children() if isinstance(w, ttk.Radiobutton)]
        if len(radiobuttons) >= 2:
            radiobuttons[0].configure(text=tr("auto"))
            radiobuttons[1].configure(text=tr("ask"))
        set_info_default()
        set_status(status_key["value"])
        update_file_count(file_count_state["value"])
        labels = strings.get(lang_var.get(), {}).get("quality_labels", {})
        quality_combo.configure(values=list(labels.values()))
        quality_key = get_quality_key()
        if labels:
            quality_var.set(labels.get(quality_key, list(labels.values())[0]))
        note.configure(text=tr("note"))

    def get_quality_key() -> str:
        return quality_key["value"]

    def on_quality_change(event=None) -> None:
        labels = strings.get(lang_var.get(), {}).get("quality_labels", {})
        reverse = {v: k for k, v in labels.items()}
        quality_key["value"] = reverse.get(quality_var.get(), "lossless")
        if labels:
            quality_var.set(labels[quality_key["value"]])
        save_settings()

    def on_language_change(event=None) -> None:
        prev_key = quality_key["value"]
        update_language()
        quality_key["value"] = prev_key
        labels = strings.get(lang_var.get(), {}).get("quality_labels", {})
        if labels:
            quality_var.set(labels.get(quality_key["value"], list(labels.values())[0]))
        save_settings()

    def on_format_change(event=None) -> None:
        save_settings()

    lang_combo.bind("<<ComboboxSelected>>", on_language_change)
    quality_combo.bind("<<ComboboxSelected>>", on_quality_change)
    format_combo.bind("<<ComboboxSelected>>", on_format_change)
    update_language()

    if TkinterDnD and DND_FILES:
        drop_register = getattr(files_list, "drop_target_register", None)
        dnd_bind = getattr(files_list, "dnd_bind", None)
        if callable(drop_register) and callable(dnd_bind):
            drop_register(DND_FILES)
            dnd_bind("<<Drop>>", on_drop)

    animate_background()

    root.mainloop()


if __name__ == "__main__":
    main()
