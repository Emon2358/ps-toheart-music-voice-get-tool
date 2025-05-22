import os
import sys
import subprocess
import threading
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path

def choose_exe(pak_path: Path) -> Path:
    stem = pak_path.stem.upper()
    if stem == '072':
        exe_name = 'thv072.exe'
    elif stem == '073':
        exe_name = 'thv07273.exe'
    else:
        # 数字三桁 or V00～V09
        exe_name = 'thv.exe'
    exe_path = Path(__file__).parent / exe_name
    if not exe_path.exists():
        raise FileNotFoundError(f"'{exe_name}' が見つかりません。")
    return exe_path

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ToHeart PAK→WAV コンバータ＆マルチ抽出")
        self.geometry("700x480")
        self.create_widgets()

    def create_widgets(self):
        # PAK ファイル選択
        file_frame = tk.Frame(self); file_frame.pack(pady=5, fill='x')
        tk.Label(file_frame, text="PAK ファイル:").pack(side=tk.LEFT, padx=5)
        self.file_var = tk.StringVar()
        tk.Entry(file_frame, textvariable=self.file_var, width=50).pack(side=tk.LEFT)
        tk.Button(file_frame, text="選択…", command=self.select_file).pack(side=tk.LEFT)

        # 出力フォルダ選択
        out_frame = tk.Frame(self); out_frame.pack(pady=5, fill='x')
        tk.Label(out_frame, text="出力フォルダ:").pack(side=tk.LEFT, padx=5)
        self.outdir_var = tk.StringVar(value=str(Path.cwd()))
        tk.Entry(out_frame, textvariable=self.outdir_var, width=50).pack(side=tk.LEFT)
        tk.Button(out_frame, text="選択…", command=self.select_outdir).pack(side=tk.LEFT)

        # 実行ボタン
        btn_frame = tk.Frame(self); btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="変換＋マルチ抽出実行", command=self.start_conversion).pack()

        # ログ表示
        self.log = scrolledtext.ScrolledText(self, state='disabled', wrap='word')
        self.log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def select_file(self):
        path = filedialog.askopenfilename(
            title="PAK ファイルを選択", filetypes=[("PAK files", "*.PAK"), ("All files", "*.*")]
        )
        if path: self.file_var.set(path)

    def select_outdir(self):
        path = filedialog.askdirectory(
            title="出力フォルダを選択", initialdir=self.outdir_var.get()
        )
        if path: self.outdir_var.set(path)

    def start_conversion(self):
        pak = self.file_var.get().strip()
        outdir = self.outdir_var.get().strip()
        if not pak or not outdir:
            messagebox.showwarning("警告", "PAK ファイルと出力フォルダを指定してください。")
            return
        pak_path = Path(pak); outdir_path = Path(outdir)
        if not pak_path.exists() or not outdir_path.exists():
            messagebox.showerror("エラー", "パスが正しくありません。")
            return
        try:
            exe_path = choose_exe(pak_path)
        except Exception as e:
            messagebox.showerror("エラー", str(e))
            return
        threading.Thread(
            target=self.run_process, args=(exe_path, pak_path, outdir_path), daemon=True
        ).start()

    def run_process(self, exe_path: Path, pak_path: Path, outdir_path: Path):
        self.log_message(f"▶ 実行: {exe_path.name} {pak_path}\n")
        exe_dir = exe_path.parent

        # 実行前の wav 集合
        before = set(exe_dir.glob("*.wav"))

        try:
            proc = subprocess.Popen(
                [str(exe_path), str(pak_path)],
                cwd=str(exe_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            for line in proc.stdout or []:
                self.log_message(line)
            rc = proc.wait()

            # 新規生成 wav を outdir へ移動
            after = set(exe_dir.glob("*.wav"))
            new_files = after - before
            for wav in new_files:
                target = outdir_path / wav.name
                wav.rename(target)
            if rc != 0:
                self.log_message(f"⚠ エラー: リターンコード {rc}\n")
                messagebox.showerror("変換失敗", f"コード {rc} で終了しました。ログをご確認ください。")
                return

            self.log_message("✅ 変換完了。\n")
            # ── ここから "マルチ" 音声の抽出 ──
            multi_dir = outdir_path / "multi"
            multi_dir.mkdir(exist_ok=True)
            # V00/V01 由来の WAV をすべてコピー（ディスク1 = マルチ音声）
            copied = 0
            for wav in outdir_path.glob("*.wav"):
                name = wav.name.upper()
                if name.startswith("V00_") or name.startswith("V01_"):
                    shutil.copy(wav, multi_dir / wav.name)
                    copied += 1
            self.log_message(f"✅ マルチ音声抽出完了: {copied} files → {multi_dir}\n")
            messagebox.showinfo("完了", f"WAV変換・マルチ抽出が完了しました。\n抽出先: {multi_dir}")
        except Exception as e:
            self.log_message(f"❌ 例外発生: {e}\n")
            messagebox.showerror("例外", str(e))

    def log_message(self, msg: str):
        self.log.configure(state="normal")
        self.log.insert(tk.END, msg)
        self.log.configure(state="disabled")
        self.log.yview(tk.END)

if __name__ == "__main__":
    app = App()
    app.mainloop()
