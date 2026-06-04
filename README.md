# PDF限制移除工具

一款Windows桌面工具，用于移除PDF文件的权限限制，如打印、复制、编辑等限制。

## 功能

- 检测PDF文件的加密状态和权限限制
- 移除PDF文件的权限限制（打印、复制、编辑、注释等）
- 支持批量处理多个文件
- 支持文件拖拽到列表框
- 支持带密码的加密PDF文件
- 绿色单文件exe，无需安装

## 使用方法

### 直接运行exe

从 [Releases](https://github.com/asmartpig2020/RemovePDFRestrictions/releases) 页面下载最新版本的exe文件，双击运行即可。

### 从源码运行

```bash
pip install -r requirements.txt
python main.py
```

### 打包exe

```bash
pyinstaller --onefile --windowed --name "PDF限制移除工具" main.py
```

## 操作步骤

1. 通过以下方式添加PDF文件：
   - 点击「选择PDF文件」按钮
   - 点击「选择文件夹」按钮批量添加
   - 直接将PDF文件或文件夹拖拽到列表框
2. 如果PDF有用户密码，在密码框中输入
3. 点击「检测限制」查看权限状态
4. 点击「移除限制并保存」选择保存位置

## 技术栈

- Python
- pikepdf（基于QPDF引擎）
- tkinter + tkinterdnd2
- PyInstaller（打包）

## 许可证

本项目基于 **MIT Non-Commercial License** 发布，详见 [LICENSE](LICENSE)。

**你可以：**
- 免费使用、复制、修改、分发本软件
- 用于个人、教育或非商业用途

**你不能：**
- 售卖本软件（原始版本或修改版本）
- 将本软件作为付费产品或服务提供

**商业使用：**
- 如需将本软件用于商业目的，请联系作者获取授权
