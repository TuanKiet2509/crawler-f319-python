# -*- coding: utf-8 -*-
"""
Clean Enhanced CSV Data
Loại bỏ entries có content từ user khác, chỉ giữ lại content thực sự của target user
"""

import csv
import os
import re
from datetime import datetime

def analyze_csv_data(file_path):
    """Phân tích data để tìm potential issues"""
    print(f"🔍 === PHÂN TÍCH {file_path} ===")
    
    if not os.path.exists(file_path):
        print(f"❌ File không tồn tại: {file_path}")
        return
    
    suspicious_entries = []
    clean_entries = []
    total_entries = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for i, row in enumerate(reader, 1):
            total_entries += 1
            content = row.get('comment_content', '')
            author = row.get('author', '')
            source = row.get('source', '')
            
            # Detect suspicious content (có thể từ user khác)
            suspicious_patterns = [
                # Pattern 1: Mentions của user khác trong content
                r'@\w+',  # @username mentions
                # Pattern 2: Content quá dài unusual cho snippet
                len(content) > 500 and source == 'search_snippet',
                # Pattern 3: Content có dấu hiệu reply/quote
                'đã viết:' in content and '↑' in content,
                # Pattern 4: Content có format đặc biệt của comments dài
                '--- Gộp bài viết ---' in content
            ]
            
            is_suspicious = False
            reasons = []
            
            # Check patterns
            if re.search(r'@\w+', content):
                reasons.append("Có @mention")
            
            if len(content) > 500 and source == 'search_snippet':
                reasons.append("Snippet quá dài")
            
            if 'đã viết:' in content and '↑' in content:
                is_suspicious = True
                reasons.append("Có quote/reply format")
            
            if '--- Gộp bài viết ---' in content:
                reasons.append("Có format gộp bài")
            
            if is_suspicious or len(reasons) > 0:
                suspicious_entries.append({
                    'row_num': i,
                    'post_id': row.get('post_id', ''),
                    'post_title': row.get('post_title', '')[:50] + '...',
                    'content_preview': content[:100] + '...',
                    'source': source,
                    'reasons': reasons,
                    'full_row': row
                })
            else:
                clean_entries.append(row)
    
    print(f"📊 Kết quả phân tích:")
    print(f"  📄 Tổng entries: {total_entries}")
    print(f"  ✅ Clean entries: {len(clean_entries)}")
    print(f"  ⚠️ Suspicious entries: {len(suspicious_entries)}")
    
    return suspicious_entries, clean_entries

def show_suspicious_samples(suspicious_entries, max_show=5):
    """Hiển thị samples của suspicious entries"""
    print(f"\n⚠️ === SUSPICIOUS ENTRIES SAMPLE ===")
    
    if not suspicious_entries:
        print("✅ Không có suspicious entries!")
        return
    
    show_count = min(max_show, len(suspicious_entries))
    
    for i, entry in enumerate(suspicious_entries[:show_count]):
        print(f"\n[{i+1}] Post ID: {entry['post_id']}")
        print(f"    Title: {entry['post_title']}")
        print(f"    Content: {entry['content_preview']}")
        print(f"    Source: {entry['source']}")
        print(f"    Issues: {', '.join(entry['reasons'])}")
    
    if len(suspicious_entries) > show_count:
        print(f"\n... và {len(suspicious_entries) - show_count} entries khác")

def create_cleaned_csv(original_file, clean_entries, suspicious_entries):
    """Tạo file CSV đã clean"""
    if not clean_entries:
        print("❌ Không có clean entries để lưu!")
        return False
    
    # Tạo file clean
    clean_file = original_file.replace('.csv', '_cleaned.csv')
    with open(clean_file, 'w', newline='', encoding='utf-8') as f:
        if clean_entries:
            fieldnames = clean_entries[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(clean_entries)
    
    print(f"✅ Đã tạo file clean: {clean_file}")
    
    # Tạo file suspicious để review
    if suspicious_entries:
        suspicious_file = original_file.replace('.csv', '_suspicious.csv')
        with open(suspicious_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = suspicious_entries[0]['full_row'].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for entry in suspicious_entries:
                writer.writerow(entry['full_row'])
        
        print(f"⚠️ Đã tạo file suspicious để review: {suspicious_file}")
    
    return True

def main():
    """Main function"""
    print("🧹 === CLEAN ENHANCED CSV DATA ===")
    print("Loại bỏ content từ user khác")
    print("=" * 50)
    
    # Tìm file enhanced CSV
    enhanced_files = []
    for file in os.listdir('.'):
        if file.endswith('_enhanced.csv'):
            enhanced_files.append(file)
    
    if not enhanced_files:
        print("❌ Không tìm thấy file enhanced CSV nào")
        return
    
    print("📁 Enhanced CSV files tìm thấy:")
    for i, file in enumerate(enhanced_files, 1):
        print(f"  {i}. {file}")
    
    if len(enhanced_files) == 1:
        selected_file = enhanced_files[0]
        print(f"🎯 Tự động chọn: {selected_file}")
    else:
        choice = input(f"\n📋 Chọn file để clean (1-{len(enhanced_files)}): ").strip()
        try:
            file_index = int(choice) - 1
            if 0 <= file_index < len(enhanced_files):
                selected_file = enhanced_files[file_index]
            else:
                print("❌ Lựa chọn không hợp lệ")
                return
        except ValueError:
            print("❌ Lựa chọn không hợp lệ")
            return
    
    print(f"\n🔍 Đang phân tích: {selected_file}")
    suspicious_entries, clean_entries = analyze_csv_data(selected_file)
    
    if suspicious_entries:
        show_suspicious_samples(suspicious_entries)
        
        print(f"\n🤔 Tìm thấy {len(suspicious_entries)} suspicious entries.")
        print("Những entries này có thể chứa content từ user khác.")
        
        choice = input("\n🧹 Tạo file cleaned (chỉ giữ clean entries)? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            create_cleaned_csv(selected_file, clean_entries, suspicious_entries)
            
            print(f"\n📊 === SUMMARY ===")
            print(f"Original: {len(clean_entries) + len(suspicious_entries)} entries")
            print(f"Cleaned: {len(clean_entries)} entries")
            print(f"Removed: {len(suspicious_entries)} entries")
            print(f"Success rate: {len(clean_entries)/(len(clean_entries) + len(suspicious_entries))*100:.1f}%")
        else:
            print("❌ Không tạo file cleaned")
    else:
        print("🎉 Không có suspicious entries! File CSV đã clean.")

if __name__ == "__main__":
    main() 