
import sys
import os
import unittest

# Add project root to path to verify imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
from database import _parse_legacy_medical_history

class TestLegacyMigrationLogic(unittest.TestCase):
    
    def test_parse_legacy_format_v1_no_spec(self):
        """Test format cũ: không có đơn vị tính"""
        input_text = "Viêm họng\n1) Panadol x 10\n2) Vitamin C x 5"
        expected = {
            'diagnosis': 'Viêm họng',
            'medicines': [
                {'name': 'Panadol', 'qty': 10, 'spec': ''},
                {'name': 'Vitamin C', 'qty': 5, 'spec': ''}
            ]
        }
        result = _parse_legacy_medical_history(input_text)
        self.assertEqual(result, expected)
        print("✅ Test v1 (No Spec): PASS")

    def test_parse_legacy_format_v2_with_spec(self):
        """Test format mới: có đơn vị tính (Viên, Vỉ...)"""
        input_text = "Sốt virus\n1) Hapacol x 12 Gói\n2) Oresol x 5 Hộp"
        expected = {
            'diagnosis': 'Sốt virus',
            'medicines': [
                {'name': 'Hapacol', 'qty': 12, 'spec': 'Gói'},
                {'name': 'Oresol', 'qty': 5, 'spec': 'Hộp'}
            ]
        }
        result = _parse_legacy_medical_history(input_text)
        self.assertEqual(result, expected)
        print("✅ Test v2 (With Spec): PASS")

    def test_parse_mixed_content(self):
        """Test nội dung hỗn hợp / lỗi format nhẹ"""
        input_text = "Khám sức khỏe\n1) Thuốc A x 10 Viên\nDòng rác không đúng format\n2) Thuốc B x 5"
        # Dòng rác bị bỏ qua, Thuốc B không có spec
        expected_meds_count = 2
        result = _parse_legacy_medical_history(input_text)
        self.assertEqual(len(result['medicines']), 2)
        self.assertEqual(result['medicines'][0]['name'], 'Thuốc A')
        self.assertEqual(result['medicines'][0]['spec'], 'Viên')
        self.assertEqual(result['medicines'][1]['name'], 'Thuốc B')
        self.assertEqual(result['medicines'][1]['spec'], '')
        print("✅ Test Mixed Data: PASS")

if __name__ == '__main__':
    print("🧪 RUNNING QUICK LOGIC TESTS...\n")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
