# -*- coding: utf-8 -*-
"""
Fix Dependencies Script
Giải quyết lỗi conflict khi cài đặt Flask dependencies
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Chạy command với error handling"""
    print(f"\n🔧 {description}")
    print(f"📋 Chạy: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Thành công!")
            return True
        else:
            print(f"⚠️ Có warning: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def main():
    """Fix dependencies và test web interface"""
    print("🔧 === FIX DEPENDENCIES SCRIPT ===")
    print("Giải quyết lỗi blinker conflict")
    print("=" * 50)
    
    # Method 1: Upgrade pip first
    print("\n📦 === PHƯƠNG ÁN 1: UPGRADE PIP ===")
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrade pip")
    
    # Method 2: Install specific packages that are causing issues
    print("\n📦 === PHƯƠNG ÁN 2: INSTALL CORE PACKAGES ===")
    core_packages = [
        "itsdangerous",
        "click", 
        "Jinja2",
        "MarkupSafe"
    ]
    
    for package in core_packages:
        run_command(f"{sys.executable} -m pip install --upgrade {package}", f"Install {package}")
    
    # Method 3: Force install Flask with no-deps
    print("\n📦 === PHƯƠNG ÁN 3: FORCE INSTALL FLASK ===")
    flask_cmd = f"{sys.executable} -m pip install --force-reinstall --no-deps Flask==3.0.0"
    run_command(flask_cmd, "Force install Flask")
    
    werkzeug_cmd = f"{sys.executable} -m pip install --force-reinstall --no-deps Werkzeug==3.0.1"
    run_command(werkzeug_cmd, "Force install Werkzeug")
    
    # Method 4: Install blinker separately
    print("\n📦 === PHƯƠNG ÁN 4: INSTALL BLINKER ===")
    blinker_cmd = f"{sys.executable} -m pip install --upgrade --force-reinstall blinker"
    run_command(blinker_cmd, "Install blinker")
    
    # Method 5: Test import
    print("\n🧪 === TEST IMPORTS ===")
    try:
        import flask
        print("✅ Flask import: OK")
        print(f"📋 Flask version: {flask.__version__}")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        from enhanced_f319_crawler import EnhancedF319Crawler
        print("✅ Enhanced Crawler import: OK")
    except ImportError as e:
        print(f"❌ Enhanced Crawler import failed: {e}")
        print("📋 Đảm bảo file enhanced_f319_crawler.py tồn tại")
        return False
    
    # Test web app import
    try:
        from app import app
        print("✅ Flask app import: OK")
    except ImportError as e:
        print(f"❌ Flask app import failed: {e}")
        return False
    
    print(f"\n🎉 === DEPENDENCIES ĐÃ ĐƯỢC FIX! ===")
    print("✅ Tất cả packages đã sẵn sàng")
    print("🌐 Có thể chạy web interface bây giờ")
    
    # Option to run web interface
    choice = input("\n🚀 Chạy web interface ngay bây giờ? (y/n): ").strip().lower()
    if choice in ['y', 'yes']:
        print("\n🔥 Đang khởi động web interface...")
        try:
            app.run(debug=True, host='0.0.0.0', port=5000)
        except KeyboardInterrupt:
            print("\n👋 Đã dừng web interface!")
        except Exception as e:
            print(f"\n❌ Lỗi: {e}")
    else:
        print("\n📋 Để chạy web interface:")
        print("   python app.py")
        print("   hoặc python run_web.py")
        print("   hoặc python quick_start_web.py")
    
    return True

if __name__ == "__main__":
    main() 