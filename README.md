# ToHeart PAK→WAV Converter GUI

This Python/Tkinter application provides a user-friendly GUI for extracting WAV audio files from PS版ToHeart PAK data files using the original `thv.exe`, `thv072.exe`, and `thv07273.exe` tools.

## Features

* **Automatic EXE selection** based on PAK filename:

  * `thv.exe` for general PAK files (数字3桁 or V00–V09)
  * `thv072.exe` for `072.PAK`
  * `thv07273.exe` for `073.PAK`
* **PAK File Picker**: Select `.PAK` files via file dialog.
* **Output Directory Picker**: Choose where to save extracted WAV files.
* **Log Viewer**: Real-time display of conversion logs within the UI.
* **Robust Error Handling**:

  * Missing EXE lookup
  * Directory creation failures
  * Conversion failures with detailed error dialogs
* **Safe WAV Transfer**:

  * Runs the EXE in its own directory
  * Moves only newly generated `.wav` files into the user-selected folder

## Requirements

* Python 3.6+
* Tkinter (bundled with standard Python)
* Place the following executables in the same directory as `main.py`:

  * `thv.exe`
  * `thv072.exe`
  * `thv07273.exe`

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/Emon2358/thv-on-windows.git
   cd thv-on-windows
   ```
2. Ensure the PAK→WAV EXE tools are placed alongside the script.
3. (Optional) Create a Python virtual environment and install any dependencies.

## Usage

```bash
python main.py
```

1. Click **PAK ファイル…** to select your `.PAK` file (e.g., `D:\PAK\000.PAK`).
2. Click **出力フォルダ…** to choose where to save the WAV files.
3. Press **変換実行**. Logs will appear in the panel and a dialog will notify you upon completion.

## Troubleshooting

* **EXE not found**: Ensure `thv.exe`, `thv072.exe`, and `thv07273.exe` are in the same directory as the script.
* **Conversion Errors (non-zero exit codes)**: Check the log panel for details and verify the PAK file integrity.
* **Permission Issues**: Run the script with sufficient permissions to read the PAK file and write to the output folder.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for more information.

## Acknowledgments

* Original tool by えいさあ (1999)
* VB file format documentation by 山崎 淳氏
