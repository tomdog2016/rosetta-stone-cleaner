# -*- coding: utf-8 -*-
"""
注册表组件清理工具
作者：产品经理助手
创建日期：2025-03-15
描述：此脚本用于从Windows注册表中删除指定的组件项
"""

import os
import sys
import time
import ctypes
import winreg
import subprocess
from datetime import datetime

# 检查是否以管理员权限运行
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# 如果没有管理员权限，则请求提升权限
if not is_admin():
    print("此脚本需要管理员权限才能修改注册表。")
    print("正在请求管理员权限...")
    
    # 使用管理员权限重新启动脚本
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# 显示警告信息
def show_warning():
    print("\n" + "="*60)
    print("警告：此脚本将从注册表中删除指定的组件。".center(58))
    print("不正确的注册表操作可能导致系统不稳定或无法启动。".center(58))
    print("强烈建议在运行此脚本前创建系统还原点或注册表备份。".center(58))
    print("="*60 + "\n")
    
    confirmation = input("你确定要继续吗？输入'yes'继续，输入其他任何内容取消: ")
    return confirmation.lower() == 'yes'

# 创建注册表备份
def create_registry_backup():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    backup_file = os.path.join(desktop_path, f"ComponentsBackup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.reg")
    
    print(f"正在创建注册表备份到: {backup_file}")
    
    # 只备份Components目录，而不是整个Microsoft目录
    components_path = "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Installer\\UserData\\S-1-5-18\\Components"
    
    try:
        result = subprocess.run(
            ["reg", "export", components_path, backup_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("注册表备份已创建。")
            return backup_file
        else:
            print(f"注册表备份创建失败: {result.stderr}")
            return None
    except Exception as e:
        print(f"创建备份时出错: {str(e)}")
        return None

# 直接从Components目录删除指定的组件
def remove_components(components):
    removed_count = 0
    error_count = 0
    
    # 组件所在的注册表路径
    components_path = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Installer\\UserData\\S-1-5-18\\Components"
    
    # 使用Python的winreg模块直接操作注册表
    try:
        # 打开Components键
        components_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Installer\\UserData\\S-1-5-18\\Components",
            0,
            winreg.KEY_READ | winreg.KEY_WRITE
        )
        
        # 获取Components键下的子键数量
        subkey_count, value_count, last_modified = winreg.QueryInfoKey(components_key)
        
        print(f"找到 {subkey_count} 个组件，开始检查...")
        
        # 收集要删除的子键
        keys_to_delete = []
        
        # 遍历所有子键
        for i in range(subkey_count):
            try:
                # 获取子键名称
                subkey_name = winreg.EnumKey(components_key, i)
                
                # 检查是否在要删除的列表中
                if subkey_name in components:
                    keys_to_delete.append(subkey_name)
            except WindowsError as e:
                # 忽略已删除的键
                if e.winerror != 259:  # ERROR_NO_MORE_ITEMS
                    print(f"  枚举键时出错: {str(e)}")
        
        # 关闭键，准备删除操作
        winreg.CloseKey(components_key)
        
        # 删除收集到的键
        print(f"找到 {len(keys_to_delete)} 个匹配的组件，准备删除...")
        
        for key_name in keys_to_delete:
            try:
                # 使用reg delete命令删除键
                delete_path = f"{components_path}\\{key_name}"
                result = subprocess.run(
                    ["reg", "delete", delete_path, "/f"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print(f"  已删除: {key_name}")
                    removed_count += 1
                else:
                    print(f"  删除失败: {key_name}")
                    print(f"  错误信息: {result.stderr}")
                    error_count += 1
            except Exception as e:
                print(f"  删除键时出错: {key_name}")
                print(f"  错误信息: {str(e)}")
                error_count += 1
    
    except Exception as e:
        print(f"访问Components目录时出错: {str(e)}")
        error_count += 1
    
    return removed_count, error_count

# 主函数
def main():
    if not show_warning():
        print("操作已取消。")
        return
    
    backup_file = create_registry_backup()
    if not backup_file:
        print("无法创建注册表备份，脚本将退出。")
        return
    
    # 要删除的组件列表（从图片中提取）
    components_to_remove = [
        "013DB16CAB2C22A469A4E685824BA845",
        "040A459FB93A7C345A5D5184F5A9D1FC",
        "050968945C6E5B4B957014B4F24A5C7",
        "051056AFD4A72015983E34927EBEA02",
        "062BA804C42F88D598438AB2F719690",
        "0802B5A6EF0CE8E99A49E55BC047E282",
        "0A16B912A6CF47D509F7E93A4D43714D",
        "0E589F038BF0D1E51AB2388B086ABF8E",
        "11B3E070A192FB152A9C8CFB4EF153BA",
        "1419ECB0BC2FD248A7457C977C98F90",
        "152933CA21098D428E9F73123B23F09",
        "156F0A8CB8EEC35684B1DC5C020A1D1",
        "1732458BD99D2115A824A048DEF376DD",
        "17A291059CAF79159AE0735BA9A2D842",
        "1A03F8A1022DFB85481485BADA9B579B",
        "1A0EC7A5050942359B9583CF444A934AC",
        "1AEAC25945AECA857827C581C1D0935",
        "1CBDA723DDCCA9E408533AF5F4A7DCB",
        "1D87CC923877F9839B4E3BBFAF4019",
        "20A9C3D58595849A9575F9569934638",
        "20C442A7837FC9E5ABAB788CF585CC4A",
        "2187B41EC9DE0AE5A8C30464DBAD20AF",
        "219124F2F4C3D274D865869DADC75F9",
        "22F4C7B38BE9BE853A1F9BCD928E4395",
        "234475628388E125FB44B5DC1B66074",
        "2363D3C7E4D414C4FA11DE567A4E60E7",
        "242DD62E1AC9D5E449051A7C0FC17EA",
        "243A4D7CC7EFEB850A05445B4FE4A344",
        "2562EE168AAFF6C578C19AA8D2E36BC4",
        "285F70666AE86874FACBE45F6A8F48DD",
        "288ACB98ECD43CF549DDBAE5EE42FFB2",
        "28A12CC3FC9599557859285392BEDF4",
        "2A67139774512F4FA43348E4182E079",
        "2A6F6D311D70E96508F4D1EBCC9D2EFD",
        "2AA9F0DF037D9CC4F8692364B446B203",
        "2BD99D7E377BB384EB41398DEC7F2D0",
        "2E59FCDAE6CD2825C8692EE9518007DA",
        "2E75D00B0D6C7C8429C8D29A960C4A05",
        "2FC173EEC6F6C8A49B35788FC6BFB237",
        "3049DF9378489ED599F9BD1DCF98F9A3",
        "324BAE9B472552947B1F33DB1E2EA962",
        "32DBF6AF0575C6D5B8C985A4C5F6C138"
        # 这里只列出了部分组件，实际使用时应包含所有需要删除的组件
    ]
    
    # 删除组件
    removed_count, error_count = remove_components(components_to_remove)
    
    # 总结
    print("\n操作完成！")
    print(f"成功删除: {removed_count} 项")
    if error_count > 0:
        print(f"删除失败: {error_count} 项")
    print(f"注册表备份位置: {backup_file}")
    print("\n如果系统出现问题，可以通过双击备份文件恢复注册表。")
    
    # 提示重启
    restart_confirmation = input("\n建议重启系统以应用更改。是否现在重启？输入'yes'重启，输入其他任何内容取消: ")
    if restart_confirmation.lower() == 'yes':
        print("系统将在5秒后重启...")
        for i in range(5, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        os.system("shutdown /r /t 0")
    else:
        print("请记得稍后手动重启系统。")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n操作已被用户中断。")
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
    finally:
        input("\n按Enter键退出...")
