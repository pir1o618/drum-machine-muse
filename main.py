import textwrap
import threading
import tkinter as tk
from ai import call_gpt

try:
    import winsound
except ImportError:
    winsound = None


def play_pad_sound(instrument: str, muted: bool = False) -> None:
    """Plays a short synthesized drum hit sound on Windows without blocking the UI."""
    if muted or winsound is None:
        return

    tones = {
        "Hi-Hat": (1800, 35),
        "Snare": (420, 55),
        "Bass Drum": (110, 80),
    }
    freq, duration = tones.get(instrument, (440, 45))

    def _beep() -> None:
        try:
            winsound.Beep(freq, duration)
        except Exception:
            pass

    threading.Thread(target=_beep, daemon=True).start()


def animate_beat_window(rhythm: str) -> None:
    """Opens a Tkinter Canvas window that loops the beat continuously until paused or closed."""
    root = tk.Tk()
    root.title(f"Drum Machine Muse - {rhythm.upper()}")
    root.resizable(False, False)

    # Bring window to the front briefly so it is easy to spot over VS Code
    root.lift()
    root.attributes("-topmost", True)
    root.after(300, lambda: root.winfo_exists() and root.attributes("-topmost", False))

    canvas = tk.Canvas(root, width=520, height=320, bg="#181825", highlightthickness=0)
    canvas.pack()

    canvas.create_text(260, 24, text="DRUM MACHINE MUSE", fill="#f5e0dc", font=("Arial", 16, "bold"))
    canvas.create_text(260, 48, text=f"Style: {rhythm.upper()}  |  Continuous 4/4 Loop", fill="#89b4fa", font=("Arial", 12))

    # Draw three drum pads: Hi-Hat (HH), Snare (SN), and Bass Drum (BD)
    hh_pad = canvas.create_rectangle(80, 125, 170, 182, fill="#a6e3a1", outline="#1e1e2e", width=2)
    canvas.create_text(125, 200, text="HH (Hi-Hat)", fill="#cdd6f4", font=("Arial", 10, "bold"))

    sn_pad = canvas.create_rectangle(215, 125, 305, 182, fill="#f9e2af", outline="#1e1e2e", width=2)
    canvas.create_text(260, 200, text="SN (Snare)", fill="#cdd6f4", font=("Arial", 10, "bold"))

    bd_pad = canvas.create_rectangle(350, 125, 440, 182, fill="#f38ba8", outline="#1e1e2e", width=2)
    canvas.create_text(395, 200, text="BD (Kick)", fill="#cdd6f4", font=("Arial", 10, "bold"))

    # Animated beat indicator above the pads
    beat_ball = canvas.create_oval(113, 74, 137, 98, fill="#cba6f7", outline="#ffffff", width=1)
    status_text = canvas.create_text(260, 238, text="Starting continuous groove...", fill="#f5e0dc", font=("Arial", 12, "bold"))
    tempo_text = canvas.create_text(
        260,
        260,
        text="Speed: 1.0x (Normal)  |  Sound: ON  |  Bar: 1",
        fill="#a6adc8",
        font=("Arial", 9),
    )

    cycle = [
        (125, hh_pad, "#a6e3a1", "#e6ffea", "Hi-Hat"),
        (260, sn_pad, "#f9e2af", "#fffbe6", "Snare"),
        (395, bd_pad, "#f38ba8", "#ffe6ec", "Bass Drum"),
        (260, sn_pad, "#f9e2af", "#fffbe6", "Snare"),
    ]

    state = {
        "step": 0,
        "paused": False,
        "muted": False,
        "speed_multiplier": 1.0,
        "timer_id": None,
    }

    def update_info_label() -> None:
        mult = state["speed_multiplier"]
        label = "Normal"
        if mult < 0.95:
            label = "Slower"
        elif mult > 1.05:
            label = "Faster"
        sound_label = "OFF" if state["muted"] else "ON"
        bar_num = (state["step"] // 4) + 1
        canvas.itemconfig(tempo_text, text=f"Speed: {mult:.1f}x ({label})  |  Sound: {sound_label}  |  Bar: {bar_num}")

    def cancel_pending_timer() -> None:
        if state["timer_id"] is not None and root.winfo_exists():
            root.after_cancel(state["timer_id"])
            state["timer_id"] = None

    def reset_pads() -> None:
        for idx, (_cx, pad_id, base_color, _active_color, _inst) in enumerate(cycle):
            canvas.itemconfig(pad_id, fill=base_color)
            if idx == 0:
                canvas.coords(beat_ball, 113, 74, 137, 98)

    def close_window() -> None:
        cancel_pending_timer()
        if root.winfo_exists():
            root.destroy()

    def run_step() -> None:
        if not root.winfo_exists() or state["paused"]:
            return

        step = state["step"]
        beat_num = (step % 4) + 1
        cx, pad_id, base_color, active_color, instrument = cycle[step % len(cycle)]

        # Strike active pad, play sound, and update status text continuously
        canvas.itemconfig(pad_id, fill=active_color)
        canvas.coords(beat_ball, cx - 12, 90, cx + 12, 114)
        canvas.itemconfig(status_text, text=f"Beat {beat_num}/4  •  {instrument}")
        update_info_label()
        play_pad_sound(instrument, muted=state["muted"])
        root.update_idletasks()

        hit_ms = max(120, int(420 / state["speed_multiplier"]))
        gap_ms = max(80, int(240 / state["speed_multiplier"]))

        def finish_hit() -> None:
            if not root.winfo_exists():
                return
            canvas.itemconfig(pad_id, fill=base_color)
            canvas.coords(beat_ball, cx - 12, 74, cx + 12, 98)
            state["step"] += 1
            if not state["paused"]:
                state["timer_id"] = root.after(gap_ms, run_step)

        state["timer_id"] = root.after(hit_ms, finish_hit)

    def restart_loop() -> None:
        cancel_pending_timer()
        reset_pads()
        state["step"] = 0
        state["paused"] = False
        pause_btn.config(text="Pause")
        canvas.itemconfig(status_text, text="Restarting loop...")
        update_info_label()
        state["timer_id"] = root.after(150, run_step)

    def toggle_pause() -> None:
        if not state["paused"]:
            state["paused"] = True
            cancel_pending_timer()
            reset_pads()
            pause_btn.config(text="Resume")
            canvas.itemconfig(status_text, text=f"Paused at Beat {(state['step'] % 4) + 1}/4")
        else:
            state["paused"] = False
            pause_btn.config(text="Pause")
            canvas.itemconfig(status_text, text="Resuming groove...")
            state["timer_id"] = root.after(120, run_step)

    def toggle_mute() -> None:
        state["muted"] = not state["muted"]
        mute_btn.config(text="Sound: OFF" if state["muted"] else "Sound: ON")
        update_info_label()

    def change_speed(delta: float) -> None:
        new_val = round(min(2.0, max(0.4, state["speed_multiplier"] + delta)), 1)
        state["speed_multiplier"] = new_val
        update_info_label()

    # Button bar at the bottom of the window
    controls = tk.Frame(root, bg="#11111b", pady=8)
    controls.pack(fill="x")

    btn_style = {"font": ("Arial", 9, "bold"), "padx": 8, "pady": 4, "cursor": "hand2"}

    tk.Button(controls, text="Restart", bg="#89b4fa", fg="#11111b", command=restart_loop, **btn_style).pack(
        side="left", padx=(10, 4)
    )
    pause_btn = tk.Button(controls, text="Pause", bg="#f9e2af", fg="#11111b", command=toggle_pause, **btn_style)
    pause_btn.pack(side="left", padx=4)
    tk.Button(controls, text="- Slower", bg="#313244", fg="#cdd6f4", command=lambda: change_speed(-0.2), **btn_style).pack(
        side="left", padx=4
    )
    tk.Button(controls, text="+ Faster", bg="#313244", fg="#cdd6f4", command=lambda: change_speed(0.2), **btn_style).pack(
        side="left", padx=4
    )
    mute_btn = tk.Button(controls, text="Sound: ON", bg="#cba6f7", fg="#11111b", command=toggle_mute, **btn_style)
    mute_btn.pack(side="left", padx=4)
    tk.Button(controls, text="Continue", bg="#a6e3a1", fg="#11111b", command=close_window, **btn_style).pack(
        side="right", padx=(4, 10)
    )

    root.protocol("WM_DELETE_WINDOW", close_window)
    root.bind("<Escape>", lambda _e: close_window())
    root.bind("<space>", lambda _e: toggle_pause())
    root.bind("<m>", lambda _e: toggle_mute())
    root.bind("<M>", lambda _e: toggle_mute())

    state["timer_id"] = root.after(300, run_step)
    root.mainloop()


def save_patterns_to_pdf(entries: list[tuple[str, str]], filename: str = "drum_patterns.pdf") -> None:
    """Exports selected drum patterns to a multi-page PDF using Python's standard library."""
    lines: list[str] = [
        "DRUM MACHINE MUSE - SELECTED PRACTICE PATTERNS",
        "=" * 64,
        "",
    ]

    for idx, (style, pattern_text) in enumerate(entries, start=1):
        lines.append(f"{idx}. STYLE: {style.upper()}")
        lines.append("-" * 64)
        for raw_line in pattern_text.splitlines():
            clean_line = raw_line.encode("latin-1", "replace").decode("latin-1")
            wrapped = textwrap.wrap(clean_line, width=78) or [""]
            lines.extend(wrapped)
        lines.append("")
        lines.append("=" * 64)
        lines.append("")

    lines_per_page = 46
    pages = [lines[i : i + lines_per_page] for i in range(0, len(lines), lines_per_page)] or [[""]]

    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>",
    ]

    page_ids: list[int] = []
    for page_lines in pages:
        content_ops = ["BT", "/F1 10 Tf", "50 745 Td", "14 TL"]
        for line in page_lines:
            escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            content_ops.append(f"({escaped}) Tj")
            content_ops.append("T*")
        content_ops.append("ET")
        stream_bytes = "\n".join(content_ops).encode("latin-1")

        content_id = len(objects) + 1
        objects.append(
            f"<< /Length {len(stream_bytes)} >>\nstream\n".encode("ascii")
            + stream_bytes
            + b"\nendstream"
        )

        page_id = len(objects) + 1
        page_ids.append(page_id)
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_id} 0 R >>".encode("ascii")
        )

    kids_str = " ".join(f"{pid} 0 R" for pid in page_ids)
    objects[1] = f"<< /Type /Pages /Kids [{kids_str}] /Count {len(page_ids)} >>".encode("ascii")

    pdf_chunks = [b"%PDF-1.4\n"]
    offsets = [0]
    for obj_id, obj_body in enumerate(objects, start=1):
        offsets.append(sum(len(c) for c in pdf_chunks))
        pdf_chunks.append(f"{obj_id} 0 obj\n".encode("ascii") + obj_body + b"\nendobj\n")

    xref_offset = sum(len(c) for c in pdf_chunks)
    xref_lines = [f"xref\n0 {len(objects) + 1}\n", "0000000000 65535 f \n"]
    for off in offsets[1:]:
        xref_lines.append(f"{off:010d} 00000 n \n")

    trailer = (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n"
    )
    pdf_chunks.append("".join(xref_lines).encode("ascii") + trailer.encode("ascii"))

    with open(filename, "wb") as pdf_file:
        pdf_file.write(b"".join(pdf_chunks))


