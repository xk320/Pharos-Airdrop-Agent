# Pharos 空投助手

- 注册地址：[Pharos 测试网](https://testnet.pharosnetwork.xyz/experience?inviteCode=i1oh5oYCBA2Ts4MY)
- 连接新钱包
- 连接 X（推特）和 Discord

## 主要功能

  - 自动获取信息
  - 自动使用 [Proxyscrape 免费代理](https://proxyscrape.com/free-proxy-list) 运行 - 选项1
  - 自动使用自定义代理运行 - 选项2
  - 自动运行（不使用代理）- 选项3
  - 自动轮换无效代理 - 选择 y 或 n
  - 自动每日签到领取奖励
  - 自动领取 Faucet PHRS - USDC - USDT
  - 自动转账到随机地址
  - 自动在 PHRS 和 WPHRS 之间兑换
  - 自动添加 LP WPHRS/USDC - WPHRS/USDT
  - 自动兑换 WPHRS - USDC - USDT
  - 支持同时运行多个钱包

## 要求

- 请确保您的电脑已安装 Python 3.9 或更高版本，并已安装 pip

## 安装方法

1. 下载本仓库并解压，用 Cursor 或 VSC 打开

2. 安装所需依赖库：
   ```bash
   pip install -r requirements.txt # 或 pip3 install -r requirements.txt
   ```

## 配置钱包和代理

- **accounts.txt：** 只需将私钥填入此文件，每行一个私钥，支持多钱包：
  ```bash
    your_private_key_1
    your_private_key_2
  ```

- **proxy.txt：** 如有代理，将代理粘贴到此文件，每行一个，支持多钱包：
  ```bash
    ip:port # 默认协议 HTTP。
    protocol://ip:port
    protocol://user:pass@ip:port
  ```

## 运行脚本：

```bash
python bot.py
```

## 如果你喜欢这个脚本，欢迎请我喝杯咖啡

- **EVM:** 0x70A5a4ede89ED613307d255659a1dD837D9418a1
- **SOL:** AwXQn61FFabdV4iDjzCNTHtx2yanGDiEEh7KY4MKVZS2
- **SUI:** 0xc99395ead375fe240f0edd28acb12e3360ffe1e83bbd1d782b3208fc57fe338c

欢迎关注和 star，感谢你的支持，祝你空投愉快，记得保护好自己的资产！

**</velhust/>**
