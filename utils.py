# utils.py
# Chứa các hàm tiện ích

import unicodedata
from datetime import datetime

def calculate_age(dob_str):
    """
    Tính tuổi từ ngày sinh (định dạng YYYY-MM-DD) theo quy tắc:
    dưới 2 tháng hiển thị ngày, dưới 6 tuổi hiển thị tháng, trên 6 tuổi hiển thị năm.
    """
    if not dob_str:
        return ""
    try:
        dob_date = datetime.strptime(dob_str, '%Y-%m-%d')
        today = datetime.now()
        age_days = (today - dob_date).days

        if age_days < 0: # Xử lý trường hợp ngày sinh trong tương lai
             return "Ngày sinh không hợp lệ"
        elif age_days < 60:  # Dưới 2 tháng
            return f"{age_days} ngày"
        elif age_days < 2190:  # Dưới 6 tuổi (6 * 365.25 ≈ 2190)
            months = age_days // 30 # Ước lượng
            # Cân nhắc tính chính xác hơn nếu cần
            # delta = today - dob_date
            # months = delta.days // 30 # Cách tính đơn giản
            # Hoặc tính chính xác hơn:
            # years = today.year - dob_date.year
            # months = today.month - dob_date.month
            # if today.day < dob_date.day:
            #     months -= 1
            # total_months = years * 12 + months
            return f"{months} tháng"
        else:
            years = age_days // 365 # Ước lượng
            # years = today.year - dob_date.year
            # if (today.month, today.day) < (dob_date.month, dob_date.day):
            #     years -= 1
            return f"{years} tuổi"
    except ValueError:
        # Có thể là dữ liệu cũ không đúng định dạng YYYY-MM-DD
        # hoặc các định dạng như "3 tháng", "5 tuổi" đã lưu trước đó
        return dob_str # Trả về giá trị gốc nếu không thể phân tích

def format_address(address):
    """
    Định dạng địa chỉ: viết hoa chữ cái đầu mỗi từ, xử lý một số trường hợp đặc biệt.
    """
    if not address:
        return ""
    address = address.lower()
    special_cases = {
        'tp.': 'TP.', 'q.': 'Q.', 'p.': 'P.', 'h.': 'H.',
        'x.': 'X.', 'thôn': 'Thôn', 'đường': 'Đường', 'kp.': 'KP.'
        # Thêm các trường hợp khác nếu cần
    }
    parts = []
    for part in address.split():
        if part in special_cases:
            parts.append(special_cases[part])
        else:
            # Xử lý số nhà/tên đường có số: 123/45a -> giữ nguyên
            if any(char.isdigit() for char in part) and any(char == '/' or char.isalpha() for char in part):
                 parts.append(part)
            else:
                parts.append(part.title())
    return ' '.join(parts)

def remove_diacritics(text: str) -> str:
    """
    Xóa dấu tiếng Việt khỏi chuỗi.
    Ví dụ: "Nguyễn Văn An" -> "Nguyen Van An"
    """
    if not text:
        return ""
    # Chuẩn hóa Unicode về dạng NFD (Canonical Decomposition)
    # Sau đó loại bỏ các ký tự đánh dấu (Mark, Nonspacing) - Mn
    # Chuyển 'đ' và 'Đ' thành 'd' và 'D' trước khi chuẩn hóa
    text = text.replace('đ', 'd').replace('Đ', 'D')
    normalized_text = unicodedata.normalize('NFD', text)
    stripped_text = ''.join(c for c in normalized_text if unicodedata.category(c) != 'Mn')
    return stripped_text

def get_vietnamese_weekday(date_obj):
    """Trả về tên thứ trong tuần bằng tiếng Việt từ đối tượng datetime."""
    weekdays = {
        0: 'Thứ 2', 1: 'Thứ 3', 2: 'Thứ 4',
        3: 'Thứ 5', 4: 'Thứ 6', 5: 'Thứ 7', 6: 'Chủ nhật'
    }
    return weekdays.get(date_obj.weekday(), '')

def format_date_dmy(date_str):
    """Chuyển đổi chuỗi ngày YYYY-MM-DD sang DD/MM/YYYY."""
    if not date_str:
        return ""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d/%m/%Y')
    except (ValueError, TypeError):
        return date_str # Trả về chuỗi gốc nếu không thể chuyển đổi