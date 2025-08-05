import os
from pathlib import Path
import mammoth
import markdownify
from pdf2docx import Converter


def pdf_to_docx(input_path):
    """将PDF转换为DOCX文件"""
    cv = None
    try:
        if not str(input_path).endswith(".pdf"):
            print(f"跳过非PDF文件: {input_path}")
            return None

        output = str(input_path).replace(".pdf", ".docx")

        # 检查文件是否存在且可读
        if not os.path.exists(input_path):
            print(f"文件不存在: {input_path}")
            return None

        # 检查文件大小
        if os.path.getsize(input_path) == 0:
            print(f"文件为空: {input_path}")
            return None

        cv = Converter(input_path)
        cv.convert(output, start=0, end=None)
        cv.close()
        return output

    except FileNotFoundError:
        print(f"文件未找到: {input_path}")
        return None
    except PermissionError:
        print(f"文件权限不足: {input_path}")
        return None
    except Exception as e:
        error_msg = str(e).lower()
        if any(keyword in error_msg for keyword in ['corrupt', 'damaged', 'invalid', 'password', 'encrypted']):
            print(f"PDF文件损坏或加密，无法处理: {input_path}")
        elif 'memory' in error_msg:
            print(f"内存不足，跳过大文件: {input_path}")
        else:
            print(f"转换PDF到DOCX时出错 - {input_path}: {str(e)}")
        return None
    finally:
        # 确保转换器被正确关闭
        if cv is not None:
            try:
                cv.close()
            except:
                pass


def pdf_to_markdown(input_path, keep_docx=True):
    """将PDF转换为Markdown文件，先转DOCX，再转MD"""
    docx_path = None
    try:
        if not str(input_path).endswith(".pdf"):
            print(f"跳过非PDF文件: {input_path}")
            return False

        print(f"正在处理: {input_path}")
        md_file_path = str(input_path).replace(".pdf", ".md")

        # 转换PDF到DOCX
        docx_path = pdf_to_docx(input_path)
        if docx_path is None:
            print(f"跳过文件（PDF转DOCX失败）: {input_path}")
            return False

        # 检查DOCX文件是否成功生成
        if not os.path.exists(docx_path) or os.path.getsize(docx_path) == 0:
            print(f"生成的DOCX文件无效: {input_path}")
            # 如果DOCX生成失败，尝试删除可能存在的空文件
            if os.path.exists(docx_path):
                try:
                    os.remove(docx_path)
                except:
                    pass
            return False

        # 读取Word文件并转换为Markdown
        try:
            with open(docx_path, "rb") as docx_file:
                # 转化Word文档为HTML
                result = mammoth.convert_to_html(docx_file)
                # 获取HTML内容
                html = result.value

                # 检查是否成功提取内容
                if not html or html.strip() == "":
                    print(f"从DOCX中未提取到有效内容: {input_path}")
                    # 如果提取内容失败，删除DOCX文件
                    if not keep_docx and os.path.exists(docx_path):
                        try:
                            os.remove(docx_path)
                        except:
                            pass
                    return False

                # 转化HTML为Markdown
                md = markdownify.markdownify(html, heading_style="ATX")

                # 写入Markdown文件
                with open(md_file_path, "w", encoding='utf-8') as md_file:
                    md_file.write(md)

                if keep_docx:
                    print(
                        f"✓ 成功转换: {os.path.basename(input_path)} -> {os.path.basename(docx_path)} + {os.path.basename(md_file_path)}")
                else:
                    print(f"✓ 成功转换: {os.path.basename(input_path)} -> {os.path.basename(md_file_path)}")

                return True

        except UnicodeDecodeError:
            print(f"文件编码错误: {input_path}")
            # 编码错误时，根据设置决定是否保留DOCX
            if not keep_docx and os.path.exists(docx_path):
                try:
                    os.remove(docx_path)
                except:
                    pass
            return False
        except MemoryError:
            print(f"内存不足，无法处理: {input_path}")
            if not keep_docx and os.path.exists(docx_path):
                try:
                    os.remove(docx_path)
                except:
                    pass
            return False
        except Exception as e:
            print(f"读取DOCX或转换Markdown时出错 - {input_path}: {str(e)}")
            if not keep_docx and os.path.exists(docx_path):
                try:
                    os.remove(docx_path)
                except:
                    pass
            return False

    except KeyboardInterrupt:
        print("\n用户中断程序")
        raise
    except Exception as e:
        print(f"处理文件时发生未知错误 - {input_path}: {str(e)}")
        # 发生未知错误时，根据设置决定是否保留DOCX
        if not keep_docx and docx_path and os.path.exists(docx_path):
            try:
                os.remove(docx_path)
            except:
                pass
        return False


def traverse_directory(path):
    """
    遍历目录下的所有文件
    :param path: 目录路径
    :return: 文件路径列表
    """
    file_list = []
    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                file_list.append(file_path)
    except Exception as e:
        print(f"遍历目录时出错 {path}: {str(e)}")
    return file_list


def file_or_folder(path):
    """
    判断输入路径是文件、目录还是不存在的路径
    参数:
        path (str): 要检查的路径
    返回:
        str: - "file" 如果路径指向一个文件
             - "fold" 如果路径指向一个目录
             - "not exist" 如果路径不存在
             - "invalid" 如果路径格式无效
    """
    try:
        # 使用Path对象处理路径（兼容Windows和Unix）
        path_obj = Path(path)
        if path_obj.exists():
            if path_obj.is_file():
                return "file"
            elif path_obj.is_dir():
                return "fold"
        else:
            return "not exist"
    except (TypeError, OSError):
        # 处理非法路径（如包含非法字符）
        return "invalid"


if __name__ == '__main__':
    print("如有多个需要转为markdown格式的制度请放置于文件夹内，文件必须是pdf格式")
    path = input("请输入一个目录或者文件的路径:\n")
    result = file_or_folder(path)

    success_count = 0
    error_count = 0

    if result == 'file':
        if pdf_to_markdown(path):
            success_count += 1
        else:
            error_count += 1

    elif result == "fold":
        files = traverse_directory(path)
        pdf_files = [file for file in files if str(file).endswith('.pdf')]

        if not pdf_files:
            print("在指定目录中未找到PDF文件")
        else:
            print(f"找到 {len(pdf_files)} 个PDF文件，开始处理...")

            for i, file in enumerate(pdf_files, 1):
                try:
                    print(f"\n[{i}/{len(pdf_files)}] 处理文件: {os.path.basename(file)}")
                    if pdf_to_markdown(file):
                        success_count += 1
                    else:
                        error_count += 1
                except KeyboardInterrupt:
                    print(f"\n用户中断，已处理 {i - 1} 个文件")
                    break
                except Exception as e:
                    print(f"处理文件时发生严重错误 {file}: {str(e)}")
                    error_count += 1
                    continue

    elif result == 'not exist':
        print("输入有误，路径不存在，请重新输入")

    elif result == "invalid":
        print("输入有误，路径格式无效，请重新输入")

    # 显示处理结果统计
    if success_count > 0 or error_count > 0:
        print(f"\n处理完成！")
        print(f"成功转换: {success_count} 个文件")
        print(f"处理失败: {error_count} 个文件")