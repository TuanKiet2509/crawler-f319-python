# -*- coding: utf-8 -*-
"""
Enhanced F319 Comment Crawler
Sử dụng search approach hiệu quả hơn
"""

import time
import csv
import sys
import logging
import re
import zipfile
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import config

class EnhancedF319Crawler:
    def __init__(self):
        self.driver = None
        self.comments_data = []
        self.search_base_url = None
        self.user_id = None
        self.username = None
        self.setup_logging()
        
    def setup_logging(self):
        """Thiết lập logging"""
        if config.ENABLE_LOGGING:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler('enhanced_crawler.log', encoding='utf-8'),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self):
        """Khởi tạo Chrome driver"""
        try:
            self.logger.info("🚀 Đang khởi tạo Chrome driver...")
            chrome_options = Options()
            
            if config.HEADLESS_MODE:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            # FIX: Thêm fallback options khi webdriver-manager thất bại
            driver_path = None
            
            try:
                # Thử webdriver-manager trước
                self.logger.info("🔧 Thử sử dụng webdriver-manager...")
                wdm_path = ChromeDriverManager().install()
                
                # FIX: Kiểm tra xem WebDriver Manager có trả về đúng file không
                import os
                from pathlib import Path
                
                # Kiểm tra xem file có phải là chromedriver thật không
                # Không chỉ kiểm tra tên file mà còn kiểm tra có thể thực thi
                is_valid_chromedriver = False
                
                # Kiểm tra nếu file có tên chính xác là 'chromedriver' (không có extension)
                if Path(wdm_path).name == 'chromedriver':
                    if os.path.exists(wdm_path) and os.access(wdm_path, os.X_OK):
                        driver_path = wdm_path
                        is_valid_chromedriver = True
                        self.logger.info(f"✅ Sử dụng ChromeDriver từ webdriver-manager: {driver_path}")
                
                # Nếu WebDriver Manager trả về file sai
                if not is_valid_chromedriver:
                    self.logger.warning(f"⚠️ WebDriver Manager trả về file không hợp lệ: {wdm_path}")
                    
                    # Tìm file chromedriver thật trong cùng thư mục
                    wdm_dir = Path(wdm_path).parent
                    possible_paths = [
                        wdm_dir / "chromedriver",
                        wdm_dir / "chromedriver-linux64" / "chromedriver",
                        wdm_dir.parent / "chromedriver",
                    ]
                    
                    for possible_path in possible_paths:
                        if possible_path.exists() and possible_path.name == 'chromedriver':
                            # Đảm bảo file có quyền thực thi
                            if not os.access(possible_path, os.X_OK):
                                self.logger.info(f"🔧 Đặt quyền thực thi cho: {possible_path}")
                                os.chmod(possible_path, 0o755)
                            
                            if os.access(possible_path, os.X_OK):
                                driver_path = str(possible_path)
                                self.logger.info(f"✅ Tìm thấy ChromeDriver đúng: {driver_path}")
                                break
                    
                    if not driver_path:
                        self.logger.warning("⚠️ Không tìm thấy file chromedriver thật")
                        driver_path = None
                    
            except Exception as e:
                self.logger.warning(f"⚠️ webdriver-manager thất bại: {e}")
                driver_path = None
            
            # Fallback: Tìm chromedriver trong system PATH
            if not driver_path:
                self.logger.info("🔍 Tìm chromedriver trong system PATH...")
                import shutil
                system_driver = shutil.which('chromedriver')
                if system_driver:
                    driver_path = system_driver
                    self.logger.info(f"✅ Tìm thấy chromedriver system: {driver_path}")
                else:
                    self.logger.warning("⚠️ Không tìm thấy chromedriver trong PATH")
            
            # Fallback: Tải chromedriver thủ công
            if not driver_path:
                self.logger.info("📥 Tải chromedriver thủ công...")
                driver_path = self.download_chromedriver_manual()
            
            # Tạo service và driver
            if driver_path:
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.driver.set_page_load_timeout(config.BROWSER_TIMEOUT)
                
                self.logger.info("✅ Chrome driver đã được khởi tạo thành công!")
                return True
            else:
                self.logger.error("❌ Không thể tìm thấy ChromeDriver")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Lỗi khi khởi tạo Chrome driver: {e}")
            return False
    
    def download_chromedriver_manual(self):
        """Tải ChromeDriver thủ công nếu webdriver-manager thất bại"""
        try:
            import os
            import requests
            import zipfile
            from pathlib import Path
            
            self.logger.info("🔄 Đang tải ChromeDriver thủ công...")
            
            # Tạo thư mục lưu trữ
            driver_dir = Path.home() / ".chrome_driver_manual"
            driver_dir.mkdir(exist_ok=True)
            
            # Kiểm tra xem đã có file chưa
            chromedriver_path = driver_dir / "chromedriver"
            if chromedriver_path.exists() and os.access(chromedriver_path, os.X_OK):
                self.logger.info(f"✅ Sử dụng ChromeDriver đã có: {chromedriver_path}")
                return str(chromedriver_path)
            
            # Tải ChromeDriver mới
            chrome_version = "120.0.6099.71"  # Stable version
            download_url = f"https://chromedriver.storage.googleapis.com/{chrome_version}/chromedriver_linux64.zip"
            
            self.logger.info(f"📥 Tải từ: {download_url}")
            
            response = requests.get(download_url, timeout=30)
            if response.status_code == 200:
                # Lưu và giải nén
                zip_file = driver_dir / "chromedriver.zip"
                with open(zip_file, 'wb') as f:
                    f.write(response.content)
                
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(driver_dir)
                
                # Đặt quyền executable
                os.chmod(chromedriver_path, 0o755)
                zip_file.unlink()  # Xóa file zip
                
                self.logger.info(f"✅ ChromeDriver đã được tải về: {chromedriver_path}")
                return str(chromedriver_path)
            else:
                self.logger.error(f"❌ Không thể tải ChromeDriver: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Lỗi khi tải ChromeDriver thủ công: {e}")
            return None
    
    def extract_user_info(self):
        """Extract user ID và username từ profile URL"""
        try:
            self.logger.info(f"🔍 Đang extract thông tin user từ: {config.TARGET_URL}")
            
            # Extract user ID từ URL: members/lamnguyenphu.493993/ → 493993
            url_parts = config.TARGET_URL.split('/')
            username_with_id = url_parts[-2] if url_parts[-2] else url_parts[-3]
            
            # Extract user ID (phần sau dấu .)
            if '.' in username_with_id:
                parts = username_with_id.split('.')
                self.username = parts[0]  # lamnguyenphu
                self.user_id = parts[1]   # 493993
            else:
                self.logger.error("❌ Không thể extract user ID từ URL")
                return False
            
            self.logger.info(f"✅ Username: {self.username}")
            self.logger.info(f"✅ User ID: {self.user_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi khi extract user info: {e}")
            return False
    
    def construct_search_url(self):
        """Construct URL tìm kiếm tất cả bài đăng của user"""
        try:
            # URL search format: https://f319.com/search/member?user_id=493993
            base_domain = "https://f319.com"
            search_url = f"{base_domain}/search/member?user_id={self.user_id}"
            
            self.search_base_url = search_url
            self.logger.info(f"🎯 Search URL: {search_url}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi khi construct search URL: {e}")
            return False
    
    def navigate_to_search(self):
        """Navigate tới trang search"""
        try:
            self.logger.info(f"📋 Đang truy cập search page...")
            self.driver.get(self.search_base_url)
            time.sleep(3)
            
            # Kiểm tra xem có load thành công không
            if "search" in self.driver.current_url.lower():
                self.logger.info("✅ Đã truy cập thành công search page!")
                return True
            else:
                self.logger.error("❌ Không thể truy cập search page")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Lỗi khi navigate tới search: {e}")
            return False
    
    def detect_pagination(self):
        """Detect tổng số trang từ pagination"""
        try:
            self.logger.info("📊 Đang detect pagination...")
            
            # Tìm pagination element
            pagination_selectors = [
                ".PageNav",
                ".pageNav",
                "[data-last]",
                ".pagination"
            ]
            
            total_pages = 1  # Default là 1 page
            
            for selector in pagination_selectors:
                try:
                    pagination = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    # Thử lấy từ data-last attribute
                    data_last = pagination.get_attribute('data-last')
                    if data_last and data_last.isdigit():
                        total_pages = int(data_last)
                        self.logger.info(f"✅ Tìm thấy pagination từ data-last: {total_pages} trang")
                        break
                    
                    # Thử tìm từ text content
                    page_text = pagination.text
                    page_match = re.search(r'Trang\s+\d+/(\d+)', page_text)
                    if page_match:
                        total_pages = int(page_match.group(1))
                        self.logger.info(f"✅ Tìm thấy pagination từ text: {total_pages} trang")
                        break
                    
                except:
                    continue
            
            self.logger.info(f"📄 Tổng số trang để crawl: {total_pages}")
            return total_pages
            
        except Exception as e:
            self.logger.warning(f"⚠️ Không detect được pagination: {e}")
            return 1
    
    def extract_posts_from_search_page(self, page_num=1):
        """Extract tất cả posts từ search results page"""
        try:
            self.logger.info(f"📋 Đang extract posts từ page {page_num}...")
            posts_data = []
            
            # Tìm search results container
            results_selectors = [
                "ol.searchResultsList li.searchResult",
                ".searchResults li.searchResult", 
                ".searchResultsList .searchResult",
                "[data-author]"
            ]
            
            search_results = []
            for selector in results_selectors:
                try:
                    results = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if results:
                        search_results = results
                        self.logger.info(f"✅ Tìm thấy {len(results)} results với selector: {selector}")
                        break
                except:
                    continue
            
            if not search_results:
                self.logger.warning(f"⚠️ Không tìm thấy search results trên page {page_num}")
                return posts_data
            
            # Extract từng post
            for i, result in enumerate(search_results, 1):
                try:
                    # Kiểm tra author
                    author = result.get_attribute('data-author')
                    if not author or author.lower() != self.username.lower():
                        continue
                    
                    # Extract post ID
                    post_id = result.get_attribute('id')
                    if post_id:
                        post_id = post_id.replace('post-', '')
                    
                    # Extract title và URL
                    title_element = result.find_element(By.CSS_SELECTOR, "h3.title a, .title a")
                    post_title = title_element.text.strip()
                    post_url = title_element.get_attribute('href')
                    
                    # Convert relative URL to absolute
                    if post_url.startswith('posts/'):
                        post_url = f"https://f319.com/{post_url}"
                    elif post_url.startswith('/posts/'):
                        post_url = f"https://f319.com{post_url}"
                    
                    # Extract snippet content
                    snippet_content = "N/A"
                    try:
                        snippet_element = result.find_element(By.CSS_SELECTOR, "blockquote.snippet, .snippet")
                        snippet_content = snippet_element.text.strip()
                    except:
                        pass
                    
                    # Extract time
                    post_time = "N/A"
                    try:
                        time_selectors = [
                            ".DateTime",
                            "[data-time]",
                            ".meta time",
                            "abbr.DateTime"
                        ]
                        for time_sel in time_selectors:
                            try:
                                time_element = result.find_element(By.CSS_SELECTOR, time_sel)
                                post_time = time_element.get_attribute('datetime') or \
                                           time_element.get_attribute('title') or \
                                           time_element.text.strip()
                                if post_time:
                                    break
                            except:
                                continue
                    except:
                        pass
                    
                    post_data = {
                        'post_id': post_id,
                        'post_url': post_url,
                        'post_title': post_title,
                        'comment_content': snippet_content,
                        'comment_time': post_time,
                        'comment_link': post_url,
                        'author': author,
                        'page_number': page_num,
                        'source': 'search_snippet'
                    }
                    
                    posts_data.append(post_data)
                    self.logger.info(f"✅ [{page_num}.{i}] Extracted: {post_title[:50]}...")
                    
                except Exception as e:
                    self.logger.debug(f"⚠️ Lỗi khi extract post {i}: {e}")
                    continue
            
            self.logger.info(f"📊 Page {page_num}: Extracted {len(posts_data)} posts")
            return posts_data
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi khi extract posts từ page {page_num}: {e}")
            return []
    
    def crawl_all_pages(self):
        """Crawl tất cả pages trong search results"""
        try:
            all_posts = []
            
            # Detect total pages
            total_pages = self.detect_pagination()
            
            if config.MAX_POSTS_TO_CRAWL > 0:
                max_pages = min(total_pages, (config.MAX_POSTS_TO_CRAWL // 20) + 1)  # ~20 posts per page
                total_pages = max_pages
                self.logger.info(f"🔢 Giới hạn crawl: {total_pages} trang đầu tiên")
            
            # Crawl từng page
            for page in range(1, total_pages + 1):
                self.logger.info(f"📖 [{page}/{total_pages}] Đang crawl page {page}...")
                
                # Navigate tới page cụ thể nếu không phải page 1
                if page > 1:
                    page_url = f"{self.search_base_url}&page={page}"
                    self.driver.get(page_url)
                    time.sleep(config.DELAY_BETWEEN_REQUESTS)
                
                # Extract posts từ page này
                page_posts = self.extract_posts_from_search_page(page)
                all_posts.extend(page_posts)
                
                # Check limit
                if config.MAX_POSTS_TO_CRAWL > 0 and len(all_posts) >= config.MAX_POSTS_TO_CRAWL:
                    all_posts = all_posts[:config.MAX_POSTS_TO_CRAWL]
                    self.logger.info(f"🔢 Đã đạt giới hạn {config.MAX_POSTS_TO_CRAWL} posts")
                    break
                
                time.sleep(config.DELAY_BETWEEN_REQUESTS)
            
            self.comments_data = all_posts
            self.logger.info(f"🎉 Hoàn thành crawl! Tổng cộng: {len(all_posts)} posts")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi khi crawl all pages: {e}")
            return False
    
    def get_full_content_option(self, post_data):
        """Option để lấy full content từ post URL (chỉ của user target)"""
        try:
            self.logger.info(f"📝 Đang lấy full content từ: {post_data['post_url']}")
            
            self.driver.get(post_data['post_url'])
            time.sleep(2)
            
            # ⚠️ FIX: Chỉ lấy content từ comments của user target
            # Tìm tất cả comments của user target trong post này
            target_comments = []
            comment_selectors = [
                f"li.message[data-author='{self.username}']",
                f"[data-author='{self.username}']",
                f".message[data-author='{self.username}']"
            ]
            
            for selector in comment_selectors:
                try:
                    comments = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if comments:
                        target_comments = comments
                        self.logger.info(f"✅ Tìm thấy {len(comments)} comments của {self.username} với selector: {selector}")
                        break
                except:
                    continue
            
            if not target_comments:
                self.logger.warning(f"⚠️ Không tìm thấy comment nào của {self.username} trong post này")
                return post_data
            
            # Lấy content từ comment đầu tiên của user (hoặc tất cả nếu có nhiều)
            full_content_parts = []
            
            for i, comment in enumerate(target_comments):
                try:
                    # Verify lại author để chắc chắn
                    comment_author = comment.get_attribute('data-author')
                    if comment_author and comment_author.lower() != self.username.lower():
                        self.logger.warning(f"⚠️ Skip comment với author khác: {comment_author}")
                        continue
                    
                    # Extract content từ comment này
                    content_selectors = [
                        ".messageText.ugc.baseHtml",
                        ".messageText", 
                        ".message-body .bbWrapper",
                        ".post-content"
                    ]
                    
                    comment_content = ""
                    for content_sel in content_selectors:
                        try:
                            content_element = comment.find_element(By.CSS_SELECTOR, content_sel)
                            comment_content = content_element.text.strip()
                            if comment_content:
                                break
                        except:
                            continue
                    
                    if comment_content:
                        full_content_parts.append(comment_content)
                        self.logger.info(f"✅ Lấy được content từ comment #{i+1} của {self.username}")
                
                except Exception as e:
                    self.logger.debug(f"⚠️ Lỗi khi extract content từ comment #{i+1}: {e}")
                    continue
            
            # Combine all content parts
            if full_content_parts:
                # Nếu có nhiều comments, kết hợp lại
                full_content = "\n--- Gộp bài viết ---\n".join(full_content_parts)
                
                # Chỉ update nếu full content dài hơn snippet content
                current_content = post_data.get('comment_content', '')
                if len(full_content) > len(current_content):
                    post_data['comment_content'] = full_content
                    post_data['source'] = 'full_content'
                    self.logger.info(f"✅ Đã update với full content ({len(full_content)} chars)")
                else:
                    self.logger.info(f"⚡ Snippet content đã đủ chi tiết")
            else:
                self.logger.warning(f"⚠️ Không extract được content từ comment nào")
            
            return post_data
            
        except Exception as e:
            self.logger.warning(f"⚠️ Không thể lấy full content: {e}")
            return post_data
    
    def save_to_csv(self):
        """Lưu dữ liệu vào file CSV"""
        try:
            if not self.comments_data:
                self.logger.warning("⚠️ Không có dữ liệu để lưu")
                return False
            
            output_file = config.OUTPUT_FILE.replace('.csv', '_enhanced.csv')
            self.logger.info(f"💾 Đang lưu {len(self.comments_data)} posts vào {output_file}")
            
            # FIX: Thêm UTF-8 BOM để Excel tự động detect encoding
            with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['post_id', 'post_url', 'post_title', 'comment_content', 'comment_time', 
                             'comment_link', 'author', 'page_number', 'source']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for post in self.comments_data:
                    writer.writerow(post)
            
            self.logger.info(f"✅ Đã lưu thành công dữ liệu vào {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi khi lưu file CSV: {e}")
            return False
    
    def cleanup(self):
        """Dọn dẹp resources"""
        if self.driver:
            self.driver.quit()
            self.logger.info("🔚 Đã đóng browser")
    
    def run(self, get_full_content=False):
        """Chạy enhanced crawler chính"""
        try:
            self.logger.info("🚀 === Bắt đầu Enhanced F319 Crawler ===")
            self.logger.info("🎯 Sử dụng Search-based approach")
            
            # Setup driver
            if not self.setup_driver():
                return False
            
            # Extract user info
            if not self.extract_user_info():
                return False
            
            # Construct search URL
            if not self.construct_search_url():
                return False
            
            # Navigate tới search page
            if not self.navigate_to_search():
                return False
            
            # Crawl all pages
            if not self.crawl_all_pages():
                return False
            
            # Option: Lấy full content
            if get_full_content and self.comments_data:
                self.logger.info("📝 === Bắt đầu lấy full content ===")
                
                # Xác định số posts cần lấy full content
                total_posts = len(self.comments_data)
                
                if config.MAX_FULL_CONTENT_POSTS == -1:
                    # Không lấy full content
                    self.logger.info("⚠️ MAX_FULL_CONTENT_POSTS = -1, bỏ qua lấy full content")
                elif config.MAX_FULL_CONTENT_POSTS == 0:
                    # Lấy tất cả
                    posts_to_process = total_posts
                    self.logger.info(f"📋 Sẽ lấy full content cho TẤT CẢ {posts_to_process} posts")
                else:
                    # Lấy số lượng giới hạn
                    posts_to_process = min(config.MAX_FULL_CONTENT_POSTS, total_posts)
                    self.logger.info(f"📋 Sẽ lấy full content cho {posts_to_process}/{total_posts} posts")
                
                # Lấy full content cho từng post
                if config.MAX_FULL_CONTENT_POSTS != -1:
                    for i in range(posts_to_process):
                        post_data = self.comments_data[i]
                        
                        # Kiểm tra có nên skip post quá dài không
                        if config.SKIP_LONG_POSTS:
                            current_content = post_data.get('comment_content', '')
                            if len(current_content) > config.LONG_POST_THRESHOLD:
                                self.logger.info(f"⏭️ [{i+1}/{posts_to_process}] Skip post dài: {post_data.get('post_title', '')[:50]}...")
                                continue
                        
                        self.logger.info(f"📝 [{i+1}/{posts_to_process}] Lấy full content: {post_data.get('post_title', '')[:50]}...")
                        
                        # Lấy full content
                        self.comments_data[i] = self.get_full_content_option(post_data)
                        
                        # Delay giữa các requests
                        if i < posts_to_process - 1:  # Không delay ở post cuối cùng
                            time.sleep(config.FULL_CONTENT_DELAY)
                
                self.logger.info("✅ === Hoàn thành lấy full content ===")
            
            # Lưu dữ liệu
            self.save_to_csv()
            
            self.logger.info(f"🎉 === Hoàn thành! Đã crawl {len(self.comments_data)} posts ===")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi trong quá trình crawl: {e}")
            return False
        
        finally:
            self.cleanup()

def main():
    """Function chính"""
    print("🚀 === Enhanced F319 Comment Crawler ===")
    print("🎯 Search-based approach - Nhanh & Hiệu quả")
    print(f"📋 Target URL: {config.TARGET_URL}")
    print(f"📁 Output file: {config.OUTPUT_FILE.replace('.csv', '_enhanced.csv')}")
    print(f"🔢 Max posts: {config.MAX_POSTS_TO_CRAWL if config.MAX_POSTS_TO_CRAWL > 0 else 'Không giới hạn'}")
    print("=" * 60)
    
    # Option để lấy full content
    full_content_choice = input("🤔 Lấy full content từ từng post? (y/n, default=n): ").strip().lower()
    get_full_content = full_content_choice in ['y', 'yes']
    
    if get_full_content:
        print("📝 Sẽ lấy full content (chậm hơn nhưng chi tiết hơn)")
    else:
        print("⚡ Chỉ lấy snippet content (nhanh hơn)")
    
    print("=" * 60)
    
    crawler = EnhancedF319Crawler()
    success = crawler.run(get_full_content=get_full_content)
    
    if success:
        output_file = config.OUTPUT_FILE.replace('.csv', '_enhanced.csv')
        print(f"\n✅ Enhanced Crawler hoàn thành thành công!")
        print(f"📁 Dữ liệu đã được lưu trong file: {output_file}")
        print(f"📊 Logs: enhanced_crawler.log")
    else:
        print(f"\n❌ Crawler gặp lỗi. Kiểm tra file log để biết thêm chi tiết.")

if __name__ == "__main__":
    main() 