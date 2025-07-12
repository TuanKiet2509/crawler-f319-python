# -*- coding: utf-8 -*-
"""
F319 Crawler Web Interface
Web app đơn giản để chạy crawler và download kết quả
Enhanced với multi-user support
"""

import os
import sys
import uuid
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import config
from enhanced_f319_crawler import EnhancedF319Crawler

app = Flask(__name__)
app.secret_key = 'f319_crawler_secret_key_2024'

# Global variables để tracking crawl jobs
crawl_jobs = {}
DOWNLOADS_FOLDER = 'downloads'

# Tạo downloads folder nếu chưa có
if not os.path.exists(DOWNLOADS_FOLDER):
    os.makedirs(DOWNLOADS_FOLDER)

def cleanup_old_files():
    """Dọn dẹp files cũ hơn 1 giờ"""
    try:
        now = datetime.now()
        for filename in os.listdir(DOWNLOADS_FOLDER):
            file_path = os.path.join(DOWNLOADS_FOLDER, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if now - file_time > timedelta(hours=1):
                    os.remove(file_path)
                    print(f"🗑️ Đã xóa file cũ: {filename}")
    except Exception as e:
        print(f"⚠️ Lỗi khi cleanup files: {e}")

def parse_multiple_users(user_input):
    """Parse input để lấy danh sách multiple users (comma-separated only)"""
    try:
        # Split by commas only (no more newlines since we use input field)
        users = []
        parts = user_input.strip().split(',')
        
        for part in parts:
            user = part.strip()
            if user and '.' in user:
                users.append(user)
        
        # Remove duplicates
        users = list(set(users))
        return users
    except Exception as e:
        print(f"⚠️ Lỗi parse users: {e}")
        return []

def run_single_user_crawler(username_with_id, output_filename, get_full_content=False):
    """Chạy crawler cho một user"""
    try:
        # Construct target URL
        target_url = f"https://f319.com/members/{username_with_id}/"
        
        # Backup original config
        original_url = config.TARGET_URL
        original_output = config.OUTPUT_FILE
        original_headless = config.HEADLESS_MODE
        
        # Set config cho user này
        config.TARGET_URL = target_url
        config.OUTPUT_FILE = output_filename
        config.HEADLESS_MODE = True  # Luôn chạy headless trên web
        
        # Chạy crawler
        crawler = EnhancedF319Crawler()
        success = crawler.run(get_full_content=get_full_content)
        
        # Restore original config
        config.TARGET_URL = original_url
        config.OUTPUT_FILE = original_output
        config.HEADLESS_MODE = original_headless
        
        return success
        
    except Exception as e:
        print(f"❌ Lỗi crawler cho user {username_with_id}: {e}")
        return False

def run_multi_user_crawler(job_id, users_list, get_full_content=False):
    """Chạy crawler cho multiple users"""
    try:
        # Update job status
        crawl_jobs[job_id]['status'] = 'running'
        crawl_jobs[job_id]['message'] = f'Đang crawl {len(users_list)} users...'
        crawl_jobs[job_id]['total_users'] = len(users_list)
        crawl_jobs[job_id]['completed_users'] = 0
        crawl_jobs[job_id]['failed_users'] = 0
        crawl_jobs[job_id]['user_results'] = []
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        all_output_files = []
        
        # Crawl từng user
        for i, username_with_id in enumerate(users_list, 1):
            try:
                crawl_jobs[job_id]['message'] = f'Crawl user {i}/{len(users_list)}: {username_with_id}'
                
                # Tạo output filename cho user này
                safe_username = username_with_id.replace('.', '_')
                output_filename = f"f319_crawler_{job_id}_{safe_username}_{timestamp}.csv"
                output_path = os.path.join(DOWNLOADS_FOLDER, output_filename)
                
                # Chạy crawler cho user này
                success = run_single_user_crawler(username_with_id, output_path, get_full_content)
                
                if success:
                    # Tìm file thực tế được tạo (enhanced crawler có thể thêm _enhanced suffix)
                    pattern_prefix = f"f319_crawler_{job_id}_{safe_username}_{timestamp}"
                    actual_files = []
                    
                    for filename in os.listdir(DOWNLOADS_FOLDER):
                        if filename.startswith(pattern_prefix) and filename.endswith('.csv'):
                            actual_files.append(filename)
                    
                    if actual_files:
                        actual_filename = max(actual_files, key=lambda f: os.path.getctime(os.path.join(DOWNLOADS_FOLDER, f)))
                        actual_path = os.path.join(DOWNLOADS_FOLDER, actual_filename)
                        
                        # Đếm số posts
                        with open(actual_path, 'r', encoding='utf-8') as f:
                            post_count = len(f.readlines()) - 1  # Trừ header
                        
                        crawl_jobs[job_id]['completed_users'] += 1
                        crawl_jobs[job_id]['user_results'].append({
                            'username': username_with_id,
                            'status': 'success',
                            'filename': actual_filename,
                            'post_count': post_count
                        })
                        all_output_files.append(actual_filename)
                        
                        print(f"✅ User {username_with_id}: {post_count} posts")
                    else:
                        crawl_jobs[job_id]['failed_users'] += 1
                        crawl_jobs[job_id]['user_results'].append({
                            'username': username_with_id,
                            'status': 'error',
                            'message': 'Không tìm thấy file output'
                        })
                else:
                    crawl_jobs[job_id]['failed_users'] += 1
                    crawl_jobs[job_id]['user_results'].append({
                        'username': username_with_id,
                        'status': 'error',
                        'message': 'Crawler thất bại'
                    })
                
                # Delay giữa các users
                time.sleep(2)
                
            except Exception as e:
                crawl_jobs[job_id]['failed_users'] += 1
                crawl_jobs[job_id]['user_results'].append({
                    'username': username_with_id,
                    'status': 'error',
                    'message': str(e)
                })
                print(f"❌ Lỗi crawl user {username_with_id}: {e}")
        
        # Tạo combined file nếu có nhiều hơn 1 file thành công
        if len(all_output_files) > 1:
            combined_filename = f"f319_crawler_{job_id}_combined_{timestamp}.csv"
            combined_path = os.path.join(DOWNLOADS_FOLDER, combined_filename)
            
            try:
                import csv
                with open(combined_path, 'w', newline='', encoding='utf-8-sig') as combined_file:
                    writer = None
                    total_posts = 0
                    
                    for filename in all_output_files:
                        file_path = os.path.join(DOWNLOADS_FOLDER, filename)
                        if os.path.exists(file_path):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                reader = csv.DictReader(f)
                                
                                if writer is None:
                                    writer = csv.DictWriter(combined_file, fieldnames=reader.fieldnames)
                                    writer.writeheader()
                                
                                for row in reader:
                                    writer.writerow(row)
                                    total_posts += 1
                
                crawl_jobs[job_id]['combined_file'] = combined_filename
                crawl_jobs[job_id]['total_posts'] = total_posts
                print(f"✅ Đã tạo combined file: {combined_filename} với {total_posts} posts")
                
            except Exception as e:
                print(f"⚠️ Lỗi khi tạo combined file: {e}")
        
        # Update final status
        if crawl_jobs[job_id]['completed_users'] > 0:
            crawl_jobs[job_id]['status'] = 'completed'
            crawl_jobs[job_id]['message'] = f'Hoàn thành! {crawl_jobs[job_id]["completed_users"]}/{len(users_list)} users thành công'
            crawl_jobs[job_id]['output_files'] = all_output_files
        else:
            crawl_jobs[job_id]['status'] = 'error'
            crawl_jobs[job_id]['message'] = 'Tất cả users đều thất bại'
            
    except Exception as e:
        crawl_jobs[job_id]['status'] = 'error'
        crawl_jobs[job_id]['message'] = f'Lỗi: {str(e)}'
        print(f"❌ Lỗi trong multi-user crawler job {job_id}: {e}")

def run_crawler(job_id, username_with_id, get_full_content=False):
    """Chạy crawler trong background thread (backward compatibility)"""
    try:
        # Parse input để kiểm tra single hay multi user
        users_list = parse_multiple_users(username_with_id)
        
        if len(users_list) == 1:
            # Single user - dùng logic cũ
            crawl_jobs[job_id]['status'] = 'running'
            crawl_jobs[job_id]['message'] = 'Đang khởi tạo crawler...'
            
            # Construct target URL
            target_url = f"https://f319.com/members/{users_list[0]}/"
            
            # Backup original config
            original_url = config.TARGET_URL
            original_output = config.OUTPUT_FILE
            original_headless = config.HEADLESS_MODE
            
            # Set config cho job này
            config.TARGET_URL = target_url
            config.HEADLESS_MODE = True  # Luôn chạy headless trên web
            
            # Tạo unique output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"f319_crawler_{job_id}_{timestamp}.csv"
            output_path = os.path.join(DOWNLOADS_FOLDER, output_filename)
            config.OUTPUT_FILE = output_path
            
            crawl_jobs[job_id]['message'] = 'Đang crawl dữ liệu...'
            
            # Chạy crawler
            crawler = EnhancedF319Crawler()
            success = crawler.run(get_full_content=get_full_content)
            
            # FIX: Tìm file thực tế được tạo (enhanced crawler có thể thêm _enhanced suffix)
            if success:
                # Tìm tất cả files có pattern của job này
                pattern_prefix = f"f319_crawler_{job_id}_{timestamp}"
                actual_files = []
                
                for filename in os.listdir(DOWNLOADS_FOLDER):
                    if filename.startswith(pattern_prefix) and filename.endswith('.csv'):
                        actual_files.append(filename)
                
                if actual_files:
                    # Lấy file mới nhất (nếu có nhiều files)
                    actual_filename = max(actual_files, key=lambda f: os.path.getctime(os.path.join(DOWNLOADS_FOLDER, f)))
                    actual_path = os.path.join(DOWNLOADS_FOLDER, actual_filename)
                    
                    # Đếm số posts
                    with open(actual_path, 'r', encoding='utf-8') as f:
                        post_count = len(f.readlines()) - 1  # Trừ header
                    
                    crawl_jobs[job_id]['status'] = 'completed'
                    crawl_jobs[job_id]['message'] = f'Hoàn thành! Crawl được {post_count} posts'
                    crawl_jobs[job_id]['output_file'] = actual_filename  # Dùng tên file thực tế
                    crawl_jobs[job_id]['post_count'] = post_count
                else:
                    crawl_jobs[job_id]['status'] = 'error'
                    crawl_jobs[job_id]['message'] = 'Crawler hoàn thành nhưng không tìm thấy file output'
            else:
                crawl_jobs[job_id]['status'] = 'error'
                crawl_jobs[job_id]['message'] = 'Crawler gặp lỗi hoặc không tìm thấy dữ liệu'
            
            # Restore original config
            config.TARGET_URL = original_url
            config.OUTPUT_FILE = original_output
            config.HEADLESS_MODE = original_headless
            
        else:
            # Multiple users - dùng logic mới
            run_multi_user_crawler(job_id, users_list, get_full_content)
        
    except Exception as e:
        crawl_jobs[job_id]['status'] = 'error'
        crawl_jobs[job_id]['message'] = f'Lỗi: {str(e)}'
        print(f"❌ Lỗi trong crawler job {job_id}: {e}")

@app.route('/')
def index():
    """Trang chính"""
    cleanup_old_files()
    return render_template('index.html')

@app.route('/crawl', methods=['POST'])
def start_crawl():
    """Bắt đầu crawl job"""
    try:
        # Lấy input từ form
        username_with_id = request.form.get('username_id', '').strip()
        get_full_content = request.form.get('full_content') == 'on'
        max_full_content = request.form.get('max_full_content', '0').strip()
        
        # Validate input
        if not username_with_id:
            flash('Vui lòng nhập username.userid', 'error')
            return redirect(url_for('index'))
        
        # Validate max_full_content
        try:
            max_full_content_int = int(max_full_content) if max_full_content else 0
            if max_full_content_int < -1:
                max_full_content_int = 0
        except ValueError:
            max_full_content_int = 0
        
        # Cập nhật config với tùy chọn từ user
        if get_full_content:
            config.MAX_FULL_CONTENT_POSTS = max_full_content_int
            if max_full_content_int == 0:
                flash('Sẽ lấy full content cho TẤT CẢ posts (có thể mất nhiều thời gian)', 'warning')
            elif max_full_content_int == -1:
                flash('Sẽ chỉ lấy snippet content (nhanh)', 'info')
                get_full_content = False
            else:
                flash(f'Sẽ lấy full content cho {max_full_content_int} posts đầu tiên', 'info')
        
        # Parse multiple users
        users_list = parse_multiple_users(username_with_id)
        
        if not users_list:
            flash('Không tìm thấy user nào hợp lệ. Format phải là username.userid', 'error')
            return redirect(url_for('index'))
        
        # Validate format cho từng user
        for user in users_list:
            if '.' not in user:
                flash(f'Format không hợp lệ: {user}. Phải là username.userid', 'error')
                return redirect(url_for('index'))
        
        # Tạo job ID
        job_id = str(uuid.uuid4())[:8]
        
        # Initialize job tracking
        crawl_jobs[job_id] = {
            'status': 'starting',
            'message': 'Đang chuẩn bị...',
            'username_id': username_with_id,
            'users_list': users_list,
            'full_content': get_full_content,
            'max_full_content': max_full_content_int,
            'start_time': datetime.now(),
            'output_file': None,
            'post_count': 0
        }
        
        # Start crawler trong background thread
        thread = threading.Thread(target=run_crawler, args=(job_id, username_with_id, get_full_content))
        thread.daemon = True
        thread.start()
        
        if len(users_list) == 1:
            flash(f'Đã bắt đầu crawl cho {users_list[0]}', 'success')
        else:
            flash(f'Đã bắt đầu crawl cho {len(users_list)} users', 'success')
        
        return redirect(url_for('result', job_id=job_id))
        
    except Exception as e:
        flash(f'Lỗi khi bắt đầu crawl: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/result/<job_id>')
def result(job_id):
    """Trang kết quả"""
    if job_id not in crawl_jobs:
        flash('Job không tồn tại', 'error')
        return redirect(url_for('index'))
    
    job_data = crawl_jobs[job_id]
    return render_template('result.html', job_id=job_id, job_data=job_data)

@app.route('/status/<job_id>')
def job_status(job_id):
    """API endpoint để check status của job"""
    if job_id not in crawl_jobs:
        return jsonify({'status': 'not_found', 'message': 'Job không tồn tại'})
    
    job_data = crawl_jobs[job_id].copy()
    
    # Calculate elapsed time
    if 'start_time' in job_data:
        elapsed = datetime.now() - job_data['start_time']
        job_data['elapsed_time'] = str(elapsed).split('.')[0]  # Remove microseconds
    
    return jsonify(job_data)

@app.route('/download/<job_id>')
def download_file(job_id):
    """Download file kết quả"""
    try:
        if job_id not in crawl_jobs:
            flash('Job không tồn tại', 'error')
            return redirect(url_for('index'))
        
        job_data = crawl_jobs[job_id]
        
        if job_data['status'] != 'completed':
            flash('File chưa sẵn sàng để download', 'error')
            return redirect(url_for('result', job_id=job_id))
        
        # Ưu tiên combined file nếu có
        if job_data.get('combined_file'):
            file_path = os.path.join(DOWNLOADS_FOLDER, job_data['combined_file'])
            download_name = job_data['combined_file']
        elif job_data.get('output_file'):
            file_path = os.path.join(DOWNLOADS_FOLDER, job_data['output_file'])
            download_name = job_data['output_file']
        else:
            flash('Không tìm thấy file để download', 'error')
            return redirect(url_for('result', job_id=job_id))
        
        if not os.path.exists(file_path):
            flash('File không tồn tại', 'error')
            return redirect(url_for('result', job_id=job_id))
        
        return send_file(file_path, as_attachment=True, download_name=download_name)
        
    except Exception as e:
        flash(f'Lỗi khi download: {str(e)}', 'error')
        return redirect(url_for('result', job_id=job_id))

@app.route('/download_individual/<job_id>/<filename>')
def download_individual_file(job_id, filename):
    """Download individual file từ multi-user crawl"""
    try:
        if job_id not in crawl_jobs:
            flash('Job không tồn tại', 'error')
            return redirect(url_for('index'))
        
        file_path = os.path.join(DOWNLOADS_FOLDER, filename)
        
        if not os.path.exists(file_path):
            flash('File không tồn tại', 'error')
            return redirect(url_for('result', job_id=job_id))
        
        return send_file(file_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        flash(f'Lỗi khi download: {str(e)}', 'error')
        return redirect(url_for('result', job_id=job_id))

@app.route('/jobs')
def list_jobs():
    """Danh sách tất cả jobs (admin)"""
    return jsonify(crawl_jobs)

if __name__ == '__main__':
    print("🚀 === F319 CRAWLER WEB INTERFACE (Enhanced Multi-User) ===")
    print("🌐 Truy cập: http://localhost:5000")
    print("📋 Nhập username.userid để bắt đầu crawl")
    print("🔢 Hỗ trợ multiple users (cách nhau bằng dòng mới hoặc dấu phẩy)")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000) 