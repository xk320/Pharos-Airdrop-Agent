import threading
import queue
import random
import time
import os
import string
from web3 import Web3, HTTPProvider
from eth_account import Account
from hexbytes import HexBytes
import logging
from typing import List, Tuple
import requests
from concurrent.futures import ThreadPoolExecutor
from urllib3.exceptions import HTTPError

from colorama import *
import pytz
from datetime import datetime
import asyncio

wib = pytz.timezone('Asia/Jakarta')
init(autoreset=True)

class DomainName:
    DEFAULT_CONFIG = {
        'RPC_URL': "https://testnet.dplabs-internal.com",
        'CONTROLLER_ADDRESS': "0x51be1ef20a1fd5179419738fc71d95a8b6f8a175",
        'DURATION': 31536000,
        'RESOLVER': "0x9a43dcA1C3BB268546b98eb2AB1401bFc5b58505",
        'DATA': [],
        'REVERSE_RECORD': True,
        'OWNER_CONTROLLED_FUSES': 0,
        'CHAIN_ID': 688688,
        'REG_PER_KEY': 1,
        'MAX_CONCURRENCY': 5
    }

    CONTROLLER_ABI = [
        {
            "constant": True,
            "inputs": [
                {"name": "name", "type": "string"},
                {"name": "owner", "type": "address"},
                {"name": "duration", "type": "uint256"},
                {"name": "secret", "type": "bytes32"},
                {"name": "resolver", "type": "address"},
                {"name": "data", "type": "bytes[]"},
                {"name": "reverseRecord", "type": "bool"},
                {"name": "ownerControlledFuses", "type": "uint16"}
            ],
            "name": "makeCommitment",
            "outputs": [{"name": "", "type": "bytes32"}],
            "stateMutability": "pure",
            "type": "function"
        },
        {
            "constant": False,
            "inputs": [{"name": "commitment", "type": "bytes32"}],
            "name": "commit",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [
                {"name": "name", "type": "string"},
                {"name": "duration", "type": "uint256"}
            ],
            "name": "rentPrice",
            "outputs": [
                {
                    "components": [
                        {"name": "base", "type": "uint256"},
                        {"name": "premium", "type": "uint256"}
                    ],
                    "name": "",
                    "type": "tuple"
                }
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": False,
            "inputs": [
                {"name": "name", "type": "string"},
                {"name": "owner", "type": "address"},
                {"name": "duration", "type": "uint256"},
                {"name": "secret", "type": "bytes32"},
                {"name": "resolver", "type": "address"},
                {"name": "data", "type": "bytes[]"},
                {"name": "reverseRecord", "type": "bool"},
                {"name": "ownerControlledFuses", "type": "uint16"}
            ],
            "name": "register",
            "outputs": [],
            "stateMutability": "payable",
            "type": "function"
        }
    ]

    def __init__(self):
        self.config = self.DEFAULT_CONFIG.copy()
        self.accounts_file = "accounts.txt"
        self.proxy_file = "proxy.txt"
        self.accounts = self.load_file_lines(self.accounts_file)
        self.proxies = self.load_and_test_proxies(self.proxy_file) if self.proxy_file else []
        self.success_count = 0
        self.failed_count = 0
        self.total_tasks = 0
        self.current_tasks_processed = 0
        self.processed_lock = threading.Lock()

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"\
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def load_file_lines(self, filename: str) -> List[str]:
        try:
            with open(filename, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"{Fore.RED+Style.BRIGHT}未找到文件 '{filename}'.{Style.RESET_ALL}")
            return []

    def random_name(self, length: int = 9) -> str:
        if length < 3:
            length = 3
        chars_letters = string.ascii_lowercase
        chars_letters_digits = string.ascii_lowercase + string.digits
        name_list = []
        name_list.append(random.choice(chars_letters))
        for _ in range(length - 1):
            if name_list[-1] == '-':
                name_list.append(random.choice(chars_letters_digits))
            else:
                name_list.append(random.choice(chars_letters_digits + '-' * 1))
        if name_list[-1] == '-':
            name_list[-1] = random.choice(chars_letters_digits)
        cleaned_name = []
        for i, char in enumerate(name_list):
            if char == '-' and i > 0 and cleaned_name and cleaned_name[-1] == '-':
                cleaned_name.append(random.choice(chars_letters_digits))
            else:
                cleaned_name.append(char)
        while len(cleaned_name) < length:
            if cleaned_name and cleaned_name[-1] == '-':
                cleaned_name.append(random.choice(chars_letters_digits))
            else:
                cleaned_name.append(random.choice(chars_letters_digits + '-'))
        final_result = ''.join(cleaned_name[:length])
        if final_result.startswith('-'):
            final_result = random.choice(chars_letters_digits) + final_result[1:]
        if final_result.endswith('-'):
            final_result = final_result[:-1] + random.choice(chars_letters_digits)
        final_result = final_result.replace('--', random.choice(chars_letters_digits) + random.choice(chars_letters_digits))
        while len(final_result) < length:
            final_result += random.choice(chars_letters_digits)
        return final_result[:length]

    def validate_private_key(self, private_key: str) -> bool:
        if private_key.startswith('0x'):
            private_key = private_key[2:]
        if len(private_key) != 64 or not all(c in string.hexdigits for c in private_key):
            return False
        return True

    def test_proxy(self, proxy: str) -> Tuple[str, bool]:
        try:
            return proxy, True
        except (requests.RequestException, HTTPError) as e:
            print(f"{Fore.YELLOW+Style.BRIGHT}警告: {Fore.RED+Style.BRIGHT}代理 {proxy} 测试失败: {e}.{Style.RESET_ALL}")
            return proxy, False

    def load_and_test_proxies(self, proxy_file: str) -> List[str]:
        raw_proxy_list = self.load_file_lines(proxy_file)
        if not raw_proxy_list:
            print(f"{Fore.YELLOW+Style.BRIGHT}警告: 未找到代理文件 '{proxy_file}' 或文件为空。{Style.RESET_ALL}")
            return []
        proxy_test_workers = min(len(raw_proxy_list), os.cpu_count() * 2 if os.cpu_count() else 10)
        if proxy_test_workers == 0 and len(raw_proxy_list) > 0:
            proxy_test_workers = 1
        if proxy_test_workers > 0:
            with ThreadPoolExecutor(max_workers=proxy_test_workers) as executor:
                tested_proxies_results = list(executor.map(self.test_proxy, raw_proxy_list))
            proxy_list = [p for p, success in tested_proxies_results if success]
        else:
            proxy_list = []
        if not proxy_list:
            print(f"{Fore.YELLOW+Style.BRIGHT}警告: 未找到功能代理。{Style.RESET_ALL}")
        else:
            pass
        return proxy_list

    def create_web3_instance(self, proxy: str = None) -> Web3:
        if proxy:
            session = requests.Session()
            session.proxies = {'http': proxy, 'https': proxy}
            return Web3(HTTPProvider(self.config['RPC_URL'], session=session))
        return Web3(HTTPProvider(self.config['RPC_URL']))

    def register_domain_single_task(self, private_key: str, index: int, reg_index: int, proxy: str = None) -> None:
        MAX_RETRY = 5
        retry = 0
        if not self.validate_private_key(private_key):
            print(f"{Fore.RED+Style.BRIGHT}钱包 #{index+1} | 尝试 {reg_index} | 无效私钥，跳过注册。{Style.RESET_ALL}")
            with self.processed_lock:
                self.failed_count += 1
                self.current_tasks_processed += 1
            return
        w3 = self.create_web3_instance(proxy)
        try:
            account = Account.from_key(private_key)
            owner_address = account.address
            controller_address = w3.to_checksum_address(self.config['CONTROLLER_ADDRESS'])
            resolver_address = w3.to_checksum_address(self.config['RESOLVER'])
        except ValueError as e:
            print(f"{Fore.RED+Style.BRIGHT}钱包 #{index+1} | 尝试 {reg_index} | 配置中的合约或解析器地址无效: {e}.{Style.RESET_ALL}")
            with self.processed_lock:
                self.failed_count += 1
                self.current_tasks_processed += 1
            return
        domain_registered = False
        name = self.random_name()
        wallet_log_prefix = f"钱包 #{index+1} ({owner_address[:6]}...{owner_address[-4:]}) | 尝试 {reg_index} | {name}.phrs"
        try:
            balance_wei = w3.eth.get_balance(owner_address)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            print(f"{Fore.GREEN+Style.BRIGHT}[{datetime.now().astimezone(wib).strftime('%x %X %Z')}] 钱包 {wallet_log_prefix} | 当前余额: {balance_eth:.4f} ETH{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW+Style.BRIGHT}[{datetime.now().astimezone(wib).strftime('%x %X %Z')}] 钱包 {wallet_log_prefix} | 无法获取余额: {e}.{Style.RESET_ALL}")
        while retry < MAX_RETRY:
            try:
                controller = w3.eth.contract(address=controller_address, abi=self.CONTROLLER_ABI)
                secret = HexBytes(os.urandom(32))
                print(f"{Fore.CYAN+Style.BRIGHT}[{datetime.now().astimezone(wib).strftime('%x %X %Z')}] 开始为 {wallet_log_prefix} 注册...{Style.RESET_ALL}")
                print(f"{Fore.CYAN+Style.BRIGHT}[{datetime.now().astimezone(wib).strftime('%x %X %Z')}] 提交 {wallet_log_prefix} - 创建承诺...{Style.RESET_ALL}")
                commitment = controller.functions.makeCommitment(
                    name,
                    owner_address,
                    self.config['DURATION'],
                    secret,
                    resolver_address,
                    self.config['DATA'],
                    self.config['REVERSE_RECORD'],
                    self.config['OWNER_CONTROLLED_FUSES']
                ).call()
                print(f"{Fore.CYAN+Style.BRIGHT}[{datetime.now().astimezone(wib).strftime('%x %X %Z')}] 提交 {wallet_log_prefix} - 发送交易...{Style.RESET_ALL}")
                tx_commit = controller.functions.commit(commitment).build_transaction({
                    'from': owner_address,
                    'nonce': w3.eth.get_transaction_count(owner_address),
                    'gas': 200000,
                    'gasPrice': w3.eth.gas_price,
                    'chainId': self.config['CHAIN_ID']
                })
                signed_tx_commit = account.sign_transaction(tx_commit)
                try:
                    tx_hash_commit = w3.eth.send_raw_transaction(signed_tx_commit.raw_transaction)
                except AttributeError as e:
                    print(f"{Fore.RED+Style.BRIGHT}[CRITICAL] 无法访问 {wallet_log_prefix} 的 raw_transaction: {e}.{Style.RESET_ALL}")
                    raise
                except ValueError as e:
                    if "nonce" in str(e).lower() or "transaction already in pool" in str(e).lower():
                        print(f"{Fore.YELLOW+Style.BRIGHT}[{datetime.now().astimezone(wib).strftime('%x %X %Z')}] 非零错误或交易已在池中，尝试使用新nonce重试。{Style.RESET_ALL}")
                        tx_commit['nonce'] = w3.eth.get_transaction_count(owner_address)
                        signed_tx_commit = account.sign_transaction(tx_commit)
                        tx_hash_commit = w3.eth.send_raw_transaction(signed_tx_commit.raw_transaction)
                    else:
                        raise
                receipt_commit = w3.eth.wait_for_transaction_receipt(tx_hash_commit)
                if receipt_commit.status == 1:
                    print(f"{Fore.GREEN+Style.BRIGHT}[{datetime.now().astimezone(wib).strftime('%x %X %Z')}] 提交 {wallet_log_prefix} - 成功！TX Hash: {tx_hash_commit.hex()}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED+Style.BRIGHT}[{datetime.now().astimezone(wib).strftime('%x %X %Z')}] 提交 {wallet_log_prefix} - 失败。TX Hash: {tx_hash_commit.hex()}{Style.RESET_ALL}")
                    raise Exception("Commitment transaction failed.")
                print(f"{Fore.CYAN+Style.BRIGHT}[{datetime.now().astimezone(wib).strftime('%x %X %Z')}] 等待 60 秒以完成 {wallet_log_prefix}...{Style.RESET_ALL}")
                time.sleep(60)
                print(f"{Fore.CYAN+Style.BRIGHT}[{datetime.now().astimezone(wib).strftime('%x %X %Z')}] 注册 {wallet_log_prefix} - 计算租金价格...{Style.RESET_ALL}")
                price = controller.functions.rentPrice(name, self.config['DURATION']).call()
                value = price[0] + price[1]
                print(f"{Fore.CYAN+Style.BRIGHT}[{datetime.now().astimezone(wib).strftime('%x %X %Z')}] 注册 {wallet_log_prefix} - 租金价格: {w3.from_wei(value, 'ether')} ETH.{Style.RESET_ALL}")
                print(f"{Fore.CYAN+Style.BRIGHT}[{datetime.now().astimezone(wib).strftime('%x %X %Z')}] 注册 {wallet_log_prefix} - 发送交易...{Style.RESET_ALL}")
                tx_register = controller.functions.register(
                    name,
                    owner_address,
                    self.config['DURATION'],
                    secret,
                    resolver_address,
                    self.config['DATA'],
                    self.config['REVERSE_RECORD'],
                    self.config['OWNER_CONTROLLED_FUSES']
                ).build_transaction({
                    'from': owner_address,
                    'nonce': w3.eth.get_transaction_count(owner_address),
                    'gas': 300000,
                    'gasPrice': w3.eth.gas_price,
                    'value': value,
                    'chainId': self.config['CHAIN_ID']
                })
                signed_tx_register = account.sign_transaction(tx_register)
                try:
                    tx_hash_register = w3.eth.send_raw_transaction(signed_tx_register.raw_transaction)
                except AttributeError as e:
                    print(f"{Fore.RED+Style.BRIGHT}[CRITICAL] 无法访问 {wallet_log_prefix} 的 raw_transaction: {e}.{Style.RESET_ALL}")
                    raise
                except ValueError as e:
                    if "nonce" in str(e).lower() or "transaction already in pool" in str(e).lower():
                        print(f"{Fore.YELLOW+Style.BRIGHT}[{datetime.now().astimezone(wib).strftime('%x %X %Z')}] 非零错误或交易已在池中，尝试使用新nonce重试。{Style.RESET_ALL}")
                        tx_register['nonce'] = w3.eth.get_transaction_count(owner_address)
                        signed_tx_register = account.sign_transaction(tx_register)
                        tx_hash_register = w3.eth.send_raw_transaction(signed_tx_register.raw_transaction)
                    else:
                        raise
                receipt_register = w3.eth.wait_for_transaction_receipt(tx_hash_register)
                if receipt_register.status == 1:
                    print(f"{Fore.GREEN+Style.BRIGHT}[{datetime.now().astimezone(wib).strftime('%x %X %Z')}] 注册 {wallet_log_prefix} - 成功！域名 {name}.phrs 已注册！TX Hash: {tx_hash_register.hex()}{Style.RESET_ALL}")
                    domain_registered = True
                    break
                else:
                    print(f"{Fore.RED+Style.BRIGHT}[{datetime.now().astimezone(wib).strftime('%x %X %Z')}] 注册 {wallet_log_prefix} - 失败。TX Hash: {tx_hash_register.hex()}{Style.RESET_ALL}")
                    raise Exception("Registration transaction failed.")
            except Exception as err:
                retry += 1
                msg = str(err)[:150] + '...' if len(str(err)) > 150 else str(err)
                print(f"{Fore.YELLOW+Style.BRIGHT}[{datetime.now().astimezone(wib).strftime('%x %X %Z')}] 错误处理 {wallet_log_prefix}: {msg} - 重试 ({retry}/{MAX_RETRY}) 在 60 秒后...{Style.RESET_ALL}")
                time.sleep(60)
        with self.processed_lock:
            if domain_registered:
                self.success_count += 1
            else:
                self.failed_count += 1
            self.current_tasks_processed += 1
        self.print_progress()

    def print_progress(self):
        self.log(f"{Fore.GREEN+Style.BRIGHT}进度 | 总任务: {self.total_tasks} | 成功: {self.success_count} | 失败: {self.failed_count} | 已处理: {self.current_tasks_processed}/{self.total_tasks}{Style.RESET_ALL}")

    def run(self, reg_per_key=1, max_concurrency=5):
        self.config['REG_PER_KEY'] = reg_per_key
        self.config['MAX_CONCURRENCY'] = max_concurrency
        self.success_count = 0
        self.failed_count = 0
        self.current_tasks_processed = 0
        tasks_to_process = [(pk, idx, i + 1) for idx, pk in enumerate(self.accounts) for i in range(self.config['REG_PER_KEY'])]
        random.shuffle(tasks_to_process)
        self.total_tasks = len(tasks_to_process)
        print(f"{Fore.CYAN+Style.BRIGHT}开始域名注册，共 {len(self.accounts)} 个账户，总 {self.total_tasks} 次注册。{Style.RESET_ALL}")
        try:
            with ThreadPoolExecutor(max_workers=self.config['MAX_CONCURRENCY']) as executor:
                futures = []
                for pk, idx, reg_idx in tasks_to_process:
                    chosen_proxy = None
                    if self.proxies:
                        chosen_proxy = random.choice(self.proxies)
                    futures.append(executor.submit(self.register_domain_single_task, pk, idx, reg_idx, chosen_proxy))
                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        print(f"{Fore.RED+Style.BRIGHT}一个任务失败，可能需要重启。{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"{Fore.YELLOW+Style.BRIGHT}用户中断 (Ctrl+C)。优雅关闭...{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED+Style.BRIGHT}发生意外错误: {e}.{Style.RESET_ALL}")
        self.print_progress()
        print(f"{Fore.GREEN+Style.BRIGHT}所有域名注册任务已完成{Style.RESET_ALL}")

# 用法示例：
# dn = DomainName(accounts_file='accounts.txt', proxy_file='proxy.txt')
# dn.run(reg_per_key=1, max_concurrency=5)

if __name__ == "__main__":


    # 实例化，传入账户和代理文件
    dn = DomainName()
    # 启动注册流程，参数可自定义
    dn.run(reg_per_key=1, max_concurrency=5)