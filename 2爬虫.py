import os
import json
import requests
from bs4 import BeautifulSoup
import time
import re

def sanitize_filename(filename):
    """
    清理文件名，移除非法字符
    """ 
    # 移除Windows文件名中不允许的字符
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    # 替换可能引起问题的空格和点
    filename = filename.replace(' ', '_').replace('.', '_')
    # 限制文件名长度
    if len(filename) > 100:
        filename = filename[:100]
    return filename

def create_folder_structure(data, base_path="ygo_packages"):
    """
    根据JSON数据创建文件夹结构
    """
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    
    for level1_item in data:
        # 创建1级文件夹
        level1_name = sanitize_filename(level1_item['title'])
        level1_path = os.path.join(base_path, level1_name)
        
        if not os.path.exists(level1_path):
            os.makedirs(level1_path)
            print(f"创建文件夹: {level1_path}")
        
        # 创建2级文件夹
        for level2_item in level1_item['children']:
            level2_name = sanitize_filename(level2_item['title'])
            level2_path = os.path.join(level1_path, level2_name)
            
            if not os.path.exists(level2_path):
                os.makedirs(level2_path)
                print(f"创建文件夹: {level2_path}")

def download_package_html(data, base_path="ygo_packages", delay=1):
    """
    下载每个卡包的HTML内容
    """
    base_url = "https://ocg-card.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    total_packages = sum(
        len(level2['children']) 
        for level1 in data 
        for level2 in level1['children']
    )
    downloaded_count = 0
    
    for level1_item in data:
        level1_name = sanitize_filename(level1_item['title'])
        level1_path = os.path.join(base_path, level1_name)
        
        for level2_item in level1_item['children']:
            level2_name = sanitize_filename(level2_item['title'])
            level2_path = os.path.join(level1_path, level2_name)
            
            for level3_item in level2_item['children']:
                level3_name = sanitize_filename(level3_item['title'])
                href = level3_item['href']
                
                # 构建完整URL
                if href.startswith('/'):
                    full_url = base_url + href
                else:
                    full_url = base_url + '/' + href
                
                # 生成文件名
                filename = f"{level3_name}.html"
                filepath = os.path.join(level2_path, filename)
                
                # 如果文件已存在，跳过下载
                if os.path.exists(filepath):
                    print(f"文件已存在，跳过: {filename}")
                    downloaded_count += 1
                    continue
                
                try:
                    print(f"正在下载: {level3_name}")
                    print(f"URL: {full_url}")
                    
                    response = requests.get(full_url, headers=headers, timeout=10)
                    response.encoding = 'utf-8'
                    
                    if response.status_code == 200:
                        # 使用BeautifulSoup美化HTML
                        soup = BeautifulSoup(response.text, 'html.parser')
                        pretty_html = soup.prettify()
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(pretty_html)
                        
                        downloaded_count += 1
                        print(f"✓ 成功下载: {filename} ({downloaded_count}/{total_packages})")
                    else:
                        print(f"✗ 下载失败，状态码: {response.status_code} - {filename}")
                    
                    # 延迟，避免请求过快
                    time.sleep(delay)
                    
                except requests.exceptions.RequestException as e:
                    print(f"✗ 请求错误: {e} - {filename}")
                except Exception as e:
                    print(f"✗ 未知错误: {e} - {filename}")
    
    return downloaded_count

def create_index_files(data, base_path="ygo_packages"):
    """
    创建索引文件，方便导航
    """
    # 创建主索引文件
    index_content = """<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>游戏王卡包索引</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        h2 { color: #666; margin-left: 20px; }
        h3 { color: #999; margin-left: 40px; }
        a { text-decoration: none; color: #0066cc; }
        a:hover { text-decoration: underline; }
        .category { margin-bottom: 20px; }
        .package { margin-left: 60px; }
    </style>
</head>
<body>
    <h1>游戏王OCG卡包索引</h1>
"""
    
    for level1_item in data:
        level1_name = sanitize_filename(level1_item['title'])
        index_content += f'    <div class="category">\n'
        index_content += f'        <h2>{level1_item["title"]}</h2>\n'
        
        for level2_item in level1_item['children']:
            level2_name = sanitize_filename(level2_item['title'])
            index_content += f'        <h3>{level2_item["title"]}</h3>\n'
            index_content += f'        <div class="package">\n'
            
            for level3_item in level2_item['children']:
                level3_name = sanitize_filename(level3_item['title'])
                filename = f"{level3_name}.html"
                relative_path = f"{level1_name}/{level2_name}/{filename}"
                index_content += f'            <a href="{relative_path}">{level3_item["title"]}</a><br>\n'
            
            index_content += f'        </div>\n'
        
        index_content += f'    </div>\n'
    
    index_content += """</body>
</html>"""
    
    index_path = os.path.join(base_path, "index.html")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"索引文件已创建: {index_path}")

def main():
    # 读取JSON文件
    json_file = "ygo_structure.json"
    
    if not os.path.exists(json_file):
        print(f"错误: 找不到 {json_file} 文件")
        print("请先运行之前的脚本来生成JSON文件")
        return
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取JSON文件失败: {e}")
        return
    
    print("开始创建文件夹结构...")
    create_folder_structure(data)
    
    print("\n开始下载卡包HTML内容...")
    downloaded = download_package_html(data, delay=0.5)  # 0.5秒延迟
    
    # 统计信息
    total_packages = sum(
        len(level2['children']) 
        for level1 in data 
        for level2 in level1['children']
    )
    
    print(f"\n下载完成!")
    print(f"总共卡包数量: {total_packages}")
    print(f"成功下载: {downloaded}")
    
    # 创建索引文件
    print("\n创建索引文件...")
    create_index_files(data)
    
    print(f"\n所有操作完成!")
    print(f"文件保存在: ygo_packages/ 目录")
    print(f"打开 ygo_packages/index.html 可以查看所有卡包的索引")

if __name__ == "__main__":
    main()