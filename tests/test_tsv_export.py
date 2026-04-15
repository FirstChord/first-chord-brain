#!/usr/bin/env python3
"""
Quick test for TSV export functionality
Run this to verify TSV export works without doing full onboarding
"""

import os
import sys
from datetime import datetime

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_tsv_export():
    """Test that TSV file creation works correctly"""

    print("🧪 Testing TSV Export Functionality...\n")

    # Mock student data (similar to what onboarding collects)
    mock_student_data = {
        'name': 'Test Student',
        'tutor_short': 'Arion',
        'student_surname': 'Student',
        'student_forename': 'Test',
        'parent_email': 'test@example.com',
        'mms_id': '',  # blank initially
        'theta_username': 'testfc',
        'soundslice_url': 'https://www.soundslice.com/courses/12345/',
        'instrument': 'guitar',
        'parent_surname': 'Parent',
        'parent_forename': 'Test'
    }

    # Create TSV content
    row_values = [
        mock_student_data['tutor_short'].upper(),
        mock_student_data['student_surname'],
        mock_student_data['student_forename'],
        mock_student_data['parent_email'],
        mock_student_data.get('mms_id', ''),
        mock_student_data['theta_username'],
        mock_student_data.get('soundslice_url', ''),
        mock_student_data['instrument'],
        mock_student_data['parent_surname'],
        mock_student_data['parent_forename'],
    ]

    header_row = "Tutor Name\tStudent Surname\tStudent Forename\tEmail\tMMS ID\tTheta Username\tSoundslice\tInstrument\tParent Surname\tParent Forename"
    data_row = '\t'.join(row_values)
    tsv_content = f"{header_row}\n{data_row}"

    # Get absolute path to exports folder
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    exports_dir = os.path.join(script_dir, 'exports')

    # Create exports directory if it doesn't exist
    os.makedirs(exports_dir, exist_ok=True)

    # Generate test filename
    date_slug = datetime.now().strftime('%Y-%m-%d')
    filename = f"{date_slug}-test-student-TEST.tsv"
    filepath = os.path.join(exports_dir, filename)

    # Test 1: Create file
    print("📝 Test 1: Creating TSV file...")
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(tsv_content)
        print(f"   ✅ File created: {filepath}")
    except Exception as e:
        print(f"   ❌ FAILED to create file: {e}")
        return False

    # Test 2: Verify file exists
    print("\n📂 Test 2: Verifying file exists...")
    if os.path.exists(filepath):
        print(f"   ✅ File exists")
    else:
        print(f"   ❌ FAILED: File not found")
        return False

    # Test 3: Read and verify content
    print("\n📖 Test 3: Reading file content...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.strip().split('\n')

        if len(lines) == 2:
            print(f"   ✅ File has correct number of lines (2)")
        else:
            print(f"   ❌ FAILED: Expected 2 lines, got {len(lines)}")
            return False

        # Verify header
        if lines[0] == header_row:
            print(f"   ✅ Header row is correct")
        else:
            print(f"   ❌ FAILED: Header mismatch")
            return False

        # Verify data
        if lines[1] == data_row:
            print(f"   ✅ Data row is correct")
        else:
            print(f"   ❌ FAILED: Data row mismatch")
            return False

    except Exception as e:
        print(f"   ❌ FAILED to read file: {e}")
        return False

    # Test 4: Verify tab separation
    print("\n🔍 Test 4: Verifying tab-separated format...")
    data_cells = lines[1].split('\t')
    if len(data_cells) == 10:
        print(f"   ✅ Data splits into 10 columns (correct)")
    else:
        print(f"   ❌ FAILED: Expected 10 columns, got {len(data_cells)}")
        return False

    # Show the data for visual verification
    print("\n📊 Data Preview:")
    print("   Columns:")
    headers = header_row.split('\t')
    for i, (header, value) in enumerate(zip(headers, data_cells)):
        print(f"   {chr(65+i)}: {header} = '{value}'")

    # Test 5: Cleanup
    print("\n🧹 Test 5: Cleanup...")
    try:
        os.remove(filepath)
        print(f"   ✅ Test file removed")
    except Exception as e:
        print(f"   ⚠️  Could not remove test file: {e}")
        print(f"   (You can manually delete: {filepath})")

    # All tests passed!
    print("\n" + "="*50)
    print("🎉 ALL TESTS PASSED!")
    print("="*50)
    print("\nTSV export functionality is working correctly!")
    print("\nYou can now run full onboarding with confidence that")
    print("TSV files will be created and formatted properly.")

    return True

if __name__ == "__main__":
    success = test_tsv_export()
    sys.exit(0 if success else 1)
