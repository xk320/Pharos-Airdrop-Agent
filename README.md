# Pharos 空投助手

一个功能强大的Web3空投自动化工具，支持Pharos测试网、AutoStaking和Brokex等多个平台的自动化操作。

## 🌟 主要功能

### Pharos 测试网 (bot.py)
- ✅ 自动登录和身份验证
- ✅ 自动每日签到领取奖励
- ✅ 自动领取 Faucet (PHRS, USDC, USDT)
- ✅ 自动转账到随机地址
- ✅ 自动在 PHRS 和 WPHRS 之间兑换
- ✅ 自动添加流动性 (WPHRS/USDC, WPHRS/USDT)
- ✅ 自动代币兑换 (WPHRS ↔ USDC ↔ USDT)
- ✅ 支持多钱包并发运行
- ✅ 支持自定义代理

### AutoStaking 平台 (AutoStaking.py)
- ✅ 自动领取 Faucet
- ✅ 智能投资组合推荐
- ✅ 自动质押操作
- ✅ 支持 USDC, USDT, MUSD 代币
- ✅ 多钱包管理

### Brokex 交易平台 (Brokex.py)
- ✅ 自动领取 Faucet
- ✅ 自动开仓/平仓操作
- ✅ 流动性挖矿 (LP 存款/提款)
- ✅ 支持杠杆交易
- ✅ 多钱包并发操作

### FaroSwap 去中心化交易所 (FaroSwap.py)
- ✅ 自动代币交换 (PHRS, WPHRS, USDC, USDT, WETH, WBTC)
- ✅ 自动添加 DVM 流动性
- ✅ 智能路由选择 (Dodo API)
- ✅ 支持多种交易对
- ✅ 多钱包并发操作
- ✅ 随机交易金额和延迟

### DomainName 域名注册 (DomainName.py)
- ✅ 自动注册 .phrs 域名
- ✅ 批量域名注册
- ✅ 随机域名生成
- ✅ 多线程并发注册
- ✅ 代理支持
- ✅ 进度跟踪和错误重试

## 📋 系统要求

### 基础要求
- **Python**: 3.9 或更高版本
- **pip**: Python 包管理器
- **网络**: 稳定的网络连接
- **代理**: 可选的代理服务器

### 推荐配置
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **内存**: 至少 4GB RAM
- **存储**: 至少 1GB 可用空间
- **网络**: 稳定的互联网连接，推荐使用代理

### 开发环境（可选）
- **IDE**: VS Code, PyCharm, 或 Cursor
- **Git**: 用于版本控制
- **虚拟环境**: 推荐使用 venv 或 conda

## 🚀 快速开始

### 1. 环境准备

#### 检查Python版本
首先检查您的系统是否已安装Python：

```bash
python --version  # 检查Python版本
pip --version     # 检查pip版本
```

如果显示版本号且版本 >= 3.9，则可跳过安装步骤。

#### 各系统Python安装指南

**Windows 系统：**
1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载 Python 3.9+ 安装包
3. 运行安装程序，**重要：勾选 "Add Python to PATH"**
4. 验证安装：
   ```cmd
   python --version
   pip --version
   ```

**macOS 系统：**
```bash
# 使用 Homebrew 安装（推荐）
brew install python@3.9

# 或使用官方安装包
# 1. 访问 https://www.python.org/downloads/macos/
# 2. 下载并安装 .pkg 文件

# 验证安装
python3 --version
pip3 --version
```

**Ubuntu/Debian Linux：**
```bash
# 更新包管理器
sudo apt update

# 安装Python 3.9+
sudo apt install python3.9 python3.9-pip python3.9-venv

# 创建软链接（可选）
sudo ln -s /usr/bin/python3.9 /usr/bin/python3
sudo ln -s /usr/bin/pip3.9 /usr/bin/pip3

# 验证安装
python3 --version
pip3 --version
```

**CentOS/RHEL/Fedora：**
```bash
# CentOS/RHEL 8+
sudo dnf install python3.9 python3.9-pip

# 或使用 EPEL 仓库
sudo yum install epel-release
sudo yum install python3.9 python3.9-pip

# 验证安装
python3.9 --version
pip3.9 --version
```

**使用 pyenv（推荐用于多版本管理）：**
```bash
# 安装 pyenv
curl https://pyenv.run | bash

# 添加到 shell 配置
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# 重新加载配置
source ~/.bashrc

# 安装Python 3.9+
pyenv install 3.9.18
pyenv global 3.9.18

# 验证安装
python --version
pip --version
```

### 2. 下载和安装

#### 获取项目代码
```bash
# 方法1：使用 Git 克隆（推荐）
git clone <repository-url>
cd Pharos-Airdrop-Agent

# 方法2：直接下载 ZIP 文件
# 1. 点击项目页面的 "Code" -> "Download ZIP"
# 2. 解压到本地目录
# 3. 进入项目目录
```

