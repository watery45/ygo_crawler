import os
import csv
from bs4 import BeautifulSoup
import re

def parse_card_info(html_content):
    """解析HTML内容，提取卡牌信息"""
    soup = BeautifulSoup(html_content, 'html.parser')
    cards = []
    
    # 查找卡牌列表表格
    card_table = soup.find('table')
    if not card_table:
        return cards
    
    # 查找所有卡牌行
    rows = card_table.find_all('tr')
    i = 0
    
    while i < len(rows):
        row = rows[i]
        
        # 检查是否是卡牌开始行（包含卡牌编号）
        card_number_td = row.find('td', class_='card-number')
        if card_number_td:
            card_info = {}
            
            # 提取卡牌编号
            card_info['卡牌编码'] = card_number_td.get_text(strip=True)
            
            # 提取卡名
            card_name_td = row.find('td', class_=re.compile(r'(e-mon|r-mon|f-mon|s-mon|x-mon|l-mon|magic)'))
            if card_name_td:
                # 移除Ruby注音
                ruby = card_name_td.find('div', class_='card-ruby')
                if ruby:
                    ruby.decompose()
                card_info['卡名'] = card_name_td.get_text(strip=True)
            
            # 提取卡牌类别
            category_td = row.find('td', class_='card-category')
            if category_td:
                card_info['卡牌类别'] = category_td.get_text(strip=True)
            
            # 提取罕贵度
            rare_td = row.find('td', class_='card-rare')
            if rare_td:
                # 提取所有罕贵度类型
                rare_texts = []
                for link in rare_td.find_all('a'):
                    rare_texts.append(link.get_text(strip=True))
                card_info['罕贵度'] = ' / '.join(rare_texts)
            
            # 检查下一行是否有属性等信息
            if i + 1 < len(rows):
                next_row = rows[i + 1]
                
                # 提取属性
                attr_td = next_row.find('td', class_='card-attr')
                if attr_td:
                    card_info['属性'] = attr_td.get_text(strip=True)
                
                # 提取等级/阶数
                star_td = next_row.find('td', class_='card-star')
                if star_td:
                    card_info['等级'] = star_td.get_text(strip=True)
                else:
                    # 检查是否是超量怪兽（没有等级但有阶数）
                    non_stts = next_row.find('td', class_='non-stts')
                    if non_stts and non_stts.get_text(strip=True) == '-':
                        # 对于超量怪兽，等级字段存储阶数
                        card_info['等级'] = '阶数'  # 具体阶数需要在链接信息中获取
                
                # 提取种族
                type_td = next_row.find('td', class_='card-type')
                if type_td:
                    card_info['种族'] = type_td.get_text(strip=True)
                
                # 提取攻击力
                force_tds = next_row.find_all('td', class_='card-force')
                if len(force_tds) >= 1:
                    card_info['攻击力'] = force_tds[0].get_text(strip=True)
                if len(force_tds) >= 2:
                    card_info['防御力'] = force_tds[1].get_text(strip=True)
                
                # 提取卡片密码
                pass_td = next_row.find('td', class_='card-pass')
                if pass_td:
                    card_info['卡片密码'] = pass_td.get_text(strip=True)
            
            # 提取卡牌文本（可能跨越多行）
            card_text = ""
            j = i + 2  # 从卡牌信息后的行开始
            while j < len(rows):
                text_row = rows[j]
                text_td = text_row.find('td', class_='card-text')
                if text_td:
                    card_text += text_td.get_text(strip=True) + " "
                    j += 1
                else:
                    # 检查是否是新的卡牌开始
                    if text_row.find('td', class_='card-number'):
                        break
                    j += 1
            
            if card_text:
                card_info['卡牌文本'] = card_text.strip()
            
            cards.append(card_info)
            
            # 跳过已经处理的行
            i = j
        else:
            i += 1
    
    return cards

def process_html_directory(html_dir, csv_dir):
    """处理HTML目录，生成对应的CSV文件"""
    
    # 确保输出目录存在
    os.makedirs(csv_dir, exist_ok=True)
    
    # 遍历HTML目录
    for root, dirs, files in os.walk(html_dir):
        for file in files:
            if file.endswith('.html'):
                html_path = os.path.join(root, file)
                
                # 计算对应的CSV路径
                relative_path = os.path.relpath(html_path, html_dir)
                csv_path = os.path.join(csv_dir, os.path.splitext(relative_path)[0] + '.csv')
                
                # 确保CSV文件的目录存在
                os.makedirs(os.path.dirname(csv_path), exist_ok=True)
                
                try:
                    # 读取HTML文件
                    with open(html_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    # 解析卡牌信息
                    cards = parse_card_info(html_content)
                    
                    if cards:
                        # 写入CSV文件
                        with open(csv_path, 'w', encoding='utf-8', newline='') as csvfile:
                            fieldnames = ['卡牌编码', '卡名', '卡牌类别', '属性', '等级', '种族', 
                                        '攻击力', '防御力', '罕贵度', '卡片密码', '卡牌文本']
                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                            
                            writer.writeheader()
                            for card in cards:
                                writer.writerow(card)
                        
                        print(f"成功处理: {html_path} -> {csv_path} (找到 {len(cards)} 张卡牌)")
                    else:
                        print(f"警告: 在 {html_path} 中未找到卡牌信息")
                        
                except Exception as e:
                    print(f"处理文件 {html_path}  时出错: {str(e)}")

def main():
    # 配置目录路径
    html_directory = "ygo_packages"  # 替换为实际的HTML目录路径
    csv_directory = "csv_directory"    # CSV输出目录
    
    # 处理所有HTML文件
    process_html_directory(html_directory, csv_directory)
    print("处理完成！")

if __name__ == "__main__":
    main()