import os
import csv
import glob

def merge_csv_files(csv_directory, output_file):
    """
    合并csv_directory下所有CSV文件到一个输出文件，确保Excel兼容
    
    Args:
        csv_directory (str): CSV文件所在的根目录
        output_file (str): 合并后的输出文件路径
    """
    
    # 查找所有CSV文件
    csv_files = glob.glob(os.path.join(csv_directory, "**", "*.csv"), recursive=True)
    
    if not csv_files:
        print(f"在目录 {csv_directory} 中未找到CSV文件")
        return
    
    print(f"找到 {len(csv_files)} 个CSV文件")
    
    # 用于存储所有数据
    all_data = []
    # 存储字段名，确保一致性
    fieldnames = set()
    
    # 读取所有CSV文件
    for csv_file in csv_files:
        try:
            # 尝试多种编码方式读取
            for encoding in ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']:
                try:
                    with open(csv_file, 'r', encoding=encoding) as f:
                        reader = csv.DictReader(f)
                        
                        # 获取字段名
                        current_fields = reader.fieldnames
                        if current_fields:
                            fieldnames.update(current_fields)
                        
                        # 读取数据
                        file_data = list(reader)
                        all_data.extend(file_data)
                        
                        print(f"已读取: {csv_file} ({len(file_data)} 行, 编码: {encoding})")
                        break  # 成功读取则跳出编码尝试循环
                except UnicodeDecodeError:
                    continue  # 尝试下一种编码
            else:
                # 所有编码都失败
                print(f"警告: 无法读取文件 {csv_file}，尝试了所有编码方式")
                
        except Exception as e:
            print(f"读取文件 {csv_file} 时出错: {str(e)}")
    
    if not all_data:
        print("没有找到有效数据")
        return
    
    # 将set转换为list并排序，确保字段顺序一致
    fieldnames = sorted(list(fieldnames))
    
    # 写入合并后的CSV文件，使用Excel兼容的编码
    try:
        # 方法1: 使用utf-8-sig (带BOM的UTF-8，Excel兼容)
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # 写入表头
            writer.writeheader()
            
            # 写入所有数据
            for row in all_data:
                # 确保每一行都有所有字段，缺失字段设为空字符串
                complete_row = {field: row.get(field, '') for field in fieldnames}
                writer.writerow(complete_row)
        
        print(f"合并完成！共 {len(all_data)} 行数据已保存到: {output_file}")
        print(f"字段列表: {', '.join(fieldnames)}")
        print("文件已使用UTF-8 with BOM编码保存，可在Excel中直接打开")
        
    except Exception as e:
        print(f"写入合并文件时出错: {str(e)}")

def merge_csv_files_simple(csv_directory, output_file):
    """
    简化版本的合并函数，直接拼接文件内容，确保Excel兼容
    
    Args:
        csv_directory (str): CSV文件所在的根目录
        output_file (str): 合并后的输出文件路径
    """
    
    csv_files = glob.glob(os.path.join(csv_directory, "**", "*.csv"), recursive=True)
    
    if not csv_files:
        print(f"在目录 {csv_directory} 中未找到CSV文件")
        return
    
    print(f"找到 {len(csv_files)} 个CSV文件")
    
    first_file = True
    
    # 使用utf-8-sig编码确保Excel兼容
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as outfile:
        for i, csv_file in enumerate(csv_files):
            try:
                # 尝试多种编码方式读取
                for encoding in ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']:
                    try:
                        with open(csv_file, 'r', encoding=encoding) as infile:
                            if first_file:
                                # 第一个文件，包含表头
                                outfile.write(infile.read())
                                first_file = False
                            else:
                                # 后续文件，跳过表头
                                lines = infile.readlines()
                                if lines:  # 确保文件不为空
                                    # 跳过第一行（表头），写入其余内容
                                    outfile.writelines(lines[1:])
                        
                        print(f"已合并: {csv_file} (编码: {encoding})")
                        break  # 成功读取则跳出编码尝试循环
                    except UnicodeDecodeError:
                        continue  # 尝试下一种编码
                else:
                    # 所有编码都失败
                    print(f"警告: 无法读取文件 {csv_file}，尝试了所有编码方式")
                    
            except Exception as e:
                print(f"处理文件 {csv_file} 时出错: {str(e)}")
    
    print(f"简化合并完成！输出文件: {output_file}")
    print("文件已使用UTF-8 with BOM编码保存，可在Excel中直接打开")

def merge_csv_with_pandas(csv_directory, output_file):
    """
    使用pandas合并CSV文件，确保Excel兼容
    
    Args:
        csv_directory (str): CSV文件所在的根目录
        output_file (str): 合并后的输出文件路径
    """
    try:
        import pandas as pd
    except ImportError:
        print("pandas库未安装，请使用基础版本或安装pandas: pip install pandas")
        return
    
    csv_files = glob.glob(os.path.join(csv_directory, "**", "*.csv"), recursive=True)
    
    if not csv_files:
        print(f"在目录 {csv_directory} 中未找到CSV文件")
        return
    
    print(f"找到 {len(csv_files)} 个CSV文件")
    
    # 读取所有CSV文件到DataFrame列表
    dataframes = []
    for csv_file in csv_files:
        try:
            # 尝试多种编码方式
            for encoding in ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']:
                try:
                    df = pd.read_csv(csv_file, encoding=encoding)
                    dataframes.append(df)
                    print(f"已读取: {csv_file} ({len(df)} 行, {len(df.columns)} 列, 编码: {encoding})")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                print(f"警告: 无法读取文件 {csv_file}，尝试了所有编码方式")
                
        except Exception as e:
            print(f"读取文件 {csv_file} 时出错: {str(e)}")
    
    if not dataframes:
        print("没有找到有效数据")
        return
    
    # 合并所有DataFrame
    merged_df = pd.concat(dataframes, ignore_index=True, sort=False)
    
    # 保存合并后的CSV，使用utf-8-sig确保Excel兼容
    merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"Pandas合并完成！共 {len(merged_df)} 行数据已保存到: {output_file}")
    print(f"字段列表: {', '.join(merged_df.columns.tolist())}")
    print("文件已使用UTF-8 with BOM编码保存，可在Excel中直接打开")

def main():
    """
    主函数，提供多种合并方法供选择
    """
    # 配置路径
    csv_directory = "csv_directory"  # 替换为实际的CSV目录路径
    
    print("请选择合并方法:")
    print("1. 完整合并（处理字段不一致）")
    print("2. 简化合并（快速，假设结构相同）")
    print("3. 使用Pandas合并（需要安装pandas）")
    
    choice = input("请输入选择 (1/2/3): ").strip()
    
    if choice == "1":
        output_file = "merged_cards.csv"
        merge_csv_files(csv_directory, output_file)
    elif choice == "2":
        output_file = "merged_cards_simple.csv"
        merge_csv_files_simple(csv_directory, output_file)
    elif choice == "3":
        output_file = "merged_cards_pandas.csv"
        merge_csv_with_pandas(csv_directory, output_file)
    else:
        print("无效选择，使用默认方法1")
        output_file = "merged_cards.csv"
        merge_csv_files(csv_directory, output_file)

if __name__ == "__main__":
    main()