#### 安装依赖包
```bash
# 使用 pip 安装依赖
pip install -r requirements.txt

# 如果遇到权限问题，使用：
pip install --user -r requirements.txt

# 在 Linux/macOS 上可能需要使用：
pip3 install -r requirements.txt

# 建议使用虚拟环境（推荐）：
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

#### 验证安装
```bash
# 检查关键依赖是否安装成功
python -c "import web3, aiohttp, eth_account; print('依赖安装成功！')"
```

### 3. 配置钱包

编辑 `accounts.txt` 文件，添加您的私钥（每行一个）：

```txt
your_private_key_1
your_private_key_2
your_private_key_3
```

⚠️ **安全提醒**：请妥善保管您的私钥，不要泄露给他人。

### 4. 配置代理（可选）

如果您需要使用代理，编辑 `proxy.txt` 文件：

```txt
# HTTP代理
ip:port

# 带认证的代理
http://user:pass@ip:port
```


## 🎯 使用方法

### Pharos 测试网操作

```bash
python bot.py
```

运行后选择以下功能：
1. **每日签到** - 自动签到领取奖励
2. **领取 Faucet** - 自动领取测试代币
3. **转账操作** - 向随机地址转账
4. **代币兑换** - PHRS ↔ WPHRS 兑换
5. **添加流动性** - 为交易对添加流动性
6. **代币交换** - 在不同代币间交换

### AutoStaking 操作

```bash
python AutoStaking.py
```

功能包括：
- 自动领取 Faucet
- 智能投资组合推荐
- 自动质押操作

### Brokex 交易操作

```bash
python Brokex.py
```

功能包括：
- 自动领取 Faucet
- 杠杆交易开仓/平仓
- 流动性挖矿操作

### FaroSwap 交易操作

```bash
python FaroSwap.py
```

功能包括：
- 自动代币交换 (支持6种代币)
- 自动添加流动性
- 智能路由优化
- 批量交易执行

### DomainName 域名注册

```bash
python DomainName.py
```

功能包括：
- 自动注册 .phrs 域名
- 批量域名管理
- 随机域名生成
- 并发注册处理

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `bot.py` | Pharos 测试网主程序 |
| `AutoStaking.py` | AutoStaking 平台自动化脚本 |
| `Brokex.py` | Brokex 交易平台自动化脚本 |
| `FaroSwap.py` | FaroSwap DEX 自动化交易模块 |
| `DomainName.py` | Pharos 域名注册自动化模块 |
| `getsorce.py` | 数据获取模块 |
| `accounts.txt` | 钱包私钥配置文件 |
| `proxy.txt` | 代理服务器配置文件 |
| `pools.json` | 流动性池配置 |
| `requirements.txt` | Python 依赖包列表 |

## ⚙️ 配置说明

### 网络配置
- **Pharos RPC**: `https://testnet.dplabs-internal.com`
- **合约地址**: 已预配置在脚本中


```

## ⚠️ 注意事项

1. **私钥安全**：请确保 `accounts.txt` 文件安全，不要上传到公共仓库
2. **网络稳定**：建议使用稳定的网络连接，必要时配置代理
3. **资金风险**：测试网操作不会损失真实资金，但请谨慎操作
4. **频率限制**：避免过于频繁的操作，以免触发平台限制
5. **合规使用**：请遵守各平台的使用条款和规则
6. **域名注册**：DomainName 模块会消耗真实 ETH 进行域名注册
7. **交易风险**：FaroSwap 和 Brokex 的交易操作需要谨慎评估风险
8. **并发控制**：合理设置并发数量，避免对网络造成过大压力

## 🐛 故障排除

### 常见问题

1. **连接超时**
   - 检查网络连接
   - 尝试使用代理
   - 增加重试次数

2. **私钥错误**
   - 确认私钥格式正确
   - 检查是否有额外空格或换行

3. **依赖包错误**
   ```bash
   # 升级 pip
   python -m pip install --upgrade pip
   
   # 重新安装依赖
   pip install --upgrade -r requirements.txt
   
   # 如果仍有问题，尝试：
   pip install --force-reinstall -r requirements.txt
   ```

4. **权限错误**
   ```bash
   # Linux/macOS 权限问题
   chmod +x *.py
   
   # Windows 权限问题
   # 以管理员身份运行命令提示符
   
   # pip 权限问题
   pip install --user -r requirements.txt
   ```

5. **域名注册失败**
   - 检查 ETH 余额是否充足
   - 确认域名是否已被注册
   - 检查网络连接和代理设置

6. **交易失败**
   - 检查代币余额和授权状态
   - 确认滑点设置是否合理
   - 检查网络拥堵情况

## 📞 支持

如果您遇到问题或有建议，请：
1. 检查本文档的故障排除部分
2. 查看代码注释和错误信息
3. 确保使用最新版本的依赖包

## 📄 许可证

本项目仅供学习和研究使用，请遵守相关法律法规和平台规则。

---

**免责声明**：本工具仅供技术学习和研究使用，使用者需自行承担使用风险，开发者不承担任何责任。
