import os
from pathlib import Path
import mammoth
import markdownify
from pdf2docx import Converter


def pdf_to_docx(input):
    if str(input).endswith(".pdf"):
        output = str(input).replace(".pdf",".docx")

    cv=Converter(input)
    cv.convert(output,start=0,end=None)
    cv.close()
    return output




#此方法将pdf转为md文件，先转docx，再转md
def pdf_to_markdown(input):

    if str(input).endswith(".pdf"):
        md_file = str(input).replace(".pdf", ".md")
    docx=pdf_to_docx(input)

    # 读取 Word 文件
    with open(docx, "rb") as docx_file:
        # 转化 Word 文档为 HTML
        result = mammoth.convert_to_html(docx)
        # 获取 HTML 内容
        html = result.value
        # 转化 HTML 为 Markdown
        md = markdownify.markdownify(html, heading_style="ATX")
        print(md)
        with  open(md_file, "w",encoding='utf-8') as md_file:
            md_file.write(md)








def traverse_directory(path):
    """
    遍历目录下的所有文件
    :param path: 目录路径
    :return: 文件路径列表
    """
    file_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            file_list.append(file_path)
    return file_list

#返回file、fold、not exist、invalid
def file_or_folder(path):
    """
    判断输入路径是文件、目录还是不存在的路径

    参数:
        path (str): 要检查的路径

    返回:
        str:
            - "file" 如果路径指向一个文件
            - "directory" 如果路径指向一个目录
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
    #filepath=input("请输入制度文件夹路径")
    #outputpath=input("请输入输出文件夹路径")
    #filepath="C:/Users/Brokenhm/Desktop/img/test.pdf"
    #out="C:/Users/Brokenhm/Desktop/img/test.pdf"
    #pdf_to_markdown(filepath)
    print("如有多个需要转为markdown格式的制度请放置于文件夹内，文件必须是pdf格式")
    path=input("请输入一个目录或者文件的路径:\n")
    result=file_or_folder(path)
    if result.__eq__('file'):

        pdf_to_markdown(path)

    if result.__eq__("fold"):
        files=traverse_directory(path)
        for file in files:
            if str(file).endswith('.pdf'):
                pdf_to_markdown(file)
            print(str(file))
    elif result.__eq__('not exist'):
        print("输入有误，请重新输入")
    elif result.__eq__("invalid"):
        print("输入有误，请重新输入")