def main() -> None:
    """Main application loop for Drum Machine Muse."""
    print("=" * 60)
    print("        DRUM MACHINE MUSE PROJECT        ")
    print("=" * 60)
    print("Get drum patterns to inspire your next practice session.")
    print("Type 'exit' at any time to close the program.")
    print("-" * 60)

    selected_patterns: list[tuple[str, str]] = []

    while True:
        print()
        rhythm = input("Enter a rhythm style (or 'exit'): ").strip()

        if rhythm.lower() == "exit":
            if selected_patterns:
                try:
                    save_patterns_to_pdf(selected_patterns, "drum_patterns.pdf")
                    print(f"\nSaved {len(selected_patterns)} selected pattern(s) to 'drum_patterns.pdf'")
                except Exception as e:
                    print(f"\nCould not save PDF: {e}")
            print("\nKeep practicing! Goodbye.")
            break

        if not rhythm:
            print("Input cannot be empty. Please enter a valid style.")
            continue

        print("-" * 40)
        print("[ Searching rhythm... ]")
        prompt = f"Create a unique {rhythm} drum pattern for a practice session."

        try:
            drum = call_gpt(prompt)
        except Exception as e:
            drum = f"Error connecting to AI: {e}"

        animate_beat_window(rhythm)

        print(f"\nHere is your custom {rhythm.upper()} drum pattern:\n")
        print(drum)
        print("-" * 40)

        try:
            with open("drum_patterns.log", "a", encoding="utf-8") as file:
                file.write(f"=== STYLE: {rhythm.upper()} ===\n")
                file.write(drum)
                file.write("\n\n" + "=" * 40 + "\n\n")
            print("Saved to 'drum_patterns.log'")
        except Exception as e:
            print(f"Could not save file: {e}")

        keep = input("Add this pattern to your PDF sheet? (y/n): ").strip().lower()
        if keep in ("y", "yes", "s", "si", "sí"):
            selected_patterns.append((rhythm, drum))
            print("Added to PDF queue.")

        print("-" * 60)


if __name__ == "__main__":
    main()
