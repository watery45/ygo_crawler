import os
import csv
from bs4 import BeautifulSoup
import re

def parse_yugioh_pack_html(file_path, filename):
    """
    解析游戏王卡包HTML文件，提取卡包名、发售日期、卡片数量和卡包缩写
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 提取卡包名（使用文件名作为卡包名）
        pack_name = os.path.splitext(filename)[0]
        
        # 提取发售日期
        date_element = soup.find('time', {'class': ['entry-date', 'date', 'published', 'updated']})
        if date_element:
            date_published = date_element.get_text(strip=True)
        else:
            date_meta = soup.find('meta', {'property': 'article:published_time'})
            if date_meta:
                date_published = date_meta.get('content', '').split('T')[0]
            else:
                date_published = "未知"
        
        # 提取卡片数量
        total_div = soup.find('div', class_='total')
        if total_div:
            total_text = total_div.get_text(strip=True)
            if '全' in total_text and '枚' in total_text:
                card_count = ''.join(filter(str.isdigit, total_text))
            else:
                card_count = "未知"
        else:
            card_count = "未知"
        
        # 提取卡包缩写
        pack_abbreviation = "未知"
        
        # 方法1: 从canonical链接中提取
        canonical_link = soup.find('link', {'rel': 'canonical'})
        if canonical_link and 'href' in canonical_link.attrs:
            href = canonical_link['href']
            # 从URL中提取缩写，例如从 https://ocg-card.com/list/agov/ 提取 agov
            match = re.search(r'/list/([^/]+)/?$', href)
            if match:
                pack_abbreviation = match.group(1)
        
        # 方法2: 如果没有找到，从文件名中提取（假设文件名就是缩写）
        if pack_abbreviation == "未知":
            pack_abbreviation = os.path.splitext(filename)[0].lower()
        
        return {
            'pack_name': pack_name,
            'pack_abbreviation': pack_abbreviation,
            'release_date': date_published,
            'card_count': card_count,
            'file_path': file_path
        }
    
    except Exception as e:
        print(f"解析文件 {file_path} 时出错: {e}")
        return None

def main():
    html_directory = 'ygo_packages'  # 修改为你的目录路径
    output_csv = 'yugioh_pack_info.csv'
    
    # 存储所有卡包信息
    pack_info_list = []
    
    # 遍历目录
    for root, dirs, files in os.walk(html_directory):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                print(f"正在处理: {file_path}")
                
                # 解析HTML文件
                pack_info = parse_yugioh_pack_html(file_path, file)
                if pack_info:
                    pack_info_list.append(pack_info)
    
    # 写入CSV文件
    if pack_info_list:
        with open(output_csv, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = ['pack_name', 'pack_abbreviation', 'release_date', 'card_count', 'file_path']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for pack_info in pack_info_list:
                writer.writerow(pack_info)
        
        print(f"成功解析 {len(pack_info_list)} 个卡包信息，已保存到 {output_csv}")
        
        # 打印前几行作为示例
        print("\n前5行数据示例:")
        for i, pack in enumerate(pack_info_list[:5]):
            print(f"{i+1}. {pack}")
    else:
        print("未找到任何卡包信息")

if __name__ == "__main__":
    main()