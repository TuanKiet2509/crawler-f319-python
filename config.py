# -*- coding: utf-8 -*-
"""
Configuration file cho F319 Crawler
Bạn có thể thay đổi các settings này theo nhu cầu
"""

# URL target
TARGET_URL = "https://f319.com/members/lamnguyenphu.493993/"

# Browser settings
HEADLESS_MODE = True  # True = chạy ẩn browser, False = hiện browser
BROWSER_TIMEOUT = 30  # Thời gian chờ tối đa (giây)

# Crawler settings
DELAY_BETWEEN_REQUESTS = 2  # Delay giữa các request (giây)
MAX_POSTS_TO_CRAWL = 50  # Số bài đăng tối đa để crawl (0 = không giới hạn)
RETRY_ATTEMPTS = 3  # Số lần retry khi có lỗi

# Full content settings
MAX_FULL_CONTENT_POSTS = 0  # Số posts lấy full content (0 = tất cả, -1 = không lấy)
FULL_CONTENT_DELAY = 3  # Delay giữa các full content requests (giây)
SKIP_LONG_POSTS = True  # Bỏ qua posts quá dài (>5000 chars snippet)
LONG_POST_THRESHOLD = 5000  # Ngưỡng độ dài post (chars)

# Output settings
OUTPUT_FILE = "comments_data.csv"  # Tên file output
ENABLE_LOGGING = True  # Bật/tắt logging

# Selectors cập nhật theo cấu trúc thực tế của f319.com
POSTS_TAB_SELECTOR = "a[href*='#postings']"  # Selector cho tab "Các bài đăng"
POST_LINKS_SELECTOR = ".title a[href*='posts/']"  # Selector cho links bài đăng
COMMENT_SELECTOR = ".messageText"  # Selector cho nội dung comment 