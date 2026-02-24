#!/bin/bash

# Đường dẫn hiện tại của project
PROJECT_DIR=$(pwd)
EXEC_PATH="$PROJECT_DIR/dist/QuanLyPhongKhamv5.0.5"
ICON_PATH="$PROJECT_DIR/logo.ico"
APP_NAME="Quan Ly Phong Kham"

# Kiểm tra file thực thi có tồn tại không
if [ ! -f "$EXEC_PATH" ]; then
    echo "⚠️ Không tìm thấy file thực thi tại dist/. Anh vui lòng build app trước nhé!"
    exit 1
fi

# Tạo file .desktop
CAT_FILE=~/.local/share/applications/quanlyphongkham.desktop

echo "[Desktop Entry]
Version=5.0.5
Type=Application
Name=$APP_NAME
Comment=Phan mem quan ly phong kham Nhi
Exec=$EXEC_PATH
Icon=$ICON_PATH
Terminal=false
Categories=Office;Medical;
Keywords=clinic;medical;doctor;
StartupNotify=true" > $CAT_FILE

# Cấp quyền thực thi cho file shortcut
chmod +x $CAT_FILE

echo "✅ Đã tạo phím tắt thành công!"
echo "📍 Vị trí: $CAT_FILE"
echo "👉 Bây giờ anh có thể nhấn phím Windows (Super) và gõ '$APP_NAME' để mở app rồi!"
