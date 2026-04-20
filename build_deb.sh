#!/bin/bash

# 1. Cấu hình thông tin
PACKAGE_NAME="quanlyphongkham"
# VERSION="5.2.0"
VERSION=$(python3 -c "import config; print(config.APP_VERSION)")
ARCH="amd64"
STAGING_DIR="deb_build"
EXE_NAME="QuanLyPhongKhamv${VERSION}"

echo "🚀 Bắt đầu đóng gói .deb cho $PACKAGE_NAME v$VERSION..."

# 2. Xóa và tạo lại thư mục đóng gói
rm -rf $STAGING_DIR
mkdir -p $STAGING_DIR/DEBIAN
mkdir -p $STAGING_DIR/usr/bin
mkdir -p $STAGING_DIR/usr/share/applications
mkdir -p $STAGING_DIR/usr/share/pixmaps
mkdir -p $STAGING_DIR/opt/$PACKAGE_NAME

# 3. Tạo file control (Metadata của gói)
cat <<EOF > $STAGING_DIR/DEBIAN/control
Package: $PACKAGE_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Maintainer: Nguyen Duy Truong <skul9x@gmail.com>
Description: Phan mem Quan ly Phong kham Nhi version $VERSION
 🤖 Ho tro dong bo Cloud Supabase va quan ly benh nhan chuyen nghiep.
EOF

# 4. Kiểm tra và Copy file thực thi
if [ ! -f "dist/$EXE_NAME" ]; then
    echo "⚠️ Không tìm thấy file 'dist/$EXE_NAME'. Đang tiến hành build PyInstaller trước..."
    
    # Tìm đường dẫn plugin iBus (để hỗ trợ gõ tiếng Việt)
    IBUS_PLUGIN=$(find venv/lib -name "libibusplatforminputcontextplugin.so" | head -n 1)
    
    if [ -z "$IBUS_PLUGIN" ]; then
        echo "❌ Lỗi: Không tìm thấy libibusplatforminputcontextplugin.so trong venv."
        echo "Vui lòng chạy: ./venv/bin/pip install PySide6"
        exit 1
    fi

    ./venv/bin/pyinstaller --noconfirm --name "$EXE_NAME" --onefile --windowed \
        --icon=logo.ico \
        --add-data "logo.ico:." \
        --add-data "drugs.json:." \
        --add-binary "$IBUS_PLUGIN:PySide6/Qt/plugins/platforminputcontexts/" \
        --hidden-import pytz \
        --hidden-import supabase \
        --hidden-import postgrest \
        --hidden-import httpx \
        --hidden-import openpyxl \
        main_pyside.py
fi

cp dist/$EXE_NAME $STAGING_DIR/opt/$PACKAGE_NAME/
cp logo.ico $STAGING_DIR/usr/share/pixmaps/quanlyphongkham.ico

# 5. Tạo lệnh thực thi trong /usr/bin (wrapper script)
cat > $STAGING_DIR/usr/bin/$PACKAGE_NAME <<WRAPPER
#!/bin/bash
export QT_IM_MODULE=ibus
export XMODIFIERS=@im=ibus
export GTK_IM_MODULE=ibus
export IBUS_ENABLE_SYNC_MODE=1
/opt/$PACKAGE_NAME/$EXE_NAME "\$@"
WRAPPER
chmod +x $STAGING_DIR/usr/bin/$PACKAGE_NAME

# 6. Tạo file .desktop (Icon trong Menu)
cat <<EOF > $STAGING_DIR/usr/share/applications/quanlyphongkham.desktop
[Desktop Entry]
Version=$VERSION
Type=Application
Name=Quan Ly Phong Kham
Comment=Phan mem quan ly phong kham
Exec=$PACKAGE_NAME
Icon=/usr/share/pixmaps/quanlyphongkham.ico
Terminal=false
Categories=Office;Medical;
EOF

# 7. Đóng gói thành file .deb
dpkg-deb --build $STAGING_DIR

# 8. Đổi tên file cho dễ nhìn
mv deb_build.deb ${PACKAGE_NAME}_${VERSION}_${ARCH}.deb

echo "--------------------------------------------------"
echo "✅ HOÀN TẤT! Đã tạo xong file cài đặt:"
echo "👉 ${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
echo ""
echo "Để cài đặt, anh chạy lệnh:"
echo "sudo dpkg -i ${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
echo "Sau đó anh có thể tìm app trong menu Ubuntu rồi!"
