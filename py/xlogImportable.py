import os
import shutil
import time
import frontmatter  # pip install python-frontmatter

def move_files_to_root(root_folder: str) -> None:
    """将所有文件移动到根目录，同时删除空的子目录"""
    # 首先检查根目录是否为空
    if not os.listdir(root_folder):
        print(f"根目录 '{root_folder}' 为空文件夹，已跳过移动文件操作。")
        return

    # 找到所有子目录中的文件并移动到根目录
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            src_path = os.path.join(dirpath, filename)
            dst_path = os.path.join(root_folder, filename)
            count = 1
            while os.path.exists(dst_path):
                name, ext = os.path.splitext(filename)
                dst_path = os.path.join(root_folder, f"{name}_new({count}){ext}")
                count += 1
            shutil.move(src_path, dst_path, copy_function=shutil._samefile)

    # 删除所有空文件夹
    for dirpath, dirnames, filenames in os.walk(root_folder, topdown=False):
        for dirname in dirnames:
            subdir_path = os.path.join(dirpath, dirname)
            if not os.listdir(subdir_path):
                os.rmdir(subdir_path)

    print(f"成功将所有文件移动到根目录 '{root_folder}'，并删除所有空子文件夹。")

def delete_files_with_keywords(root_folder: str, target_keywords: list[str] = ["password"]) -> None:
    """根据关键字删除文件"""
    for filename in os.listdir(root_folder):
        file_path = os.path.join(root_folder, filename)
        if filename.endswith(".md"):
            with open(file_path, "r", encoding='utf-8') as f:
                content = f.read()
                md = frontmatter.loads(content)
                if any(keyword in md.keys() for keyword in target_keywords):
                    if os.path.exists(file_path):
                        f.close()
                        time.sleep(0.5)
                        os.remove(file_path)
                        print(f"已删除{filename}文件。")
                    else:
                        print(f"{filename}文件不存在。")

def remove_tags_from_directory(root_folder: str) -> None:
    """从子目录的所有文件中移除'tags'行"""
    count = 0
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith('.md'):
                full_pathname = os.path.join(dirpath, filename)
                try:
                    # 使用temp文件避免数据丢失
                    with open(full_pathname, 'r', encoding='utf-8') as f, open(full_pathname + '.temp', 'w', encoding='utf-8') as temp_f:
                        lines = f.readlines()
                        # 移除 tags 行
                        new_lines = [line for line in lines if not line.startswith('tags')]
                        temp_f.write(''.join(new_lines))
                    os.remove(full_pathname)
                    shutil.move(full_pathname + '.temp', full_pathname)
                    count += 1
                except Exception as e:
                    print(f"处理 {full_pathname} 时出错：{e}")
                    os.remove(full_pathname + '.temp')   # 如果出错则删除temp文件
    print(f"已完成，共处理了 {count} 个文件。")

def rename_markdown_files(root_folder: str) -> None:
    """将markdown文件根据alink行重命名"""
    for root, dirs, files in os.walk(root_folder):
        for filename in files:
            if filename.endswith('.md') or filename.endswith('.markdown'):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                for linenum, line in enumerate(lines):
                    if line.startswith('alink:'):
                        new_filename = line[len('alink:'):].strip()
                        new_file_path = os.path.join(root, f"{new_filename}")
                        if new_file_path != file_path:
                            shutil.move(file_path, new_file_path)

if __name__ == '__main__':
    while True:
        root_folder = input("xlogImportable:请输入根文件夹路径：").strip()
        if root_folder:
            break
        print("输入不能为空，请重新输入！")

    print("正在将所有文件移动到根目录，同时删除空的子目录")
    move_files_to_root(root_folder)

    # 根据关键字删除文件
    target_keywords = input("输入要删除的 md 文件中 front-matter 含有的属性：(默认为 password)，多个关键词之间用空格分隔：").split(" ")
    if not target_keywords or all(keyword.strip() == "" for keyword in target_keywords):
        target_keywords = ["password"]

    print("根据关键字删除文件")
    delete_files_with_keywords(root_folder, target_keywords)

    print("正在从子目录的所有文件中移除 'tags' 行（使用 'categories' 作为 xlog 的 'tags'）")
    remove_tags_from_directory(root_folder)

    print("正在将 markdown 文件根据 alink 行重命名")
    rename_markdown_files(root_folder)
