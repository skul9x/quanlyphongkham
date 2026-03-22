# 📦 Quy trình Đóng gói & Đẩy code lên GitHub

Dưới đây là các bước chuẩn để AI thực hiện việc đóng gói ứng dụng (build .deb) và đồng bộ code lên GitHub.

## 🛠️ Bước 1: Build & Đóng gói (.deb)

AI cần thực hiện chuỗi lệnh sau để đảm bảo PyInstaller build lại từ mã nguồn mới nhất:

```bash
# Di chuyển vào thư mục dự án (nếu cần)
cd ~/Desktop/Test_code/quanlyphongkham-Supabase-v2

# 1. Xóa file thực thi cũ để buộc PyInstaller build lại
rm -f dist/QuanLyPhongKhamv5.0.6

# 2. Chạy script đóng gói (Script này sẽ tự gọi PyInstaller và tạo file .deb)
bash build_deb.sh

# 3. Cài đặt lại file .deb vừa tạo vào hệ thống
sudo dpkg -i quanlyphongkham_5.0.6_amd64.deb
```

---

## 🚀 Bước 2: Đẩy code lên GitHub (Dành cho AI)

Khi đẩy code, AI phải sử dụng **Personal Access Token (PAT)** đã được Bệ hạ cấp:

### 🔑 Thông tin xác thực:
- **GitHub Token:** `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`

### 📋 Quy trình Push Code:
AI cần hỏi rõ User thông tin sau trước khi thực hiện lệnh push:
1. **Repository URL:** (Ví dụ: `https://github.com/skul9x/quanlyphongkham.git`)
2. **Branch name:** (Ví dụ: `Supabase-v2`)

**Lệnh mẫu để AI thực hiện:**
```bash
# AI cần thay thế [TOKEN], [REPO_URL], [BRANCH] tương ứng
git add -A
git commit -m "Mô tả thay đổi cụ thể"
git push https://[TOKEN]@[REPO_URL_WITHOUT_HTTPS] [BRANCH]
```

> [!IMPORTANT]
> **Lưu ý cho AI:** Luôn kiểm tra `git status` và giải quyết các xung đột (conflicts) bằng cách ưu tiên giữ lại code local (ours) nếu cần thiết trước khi push.
