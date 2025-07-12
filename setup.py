# -*- coding: utf-8 -*-
"""
Setup Script cho F319 Crawler
Kiểm tra và cài đặt tất cả requirements
"""

import subprocess
import sys
import os
import platform

def check_python_version():
    """Kiểm tra phiên bản Python"""
    print("🐍 Kiểm tra phiên bản Python...")
    version = sys.version_info
    
    if version.major < 3:
        print("❌ Cần Python 3.0 trở lên!")
        return False
    elif version.major == 3 and version.minor < 6:
        print("⚠️ Khuyên dùng Python 3.6 trở lên để tương thích tốt nhất")
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK!")
    return True

def check_pip():
    """Kiểm tra pip"""
    print("\n📦 Kiểm tra pip...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                      check=True, capture_output=True)
        print("✅ pip - OK!")
        return True
    except:
        print("❌ pip không tìm thấy!")
        return False

def install_dependencies():
    """Cài đặt dependencies"""
    print("\n📥 Cài đặt dependencies...")
    
    if not os.path.exists('requirements.txt'):
        print("❌ Không tìm thấy file requirements.txt!")
        return False
    
    try:
        print("Đang cài đặt packages...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], check=True, capture_output=True, text=True)
        
        print("✅ Đã cài đặt dependencies thành công!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi cài đặt: {e.stderr}")
        return False

def check_chrome():
    """Kiểm tra Chrome browser"""
    print("\n🌐 Kiểm tra Chrome browser...")
    
    system = platform.system().lower()
    chrome_found = False
    
    if system == "windows":
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        chrome_found = any(os.path.exists(path) for path in chrome_paths)
    
    elif system == "darwin":  # macOS
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        ]
        chrome_found = any(os.path.exists(path) for path in chrome_paths)
    
    elif system == "linux":
        try:
            subprocess.run(['google-chrome', '--version'], 
                          check=True, capture_output=True)
            chrome_found = True
        except:
            try:
                subprocess.run(['chromium-browser', '--version'], 
                              check=True, capture_output=True)
                chrome_found = True
            except:
                chrome_found = False
    
    if chrome_found:
        print("✅ Chrome browser - OK!")
    else:
        print("⚠️ Chrome browser không tìm thấy!")
        print("Crawler sẽ tự động download ChromeDriver, nhưng cần Chrome browser")
    
    return chrome_found

def test_imports():
    """Test import các modules cần thiết"""
    print("\n🧪 Test import modules...")
    
    modules = [
        'selenium',
        'bs4',
        'requests',
        'pandas',
        'lxml'
    ]
    
    failed = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            failed.append(module)
    
    if failed:
        print(f"\n⚠️ Các modules sau chưa được cài đặt: {', '.join(failed)}")
        return False
    
    print("\n🎉 Tất cả modules đã sẵn sàng!")
    return True

def create_test_config():
    """Tạo config test nếu chưa có"""
    print("\n⚙️ Kiểm tra config...")
    
    if os.path.exists('config.py'):
        print("✅ File config.py đã tồn tại")
        return True
    else:
        print("ℹ️ File config.py sẽ được tạo khi chạy crawler")
        return True

def main():
    """Main setup function"""
    print("🚀 F319 CRAWLER SETUP")
    print("=" * 50)
    
    all_ok = True
    
    # Kiểm tra Python
    if not check_python_version():
        all_ok = False
    
    # Kiểm tra pip
    if not check_pip():
        all_ok = False
    
    # Cài đặt dependencies
    if not install_dependencies():
        all_ok = False
    
    # Test imports
    if not test_imports():
        all_ok = False
    
    # Kiểm tra Chrome
    chrome_ok = check_chrome()
    
    # Kiểm tra config
    create_test_config()
    
    print("\n" + "=" * 50)
    
    if all_ok:
        print("🎉 SETUP HOÀN THÀNH!")
        print("\n📋 Các bước tiếp theo:")
        print("1. python test_crawler.py      # Test với 3 bài đăng")
        print("2. python run_crawler.py       # Chạy với menu")
        print("3. python quick_start.py       # Chạy nhanh")
        
        if not chrome_ok:
            print("\n⚠️ Lưu ý: Hãy cài đặt Chrome browser trước khi chạy crawler")
    else:
        print("❌ SETUP GẶP VẤN ĐỀ!")
        print("Hãy khắc phục các lỗi trên trước khi tiếp tục")
    
    print("\n📖 Xem README.md để biết thêm chi tiết")

if __name__ == "__main__":
    main() 