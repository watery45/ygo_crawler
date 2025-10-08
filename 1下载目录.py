import requests
from bs4 import BeautifulSoup
import json
import time

def fetch_ygo_webpage():
    """
    从网页获取游戏王卡包列表
    """
    url = "https://ocg-card.com/list/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print("正在从网站获取数据...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        print("数据获取成功！")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"获取网页失败: {e}")
        return None

def parse_ygo_html(html_content):
    """
    解析游戏王HTML内容，分级整理标题结构
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    result = []
    
    # 查找所有主要分类（1级标题）
    main_categories = soup.find_all('div', class_='list-category')
    
    for category in main_categories:
        category_name = category.get_text(strip=True)
        category_id = category.get('id', '')
        
        # 构建1级标题结构
        level1 = {
            'level': 1,
            'title': category_name,
            'id': category_id,
            'children': []
        }
        
        # 查找对应的list-main内容
        list_main = category.find_next_sibling('div', class_='list-main')
        if not list_main:
            continue
            
        # 查找所有dl元素（2级标题）
        dl_elements = list_main.find_all('dl')
        
        for dl in dl_elements:
            # 提取2级标题
            dt = dl.find('dt', class_='list-series-title')
            if dt:
                level2_title = dt.get_text(strip=True)
                level2_link = dt.find('a')
                level2_id = level2_link.get('id', '') if level2_link else ''
                
                # 构建2级标题结构
                level2 = {
                    'level': 2,
                    'title': level2_title,
                    'id': level2_id,
                    'children': []
                }
                
                # 查找3级标题（li中的a标签）
                # 先查找直接包含在dd中的ul
                dd = dl.find('dd')
                if dd:
                    # 查找所有ul（包括嵌套的）
                    uls = dd.find_all('ul')
                    for ul in uls:
                        lis = ul.find_all('li')
                        for li in lis:
                            a_tag = li.find('a')
                            if a_tag:
                                level3_title = a_tag.get_text(strip=True)
                                level3_href = a_tag.get('href', '')
                                
                                # 检查是否有new图标
                                new_icon = li.find('span', class_='new-icon')
                                is_new = new_icon is not None
                                
                                # 构建3级标题结构
                                level3 = {
                                    'level': 3,
                                    'title': level3_title,
                                    'href': level3_href,
                                    'is_new': is_new
                                }
                                level2['children'].append(level3)
                
                level1['children'].append(level2)
        
        result.append(level1)
    
    return result

def print_hierarchical_structure(data, indent=0):
    """
    以层级格式打印结构
    """
    for item in data:
        prefix = "  " * (item['level'] - 1)
        
        if item['level'] == 1:
            marker = "█"
        elif item['level'] == 2:
            marker = "├──"
        else:  # level 3
            marker = "│   └──"
            if item.get('is_new'):
                marker += " 🆕"
        
        print(f"{prefix}{marker} {item['title']}")
        
        if 'children' in item and item['children']:
            print_hierarchical_structure(item['children'], indent + 1)

def save_to_json(data, filename='ygo_structure.json'):
    """
    将结构保存为JSON文件
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_to_text(data, filename='ygo_structure.txt'):
    """
    将结构保存为文本文件
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("游戏王OCG卡包分级结构\n")
        f.write("=" * 50 + "\n\n")
        
        def write_level(items, file_obj):
            for item in items:
                prefix = "  " * (item['level'] - 1)
                
                if item['level'] == 1:
                    marker = "█"
                elif item['level'] == 2:
                    marker = "├──"
                else:  # level 3
                    marker = "│   └──"
                    if item.get('is_new'):
                        marker += " 🆕"
                
                file_obj.write(f"{prefix}{marker} {item['title']}\n")
                
                if 'children' in item and item['children']:
                    write_level(item['children'], file_obj)
        
        write_level(data, f)

def main():
    # 从网页获取数据
    html_content = fetch_ygo_webpage()
    
    if not html_content:
        print("无法获取网页数据，请检查网络连接或网站状态")
        return
    
    # 解析HTML
    print("正在解析数据结构...")
    structured_data = parse_ygo_html(html_content)
    
    print("\n" + "=" * 60)
    print("游戏王OCG卡包分级结构")
    print("=" * 60)
    
    # 打印层级结构
    print_hierarchical_structure(structured_data)
    
    # 保存文件
    save_to_json(structured_data)
    save_to_text(structured_data)
    
    print(f"\n结构已保存到:")
    print(f"- ygo_structure.json (JSON格式)")
    print(f"- ygo_structure.txt (文本格式)")
    
    # 统计信息
    total_level1 = len(structured_data)
    total_level2 = sum(len(cat['children']) for cat in structured_data)
    total_level3 = sum(len(l2['children']) for cat in structured_data for l2 in cat['children'])
    
    print(f"\n统计信息:")
    print(f"1级分类数量: {total_level1}")
    print(f"2级系列数量: {total_level2}")
    print(f"3级卡包数量: {total_level3}")
    
    # 显示主要分类
    print(f"\n主要分类:")
    for i, category in enumerate(structured_data, 1):
        print(f"  {i}. {category['title']}")

if __name__ == "__main__":
    main()