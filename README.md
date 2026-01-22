# High Frequency Analyzer (高周波スペクトルアナライザ)
<img width="997" height="730" alt="image" src="https://github.com/user-attachments/assets/cd956f81-e68e-4b53-ad74-8a58d4cbe9b4" />

可聴域を超え、最大200kHzまでの超高音域を可視化できるスペクトルアナライザ＆オーディオプレイヤーです。
Python, PyQt6, および PortAudio (sounddevice) を使用して構築されています。

## 特徴
- **超高周波対応**: ナイキスト周波数（例：192kHz音源なら96kHz）までのスペクトルをリアルタイム表示可能。
- **デュアルモード**:
  - **File Player**: ハイレゾ音源（WAV, FLAC等）の再生と可視化。
  - **Live Input**: マイクやライン入力からの信号をリアルタイム解析（ASIO/WASAPI対応）。
- **高速起動**: スマートランチャーによる単体exe配布。初回のみ展開し、2回目以降は高速に起動します。

## 動作環境
- Windows 10/11
- 高サンプリングレート（192kHz等）に対応したオーディオインターフェース推奨

## インストール (一般ユーザー向け)
1. GitHubの [Releases](../../releases) ページから最新の `HighFreqAnalyzer.exe` をダウンロードしてください。
2. ダウンロードしたファイルを実行するだけで起動します（インストール不要）。
   - 初回起動時は展開処理のため数秒かかります。

## 開発環境セットアップ (開発者向け)
1. 依存ライブラリのインストール:
   ```bash
   pip install -r requirements.txt
   ```
2. アプリの起動:
   ```bash
   python main.py
   ```

## Windows用ビルド方法
Git Bash (MinGW64) にて以下のスクリプトを実行してください:
```bash
sh build_smart_exe.sh
```
`dist` フォルダ内に配布用ファイル `HighFreqAnalyzer.exe` が生成されます。

## Credits
本ソフトウェアは **Google Antigravity** を使用して作成されました。
This software was created using **Google Antigravity**.
