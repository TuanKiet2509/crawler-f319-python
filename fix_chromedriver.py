#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix ChromeDriver cho F319 Crawler
Script này sẽ fix lỗi "Exec format error" với ChromeDriver
"""

import os
import sys
import shutil
import requests
import zipfile
import tarfile
import platform
import subprocess
from pathlib import Path

def get_chrome_version():
    """Lấy phiên bản Chrome hiện tại"""
    try:
        # Thử các command khác nhau để lấy Chrome version
        commands = [
            "google-chrome --version",
            "chromium --version", 
            "chromium-browser --version"
        ]
        
        for cmd in commands:
            try:
                result = subprocess.run(cmd.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.strip()
                    # Extract version number
                    version_num = version.split()[-1].split('.')[0]
                    print(f"Tìm thấy Chrome version: {version_num}")
                    return version_num
            except:
                continue
        
        # Fallback version
        print("Không tìm thấy Chrome, sử dụng version mặc định: 120")
        return "120"
        
    except Exception as e:
        print(f"Lỗi khi lấy Chrome version: {e}")
        return "120"

def download_chromedriver(version="120"):
    """Tải ChromeDriver thủ công"""
    try:
        print(f"Đang tải ChromeDriver version {version} cho Linux...")
        
        # ChromeDriver URLs
        base_url = "https://chromedriver.storage.googleapis.com"
        
        # Tìm version tương ứng
        version_url = f"{base_url}/LATEST_RELEASE_{version}"
        
        try:
            response = requests.get(version_url)
            if response.status_code == 200:
                full_version = response.text.strip()
                print(f"Tìm thấy ChromeDriver version: {full_version}")
            else:
                # Fallback versions
                fallback_versions = ["120.0.6099.71", "119.0.6045.105", "118.0.5993.70"]
                full_version = fallback_versions[0]
                print(f"Sử dụng version fallback: {full_version}")
        except:
            full_version = "120.0.6099.71"
            print(f"Sử dụng version mặc định: {full_version}")
        
        # Tải file
        download_url = f"{base_url}/{full_version}/chromedriver_linux64.zip"
        print(f"Đang tải từ: {download_url}")
        
        response = requests.get(download_url)
        if response.status_code != 200:
            print(f"Không thể tải ChromeDriver. Status code: {response.status_code}")
            return None
        
        # Tạo thư mục lưu trữ
        driver_dir = Path.home() / ".chrome_driver"
        driver_dir.mkdir(exist_ok=True)
        
        # Lưu file zip
        zip_file = driver_dir / "chromedriver.zip"
        with open(zip_file, 'wb') as f:
            f.write(response.content)
        
        print(f"Đã tải xong ChromeDriver, đang giải nén...")
        
        # Giải nén
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(driver_dir)
        
        # Đặt quyền executable
        chromedriver_path = driver_dir / "chromedriver"
        if chromedriver_path.exists():
            os.chmod(chromedriver_path, 0o755)
            print(f"ChromeDriver đã được cài đặt tại: {chromedriver_path}")
            
            # Xóa file zip
            zip_file.unlink()
            
            return str(chromedriver_path)
        else:
            print("Không tìm thấy file chromedriver sau khi giải nén")
            return None
            
    except Exception as e:
        print(f"Lỗi khi tải ChromeDriver: {e}")
        return None

def clean_webdriver_cache():
    """Xóa cache của webdriver-manager"""
    try:
        print("Đang xóa cache webdriver-manager...")
        
        # Các thư mục cache có thể có
        cache_dirs = [
            Path.home() / ".wdm",
            Path.home() / ".cache" / "selenium",
            Path("/tmp/.wdm"),
            Path("/root/.wdm")
        ]
        
        for cache_dir in cache_dirs:
            if cache_dir.exists():
                print(f"Xóa: {cache_dir}")
                shutil.rmtree(cache_dir, ignore_errors=True)
        
        print("✅ Đã xóa cache webdriver-manager")
        
    except Exception as e:
        print(f"Lỗi khi xóa cache: {e}")

def install_chrome_if_needed():
    """Cài đặt Chrome nếu chưa có"""
    try:
        # Kiểm tra Chrome đã được cài đặt chưa
        result = subprocess.run(["which", "google-chrome"], capture_output=True)
        if result.returncode == 0:
            print("Chrome đã được cài đặt")
            return True
        
        # Kiểm tra Chromium
        result = subprocess.run(["which", "chromium"], capture_output=True)
        if result.returncode == 0:
            print("Chromium đã được cài đặt")
            return True
        
        print("Chrome/Chromium chưa được cài đặt")
        print("Hướng dẫn cài đặt Chrome trên Linux:")
        print("1. Ubuntu/Debian:")
        print("   wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -")
        print("   echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list")
        print("   sudo apt update && sudo apt install google-chrome-stable")
        print()
        print("2. CentOS/RHEL:")
        print("   sudo yum install -y google-chrome-stable")
        print()
        print("3. Hoặc cài Chromium:")
        print("   sudo apt install chromium-browser  # Ubuntu/Debian")
        print("   sudo yum install chromium          # CentOS/RHEL")
        
        return False
        
    except Exception as e:
        print(f"Lỗi khi kiểm tra Chrome: {e}")
        return False

def create_fixed_crawler():
    """Tạo version crawler được fix"""
    chrome_version = get_chrome_version()
    chromedriver_path = download_chromedriver(chrome_version)
    
    if not chromedriver_path:
        print("❌ Không thể tải ChromeDriver")
        return False
    
    print("Tạo version crawler đã được fix...")
    
    # Tạo file crawler mới với path cố định
    fixed_content = f'''# -*- coding: utf-8 -*-
"""
F319 Comment Crawler - Fixed Version
Crawler đã được fix lỗi ChromeDriver
"""

import time
import csv
import sys
import logging
from datetime import datetime
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import config

# FIXED: Sử dụng path cố định cho ChromeDriver
CHROMEDRIVER_PATH = "{chromedriver_path}"

class F319CrawlerFixed:
    def __init__(self):
        self.driver = None
        self.comments_data = []
        self.setup_logging()
        
    def setup_logging(self):
        """Thiết lập logging"""
        if config.ENABLE_LOGGING:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler('crawler_fixed.log', encoding='utf-8'),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self):
        """Khởi tạo Chrome driver với path cố định"""
        try:
            self.logger.info("Đang khởi tạo Chrome driver (Fixed version)...")
            chrome_options = Options()
            
            if config.HEADLESS_MODE:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            
            # FIXED: Sử dụng path cố định thay vì webdriver-manager
            service = Service(CHROMEDRIVER_PATH)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(config.BROWSER_TIMEOUT)
            
            self.logger.info("✅ Chrome driver đã được khởi tạo thành công!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi khi khởi tạo Chrome driver: {{e}}")
            return False
    
    def navigate_to_profile(self):
        """Navigate tới trang profile"""
        try:
            self.logger.info(f"Đang truy cập trang: {{config.TARGET_URL}}")
            self.driver.get(config.TARGET_URL)
            time.sleep(3)
            
            # Kiểm tra xem trang có load thành công không
            if "f319.com" in self.driver.current_url:
                self.logger.info("✅ Đã truy cập thành công trang profile!")
                return True
            else:
                self.logger.error("❌ Không thể truy cập trang profile")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Lỗi khi truy cập trang profile: {{e}}")
            return False
    
    def find_posts_tab(self):
        """Tìm và click vào tab 'Các bài đăng'"""
        try:
            self.logger.info("Đang tìm tab 'Các bài đăng'...")
            
            # Thử các selector khác nhau cho tab posts
            selectors = [
                "a[href*='#postings']",
                "a[href*='postings']",
                "a[href*='posts']", 
                ".tabs a[href*='postings']",
                ".profileTabs a[href*='postings']",
                "//a[contains(text(), 'Các bài đăng') or contains(text(), 'Bài đăng') or contains(text(), 'Posts')]"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        element = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        element = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    self.logger.info(f"✅ Tìm thấy tab posts với selector: {{selector}}")
                    element.click()
                    time.sleep(3)
                    return True
                    
                except:
                    continue
            
            self.logger.warning("⚠️ Không tìm thấy tab 'Các bài đăng', sử dụng URL trực tiếp...")
            posts_url = config.TARGET_URL.rstrip('/') + '/#postings'
            self.driver.get(posts_url)
            time.sleep(3)
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi khi tìm tab posts: {{e}}")
            return False
    
    def extract_post_links(self):
        """Extract tất cả links bài đăng"""
        try:
            self.logger.info("Đang extract links bài đăng...")
            post_links = []
            
            # Scroll để load thêm content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Tìm tất cả links bài đăng
            selectors = [
                ".title a[href*='posts/']",
                ".titleText .title a[href*='posts/']",
                "h3.title a[href*='posts/']",
                "a[href*='posts/']",
                "a[href*='/threads/']",
                ".structItem-title a",
                ".listBlock-main a[href*='threads']"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.logger.info(f"Tìm thấy {{len(elements)}} elements với selector: {{selector}}")
                    
                    for element in elements:
                        href = element.get_attribute('href')
                        if href:
                            if href.startswith('posts/'):
                                href = f"https://f319.com/{{href}}"
                            elif href.startswith('/posts/'):
                                href = f"https://f319.com{{href}}"
                            
                            if 'posts/' in href or 'threads/' in href:
                                post_links.append(href)
                                self.logger.info(f"✅ Đã thêm link: {{href}}")
                                
                except Exception as e:
                    self.logger.warning(f"⚠️ Lỗi với selector {{selector}}: {{e}}")
                    continue
            
            # Remove duplicates
            post_links = list(set(post_links))
            
            if config.MAX_POSTS_TO_CRAWL > 0:
                post_links = post_links[:config.MAX_POSTS_TO_CRAWL]
            
            self.logger.info(f"✅ Tổng cộng tìm thấy {{len(post_links)}} bài đăng unique")
            return post_links
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi khi extract post links: {{e}}")
            return []
    
    def crawl_post_comments(self, post_url):
        """Crawl comments từ một bài đăng cụ thể"""
        try:
            self.logger.info(f"Đang crawl comments từ: {{post_url}}")
            
            # Navigate tới bài đăng
            self.driver.get(post_url)
            time.sleep(config.DELAY_BETWEEN_REQUESTS)
            
            # Lấy title bài đăng
            post_title = "N/A"
            try:
                title_selectors = [
                    ".titleBar h1",
                    ".p-title-value",
                    ".thread-title",
                    "h1",
                    ".p-title h1"
                ]
                for selector in title_selectors:
                    try:
                        title_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        post_title = title_element.text.strip()
                        if post_title:
                            break
                    except:
                        continue
            except:
                pass
            
            # Extract username từ URL
            url_parts = config.TARGET_URL.split('/')
            username_with_id = url_parts[-2] if url_parts[-2] else url_parts[-3]
            username = username_with_id.split('.')[0] if '.' in username_with_id else username_with_id
            
            self.logger.info(f"Đang tìm comments của user: {{username}}")
            
            # Scroll để load tất cả comments
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scrolls = 10
            
            while scroll_attempts < max_scrolls:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_attempts += 1
            
            # Extract comments
            comment_selectors = [
                "li.message",
                ".message",
                ".post",
                "[data-author]"
            ]
            
            comments_found = 0
            
            for selector in comment_selectors:
                try:
                    comments = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.logger.info(f"Tìm thấy {{len(comments)}} comments với selector: {{selector}}")
                    
                    for comment in comments:
                        try:
                            # Kiểm tra tác giả
                            author = comment.get_attribute('data-author')
                            
                            if not author:
                                try:
                                    author_element = comment.find_element(By.CSS_SELECTOR, 
                                        ".username, .message-name a, .userText .username")
                                    author = author_element.text.strip()
                                except:
                                    continue
                            
                            # Kiểm tra comment của user target
                            if author and author.lower() == username.lower():
                                self.logger.info(f"✅ Tìm thấy comment của {{author}}")
                                
                                # Extract content
                                content_selectors = [
                                    ".messageText",
                                    ".messageText.ugc.baseHtml",
                                    "blockquote.messageText",
                                    ".message-body .bbWrapper",
                                    ".message-content",
                                    ".post-content"
                                ]
                                
                                comment_content = "N/A"
                                for content_sel in content_selectors:
                                    try:
                                        content_element = comment.find_element(By.CSS_SELECTOR, content_sel)
                                        comment_content = content_element.text.strip()
                                        if comment_content:
                                            break
                                    except:
                                        continue
                                
                                # Extract timestamp
                                time_selectors = [
                                    ".datePermalink",
                                    ".messageMeta .DateTime",
                                    ".message-date time",
                                    ".post-date",
                                    "time",
                                    ".dateTime"
                                ]
                                
                                comment_time = "N/A"
                                for time_sel in time_selectors:
                                    try:
                                        time_element = comment.find_element(By.CSS_SELECTOR, time_sel)
                                        comment_time = time_element.get_attribute('datetime') or \\
                                                     time_element.get_attribute('title') or \\
                                                     time_element.text.strip()
                                        if comment_time:
                                            break
                                    except:
                                        continue
                                
                                # Lưu comment
                                if comment_content and comment_content != "N/A":
                                    comment_data = {{
                                        'post_url': post_url,
                                        'post_title': post_title,
                                        'comment_content': comment_content,
                                        'comment_time': comment_time,
                                        'author': author
                                    }}
                                    
                                    self.comments_data.append(comment_data)
                                    comments_found += 1
                                    self.logger.info(f"✅ Đã lưu comment #{{comments_found}} từ {{author}}")
                                
                        except Exception as e:
                            self.logger.debug(f"Lỗi khi parse comment: {{e}}")
                            continue
                    
                    if comments_found > 0:
                        break
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ Lỗi với comment selector {{selector}}: {{e}}")
                    continue
            
            self.logger.info(f"✅ Tổng cộng tìm thấy {{comments_found}} comments từ {{username}} trong bài này")
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi khi crawl comments từ {{post_url}}: {{e}}")
    
    def save_to_csv(self):
        """Lưu dữ liệu vào file CSV"""
        try:
            if not self.comments_data:
                self.logger.warning("⚠️ Không có dữ liệu để lưu")
                return False
            
            output_file = "comments_data_fixed.csv"
            self.logger.info(f"Đang lưu {{len(self.comments_data)}} comments vào {{output_file}}")
            
            with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['post_url', 'post_title', 'comment_content', 'comment_time', 'author']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for comment in self.comments_data:
                    writer.writerow(comment)
            
            self.logger.info(f"✅ Đã lưu thành công dữ liệu vào {{output_file}}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi khi lưu file CSV: {{e}}")
            return False
    
    def cleanup(self):
        """Dọn dẹp resources"""
        if self.driver:
            self.driver.quit()
            self.logger.info("✅ Đã đóng browser")
    
    def run(self):
        """Chạy crawler chính"""
        try:
            self.logger.info("=== Bắt đầu F319 Crawler (Fixed Version) ===")
            
            # Setup driver
            if not self.setup_driver():
                return False
            
            # Navigate tới profile
            if not self.navigate_to_profile():
                return False
            
            # Tìm tab posts
            if not self.find_posts_tab():
                return False
            
            # Extract post links
            post_links = self.extract_post_links()
            if not post_links:
                self.logger.warning("⚠️ Không tìm thấy bài đăng nào")
                return False
            
            # Crawl từng bài đăng
            self.logger.info(f"Bắt đầu crawl {{len(post_links)}} bài đăng...")
            
            for i, post_url in enumerate(post_links, 1):
                self.logger.info(f"[{{i}}/{{len(post_links)}}] Đang crawl: {{post_url}}")
                
                for attempt in range(config.RETRY_ATTEMPTS):
                    try:
                        self.crawl_post_comments(post_url)
                        break
                    except Exception as e:
                        if attempt < config.RETRY_ATTEMPTS - 1:
                            self.logger.warning(f"⚠️ Lỗi crawl bài {{i}}, thử lại lần {{attempt + 2}}: {{e}}")
                            time.sleep(5)
                        else:
                            self.logger.error(f"❌ Không thể crawl bài {{i}} sau {{config.RETRY_ATTEMPTS}} lần thử")
                
                time.sleep(config.DELAY_BETWEEN_REQUESTS)
            
            # Lưu dữ liệu
            self.save_to_csv()
            
            self.logger.info(f"=== ✅ Hoàn thành! Đã crawl {{len(self.comments_data)}} comments ===")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi trong quá trình crawl: {{e}}")
            return False
        
        finally:
            self.cleanup()

def main():
    """Function chính"""
    print("=== F319 Comment Crawler (Fixed Version) ===")
    print(f"Target URL: {{config.TARGET_URL}}")
    print(f"ChromeDriver path: {{CHROMEDRIVER_PATH}}")
    print("=" * 50)
    
    crawler = F319CrawlerFixed()
    success = crawler.run()
    
    if success:
        print(f"\\n✅ Crawler hoàn thành thành công!")
        print(f"Dữ liệu đã được lưu trong file: comments_data_fixed.csv")
    else:
        print(f"\\n❌ Crawler gặp lỗi. Kiểm tra file log để biết thêm chi tiết.")

if __name__ == "__main__":
    main()
'''
    
    with open("f319_crawler_fixed.py", "w", encoding="utf-8") as f:
        f.write(fixed_content)
    
    print("✅ Đã tạo file f319_crawler_fixed.py")
    return True

def main():
    """Function chính"""
    print("=== Fix ChromeDriver cho F319 Crawler ===")
    print()
    
    # Kiểm tra Chrome
    if not install_chrome_if_needed():
        print("⚠️ Vui lòng cài đặt Chrome/Chromium trước khi tiếp tục")
        return
    
    # Xóa cache
    clean_webdriver_cache()
    
    # Tạo crawler fixed
    if create_fixed_crawler():
        print()
        print("✅ Fix hoàn thành!")
        print("Bạn có thể chạy crawler bằng:")
        print("python f319_crawler_fixed.py")
        print()
        print("Hoặc chạy script test:")
        print("python -c \"from f319_crawler_fixed import F319CrawlerFixed; crawler = F319CrawlerFixed(); print('✅ ChromeDriver hoạt động tốt!' if crawler.setup_driver() else '❌ Vẫn có lỗi'); crawler.cleanup()\"")
    else:
        print("❌ Có lỗi xảy ra trong quá trình fix")

if __name__ == "__main__":
    main() 