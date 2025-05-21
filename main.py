import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path

# PAK→exe 変換ロジック
# ・V00～V09 またはそれ以外の数字三桁は thv.exe
# ・072 は thv072.exe
# ・073 は thv07273.exe

def choose_exe(pak_path: Path) -> Path:
    """PAK ファイル名で使用する exe の Path を返す"""
    stem = pak_path.stem.upper()
    exe_name = None
    if stem.isdigit():
        if stem == '072':
            exe_name = 'thv072.exe'
        elif stem == '073':
            exe_name = 'thv07273.exe'
        else:
            exe_name = 'thv.exe'
    elif stem.startswith('V') and len(stem) == 3 and stem[1:].isdigit():
        exe_name = 'thv.exe'
    else:
        raise ValueError(f"PAK ファイル名 '{stem}' の形式が不明です。")
    exe_path = Path(__file__).parent / exe_name
    if not exe_path.exists():
        raise FileNotFoundError(f"'{exe_name}' が見つかりません。スクリプトと同じフォルダに配置してください。")
    return exe_path

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ToHeart PAK→WAV コンバータ")
        self.geometry("650x450")
        self.create_widgets()

    def create_widgets(self):
        # PAK ファイル選択
        file_frame = tk.Frame(self)
        file_frame.pack(pady=5, fill='x')
        tk.Label(file_frame, text="PAK ファイル:").pack(side=tk.LEFT, padx=5)
        self.file_var = tk.StringVar()
        tk.Entry(file_frame, textvariable=self.file_var, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="選択…", command=self.select_file).pack(side=tk.LEFT)

        # 出力フォルダ選択
        out_frame = tk.Frame(self)
        out_frame.pack(pady=5, fill='x')
        tk.Label(out_frame, text="出力フォルダ:").pack(side=tk.LEFT, padx=5)
        self.outdir_var = tk.StringVar(value=str(Path.cwd()))
        tk.Entry(out_frame, textvariable=self.outdir_var, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(out_frame, text="選択…", command=self.select_outdir).pack(side=tk.LEFT)

        # 実行ボタン
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="変換実行", command=self.start_conversion).pack()

        # ログ表示
        self.log = scrolledtext.ScrolledText(self, state='disabled', wrap='word')
        self.log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def select_file(self):
        path = filedialog.askopenfilename(
            title="PAK ファイルを選択",
            filetypes=[("PAK files", "*.PAK"), ("All files", "*")]
        )
        if path:
            self.file_var.set(path)

    def select_outdir(self):
        path = filedialog.askdirectory(
            title="出力フォルダを選択",
            initialdir=self.outdir_var.get() or Path.cwd()
        )
        if path:
            self.outdir_var.set(path)

    def start_conversion(self):
        pak = self.file_var.get().strip()
        outdir = self.outdir_var.get().strip()
        if not pak:
            messagebox.showwarning("警告", "PAK ファイルを選択してください。")
            return
        if not outdir:
            messagebox.showwarning("警告", "出力フォルダを選択してください。")
            return
        pak_path = Path(pak)
        outdir_path = Path(outdir)
        if not pak_path.exists():
            messagebox.showerror("エラー", f"ファイルが見つかりません: {pak}")
            return
        if not outdir_path.exists():
            try:
                outdir_path.mkdir(parents=True)
            except Exception as e:
                messagebox.showerror("エラー", f"出力フォルダを作成できません: {e}")
                return
        try:
            exe_path = choose_exe(pak_path)
        except Exception as e:
            messagebox.showerror("エラー", str(e))
            return
        threading.Thread(
            target=self.run_process,
            args=(exe_path, pak_path, outdir_path),
            daemon=True
        ).start()

    def run_process(self, exe_path: Path, pak_path: Path, outdir_path: Path):
        self.log_message(f"実行: {exe_path.name} {pak_path}\n")
        # 実行前の出力ディレクトリ一覧
        exe_dir = exe_path.parent
        before = set(exe_dir.glob('*.wav'))
        try:
            proc = subprocess.Popen(
                [str(exe_path), str(pak_path)],
                cwd=str(exe_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            if proc.stdout is not None:
                for line in proc.stdout:
                    self.log_message(line)
            else:
                out, _ = proc.communicate()
                self.log_message(out)
            rc = proc.wait()
            # 生成されたwavを移動
            after = set(exe_dir.glob('*.wav'))
            new_files = after - before
            for wav in new_files:
                wav.rename(outdir_path / wav.name)
            if rc == 0:
                self.log_message("完了。\n")
                messagebox.showinfo("完了", f"{outdir_path} に WAV ファイルを出力しました。")
            else:
                self.log_message(f"エラー: リターンコード {rc}\n")
                messagebox.showerror(
                    "エラー",
                    f"変換に失敗しました (コード: {rc})。詳細はログをご確認ください。"
                )
        except Exception as e:
            self.log_message(f"例外: {e}\n")
            messagebox.showerror("例外", str(e))

    def log_message(self, msg: str):
        self.log.configure(state='normal')
        self.log.insert(tk.END, msg)
        self.log.configure(state='disabled')
        self.log.yview(tk.END)

if __name__ == "__main__":
    app = App()
    app.mainloop()
