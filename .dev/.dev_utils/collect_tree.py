# collect_tree.py

import os
import argparse


def write_py_file_tree_with_top_folder(root_folder, output_file, types=["py"], exclude_folders=[]):
    root_folder_name = os.path.basename(os.path.normpath(root_folder))  # 최상위 폴더명 가져오기
    with open(output_file, "w") as file:
        for dirpath, _, filenames in os.walk(root_folder):
            # 제외할 폴더명
            if any(folder in dirpath for folder in exclude_folders):
                continue
            # type 확장자 파일들만 필터링
            py_files = [f for f in filenames if f.endswith(tuple(f".{type}" for type in types))]
            if py_files:
                for py_file in py_files:
                    # 경로와 파일명을 원하는 형식으로 작성
                    relative_path = os.path.relpath(dirpath, root_folder)
                    full_path = os.path.join(root_folder_name, relative_path)  # 상위 폴더명 포함 경로
                    file.write(f"{full_path}: {py_file}\n")
    print(output_file, "파일이 생성되었습니다.")


### 사용 예시: python collect_tree.py -p C:\{프로젝트 경로} -o dart_file_tree.txt -t dart
if __name__ == "__main__":
    defaultPath: str = r"C:\Users\devra\StudioProjects\Fastapi_Restful_API_Template\fastapi_template"
    defaultOutput: str = os.path.join(r"C:\Users\devra\StudioProjects\Fastapi_Restful_API_Template\fastapi_template", "py_project_tree.txt") # os.path.join(os.path.dirname(__file__), "py_project_tree.txt")
    defaultTypes: str = ["py", "md", "yml", "txt", ]
    exclude_folders: list = ["node_modules", ".git", "venv", "_dev"]
    parser = argparse.ArgumentParser(description="Generate a tree of .py files with top folder.")
    parser.add_argument("-p", "--path", default=defaultPath, help="The root folder to scan.")
    parser.add_argument("-o", "--output", default=defaultOutput, help="The output file to write the tree.")
    parser.add_argument("-t", "--types", default=defaultTypes, help="The file type to scan.")
    parser.add_argument("-e", "--exclude", default=exclude_folders, help="The folder to exclude.")
    args = parser.parse_args()

    write_py_file_tree_with_top_folder(args.path, args.output, args.types, args.exclude)