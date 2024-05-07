# https://github.com/oobabooga/one-click-installers

import requests
import os
import subprocess
import zipfile
import sys

script_dir = os.getcwd()

def run_cmd(cmd, assert_success=False, environment=False, capture_output=False, env=None):
    # Use the conda environment
    if environment:
        conda_env_path = os.path.join(script_dir, "installer_files", "env")
        if sys.platform.startswith("win"):
            conda_bat_path = os.path.join(script_dir, "installer_files", "conda", "condabin", "conda.bat")
            cmd = "\"" + conda_bat_path + "\" activate \"" + conda_env_path + "\" >nul && " + cmd
        else:
            conda_sh_path = os.path.join(script_dir, "installer_files", "conda", "etc", "profile.d", "conda.sh")
            cmd = ". \"" + conda_sh_path + "\" && conda activate \"" + conda_env_path + "\" && " + cmd

    # Run shell commands
    result = subprocess.run(cmd, shell=True, capture_output=capture_output, env=env)

    # Assert the command ran successfully
    if assert_success and result.returncode != 0:
        print("Command '" + cmd + "' failed with exit status code '" + str(result.returncode) + "'. Exiting...")
        sys.exit()
    return result


def check_env():
    # If we have access to conda, we are probably in an environment
    conda_exist = run_cmd("conda", environment=True, capture_output=True).returncode == 0
    if not conda_exist:
        print("Conda is not installed. Exiting...")
        sys.exit()

    # Ensure this is a new environment and not the base environment
    if os.environ["CONDA_DEFAULT_ENV"] == "base":
        print("Create an environment for this project and activate it. Exiting...")
        sys.exit()

def install_dependencies():
    # Install the webui dependencies
    print('选择一种依赖安装方式:\n')
    print('1: 使用pypi官方\n')
    print('2: 使用阿里源\n')
    try:
        choice = int(input('\n输入1或2. 然后敲回车: '))
    except:
        choice = 1

    if choice == 1:
        run_cmd("python -m pip install -r requirements.txt --upgrade -i https://pypi.org/simple/", assert_success=True, environment=True)
    if choice == 2:
        run_cmd("python -m pip install -r requirements.txt --upgrade -i https://mirrors.aliyun.com/pypi/simple/", assert_success=True, environment=True)
    else:
        run_cmd("python -m pip install -r requirements.txt --upgrade -i https://mirrors.aliyun.com/pypi/simple/", assert_success=True, environment=True)

ready_msg = """

一切准备就绪!

- （重要）请确保 gpt_academic/config.py 中已经配置了正确的设置选项.
- （重要）关于如何配置项目, 请查看 `https://github.com/binary-husky/gpt_academic/wiki`.
- 关闭此窗口即可结束本程序, 下次运行时, 仍然是启动`Windows双击这里运行.bat` (或者`MacOS点击这里运行.sh`)
- 如需卸载, 删除整个文件夹即可

当您准备完毕后, 请敲回车继续.
"""

def run_model():
    input(ready_msg)
    run_cmd(f"python main.py", environment=True)


if __name__ == "__main__":
    if not os.path.exists('./gpt_academic/main.py'):
        print('正在从Github获取代码...')
        print('选择一种代码获取方式:\n')
        print('1: 自动: 连接站长镜像下载（可能会下载到非最新版本）\n')
        print('2: 自动: 请选择1）\n')

        choice = int(input('\n\n输入1或者2. 然后敲回车: '))

        if choice == 1:
            r = requests.get('https://web-1306273238.cos.ap-beijing.myqcloud.com/%E4%B8%8B%E8%BD%BD/master.zip', stream=True)
            zip_file_path = './frontier_master.zip'
            with open(zip_file_path, 'wb+') as f:
                cnt = 0
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
                        cnt += 1
                        if cnt%20==0: print('.', end='', flush=True)
            print('下载完成')
            with zipfile.ZipFile(zip_file_path, 'r') as zipobj:
                zipobj.extractall(path='./')
                print("解压完成")
            while True:
                if os.path.exists('./gpt_academic-frontier/main.py'):
                    os.rename('gpt_academic-frontier', 'gpt_academic')
                    break
                input('尚未检测到gpt_academic-frontier文件夹, 请尝试方法3, 回车重试.')

        elif choice == 2:
            run_cmd("git clone --depth=1 https://github.com/binary-husky/gpt_academic.git -b frontier", assert_success=True, environment=True)

        elif choice == 3:
            while True:
                if os.path.exists('./gpt_academic-frontier/main.py'):
                    os.rename('gpt_academic-frontier', 'gpt_academic')
                    break
                input('尚未检测到gpt_academic-frontier文件夹, 回车重试.')
        else:
            assert False, '未知选项'

    # Verifies we are in a conda environment
    check_env()

    # If webui has already been installed, skip and run
    if os.path.exists("gpt_academic/"):
        os.chdir("gpt_academic")
        install_dependencies()
        run_model()
