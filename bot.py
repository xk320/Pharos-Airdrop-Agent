from web3 import Web3
from eth_utils import to_hex
from eth_abi.abi import encode
from eth_account import Account
from eth_account.messages import encode_defunct
from aiohttp import ClientResponseError, ClientSession, ClientTimeout
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, random, secrets, json, time, os, pytz
from FaroSwap import Faroswap
from DomainName import DomainName

wib = pytz.timezone('Asia/Jakarta')

class PharosTestnet:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://testnet.pharosnetwork.xyz",
            "Referer": "https://testnet.pharosnetwork.xyz/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://api.pharosnetwork.xyz"
        self.RPC_URL = "https://testnet.dplabs-internal.com"
        self.WPHRS_CONTRACT_ADDRESS = "0x76aaaDA469D23216bE5f7C596fA25F282Ff9b364"
        self.USDC_CONTRACT_ADDRESS = "0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED"
        self.USDT_CONTRACT_ADDRESS = "0xD4071393f8716661958F766DF660033b3d35fD29"
        self.SWAP_ROUTER_ADDRESS = "0x1A4DE519154Ae51200b0Ad7c90F7faC75547888a"
        self.POTITION_MANAGER_ADDRESS = "0xF8a1D4FF0f9b9Af7CE58E1fc1833688F3BFd6115"
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
            {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]},
            {"type":"function","name":"deposit","stateMutability":"payable","inputs":[],"outputs":[]},
            {"type":"function","name":"withdraw","stateMutability":"nonpayable","inputs":[{"name":"wad","type":"uint256"}],"outputs":[]}
        ]''')
        self.SWAP_CONTRACT_ABI = [
            {
                "inputs": [
                    { "internalType": "uint256", "name": "collectionAndSelfcalls", "type": "uint256" },
                    { "internalType": "bytes[]", "name": "data", "type": "bytes[]" }
                ],
                "name": "multicall",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function",
            }
        ]
        self.ADD_LP_CONTRACT_ABI = [
            {
                "inputs": [
                    {
                        "components": [
                            { "internalType": "address", "name": "token0", "type": "address" },
                            { "internalType": "address", "name": "token1", "type": "address" },
                            { "internalType": "uint24", "name": "fee", "type": "uint24" },
                            { "internalType": "int24", "name": "tickLower", "type": "int24" },
                            { "internalType": "int24", "name": "tickUpper", "type": "int24" },
                            { "internalType": "uint256", "name": "amount0Desired", "type": "uint256" },
                            { "internalType": "uint256", "name": "amount1Desired", "type": "uint256" },
                            { "internalType": "uint256", "name": "amount0Min", "type": "uint256" },
                            { "internalType": "uint256", "name": "amount1Min", "type": "uint256" },
                            { "internalType": "address", "name": "recipient", "type": "address" },
                            { "internalType": "uint256", "name": "deadline", "type": "uint256" },
                        ],
                        "internalType": "struct INonfungiblePositionManager.MintParams",
                        "name": "params",
                        "type": "tuple",
                    },
                ],
                "name": "mint",
                "outputs": [
                    { "internalType": "uint256", "name": "tokenId", "type": "uint256" },
                    { "internalType": "uint128", "name": "liquidity", "type": "uint128" },
                    { "internalType": "uint256", "name": "amount0", "type": "uint256" },
                    { "internalType": "uint256", "name": "amount1", "type": "uint256" },
                ],
                "stateMutability": "payable",
                "type": "function",
            },
        ]
        # Ref Code
        self.ref_code = "PNFXEcz1CWezuu3g" # U can change it with yours.
        # Proxy
        self.proxies = []
        # Index
        self.proxy_index = 0
        # Account Proxies
        self.account_proxies = {}
        # Signatures
        self.signatures = {}
        # Access Tokens
        self.access_tokens = {}
        # Tx Count
        self.tx_count = 5
        self.tx_amount = round(random.uniform(0.001, 0.005), 6)
        # Wrap Option
        self.wrap_option = 1
        # Wrap Amount
        self.wrap_amount = self.tx_amount
        # Add LP Count
        self.add_lp_count = 1
        # Swap Count
        self.swap_count = 5
        # WPHRS Amount
        self.wphrs_amount = self.tx_amount
        # USDC Amount
        self.usdc_amount = self.tx_amount
        # USDT Amount
        self.usdt_amount = self.tx_amount
        # Min Delay
        self.min_delay = 1
        self.max_delay = 4

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Pharos Testnet{Fore.BLUE + Style.BRIGHT} Bot Airdrop
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:

            if not os.path.exists(filename):
                self.log(f"{Fore.RED + Style.BRIGHT}未找到文件 {filename}.{Style.RESET_ALL}")
                return
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}未找到任何代理。{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}总代理数: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}无法加载代理: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, token):
        if token not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[token] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[token]

    def rotate_proxy_for_account(self, token):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[token] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def generate_address(self, account: str):
        try:
            account = Account.from_key(account)
            address = account.address
            
            return address
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}状态 :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} 创建地址失败 {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}                  "
            )
            return None
        
    def generate_signature(self, account: str):
        try:
            encoded_message = encode_defunct(text="pharos")
            signed_message = Account.sign_message(encoded_message, private_key=account)
            signature = to_hex(signed_message.signature)

            return signature
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}状态 :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} 创建签名失败 {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}                  "
            )
            return None
        
    def generate_random_receiver(self):
        try:
            private_key_bytes = secrets.token_bytes(32)
            private_key_hex = to_hex(private_key_bytes)
            account = Account.from_key(private_key_hex)
            receiver = account.address
            
            return receiver
        except Exception as e:
            return None
        
    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account
        except Exception as e:
            return None
        
    def generate_swap_option(self):
        swap_option = random.choice([
            "WPHRStoUSDC", "WPHRStoUSDT", "USDCtoWPHRS",
            "USDTtoWPHRS", "USDCtoUSDT", "USDTtoUSDC"
        ])

        from_token = (
            self.USDC_CONTRACT_ADDRESS if swap_option in ["USDCtoWPHRS", "USDCtoUSDT"] else
            self.USDT_CONTRACT_ADDRESS if swap_option in ["USDTtoWPHRS", "USDTtoUSDC"] else
            self.WPHRS_CONTRACT_ADDRESS
        )

        to_token = (
            self.USDC_CONTRACT_ADDRESS if swap_option in ["WPHRStoUSDC", "USDTtoUSDC"] else
            self.USDT_CONTRACT_ADDRESS if swap_option in ["WPHRStoUSDT", "USDCtoUSDT"] else
            self.WPHRS_CONTRACT_ADDRESS
        )

        from_ticker = (
            "USDC" if swap_option in ["USDCtoWPHRS", "USDCtoUSDT"] else
            "USDT" if swap_option in ["USDTtoWPHRS", "USDTtoUSDC"] else
            "WPHRS"
        )

        to_ticker = (
            "USDC" if swap_option in ["WPHRStoUSDC", "USDTtoUSDC"] else
            "USDT" if swap_option in ["WPHRStoUSDT", "USDCtoUSDT"] else
            "WPHRS"
        )

        swap_amount = (
            self.usdc_amount if swap_option in ["USDCtoWPHRS", "USDCtoUSDT"] else
            self.usdt_amount if swap_option in ["USDTtoWPHRS", "USDTtoUSDC"] else
            self.wphrs_amount
        )

        return from_token, to_token, from_ticker, to_ticker, swap_amount
    
    def generate_add_lp_option(self):
        add_lp_option = random.choice(["USDCnWPHRS", "USDCnUSDT", "WPHRSnUSDT"])

        if add_lp_option == "USDCnWPHRS":
            token0 = self.USDC_CONTRACT_ADDRESS
            token1 = self.WPHRS_CONTRACT_ADDRESS
            amount0 = 0.45
            amount1 = 0.001
            ticker0 = "USDC"
            ticker1 = "WPHRS"
        elif add_lp_option == "USDCnUSDT":
            token0 = self.USDC_CONTRACT_ADDRESS
            token1 = self.USDT_CONTRACT_ADDRESS
            amount0 = 1
            amount1 = 1
            ticker0 = "USDC"
            ticker1 = "USDT"
        else:
            token0 = self.WPHRS_CONTRACT_ADDRESS
            token1 = self.USDT_CONTRACT_ADDRESS
            amount0 = 0.001
            amount1 = 0.45
            ticker0 = "WPHRS"
            ticker1 = "USDT"

        return add_lp_option, token0, token1, amount0, amount1, ticker0, ticker1
        
    async def get_web3_with_check(self, address: str, use_proxy: bool, retries=3, timeout=60):
        request_kwargs = {"timeout": timeout}

        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        if use_proxy and proxy:
            request_kwargs["proxies"] = {"http": proxy, "https": proxy}

        for attempt in range(retries):
            try:
                web3 = Web3(Web3.HTTPProvider(self.RPC_URL, request_kwargs=request_kwargs))
                web3.eth.get_block_number()
                return web3
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                    continue
                raise Exception(f"无法连接到RPC: {str(e)}")
        
    async def get_token_balance(self, address: str, contract_address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            if contract_address == "PHRS":
                balance = web3.eth.get_balance(address)
                decimals = 18
            else:
                token_contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=self.ERC20_CONTRACT_ABI)
                balance = token_contract.functions.balanceOf(address).call()
                decimals = token_contract.functions.decimals().call()

            token_balance = balance / (10 ** decimals)

            return token_balance
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     消息 :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
        
    async def perform_transfer(self, account: str, address: str, receiver: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            
            amount_to_wei = web3.to_wei(self.tx_amount, "ether")
            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            tx = {
                "to": receiver,
                "value": amount_to_wei,
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "gas": 21000,
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "chainId": web3.eth.chain_id
            }

            signed_tx = web3.eth.account.sign_transaction(tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            block_number = receipt.blockNumber

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     消息 :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def perform_wrapped(self, account: str, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.WPHRS_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)

            amount_to_wei = web3.to_wei(self.wrap_amount, "ether")
            wrap_data = token_contract.functions.deposit()
            estimated_gas = wrap_data.estimate_gas({"from": address, "value": amount_to_wei})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            wrap_tx = wrap_data.build_transaction({
                "from": address,
                "value": amount_to_wei,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(wrap_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            block_number = receipt.blockNumber

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     消息 :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def perform_unwrapped(self, account: str, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.WPHRS_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)

            amount_to_wei = web3.to_wei(self.wrap_amount, "ether")
            unwrap_data = token_contract.functions.withdraw(amount_to_wei)
            estimated_gas = unwrap_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            unwrap_tx = unwrap_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(unwrap_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            block_number = receipt.blockNumber

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     消息 :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def approving_token(self, account: str, address: str, spender_address: str, contract_address: str, amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            
            spender = web3.to_checksum_address(spender_address)
            token_contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=self.ERC20_CONTRACT_ABI)
            decimals = token_contract.functions.decimals().call()

            amount_to_wei = int(amount * (10 ** decimals))

            allowance = token_contract.functions.allowance(address, spender).call()
            if allowance < amount_to_wei:
                approve_data = token_contract.functions.approve(spender, 2**256 - 1)
                estimated_gas = approve_data.estimate_gas({"from": address})

                max_priority_fee = web3.to_wei(1, "gwei")
                max_fee = max_priority_fee

                approve_tx = approve_data.build_transaction({
                    "from": address,
                    "gas": int(estimated_gas * 1.2),
                    "maxFeePerGas": int(max_fee),
                    "maxPriorityFeePerGas": int(max_priority_fee),
                    "nonce": web3.eth.get_transaction_count(address, "pending"),
                    "chainId": web3.eth.chain_id,
                })

                signed_tx = web3.eth.account.sign_transaction(approve_tx, account)
                raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_hash = web3.to_hex(raw_tx)
                receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
                block_number = receipt.blockNumber
                
                explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
                
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     审批 :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} 成功 {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     区块   :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     交易哈希 :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     区块浏览器:{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
                )
                await asyncio.sleep(5)
            
            return True
        except Exception as e:
            raise Exception(f"批准合约token失败: {str(e)}")

    async def perform_add_liquidity(self, account: str, address: str, add_lp_option: str, token0: str, token1: str, amount0: float, amount1: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            if add_lp_option == "USDCnWPHRS":
                await self.approving_token(account, address, self.POTITION_MANAGER_ADDRESS, token0, amount0, use_proxy)
            if add_lp_option == "WPHRSnUSDT":
                await self.approving_token(account, address, self.POTITION_MANAGER_ADDRESS, token1, amount1, use_proxy)
            else:
                await self.approving_token(account, address, self.POTITION_MANAGER_ADDRESS, token0, amount0, use_proxy)
                await self.approving_token(account, address, self.POTITION_MANAGER_ADDRESS, token1, amount1, use_proxy)
            
            token0_contract = web3.eth.contract(address=web3.to_checksum_address(token0), abi=self.ERC20_CONTRACT_ABI)
            token0_decimals = token0_contract.functions.decimals().call()
            amount0_desired = int(amount0 * (10 ** token0_decimals))

            token1_contract = web3.eth.contract(address=web3.to_checksum_address(token1), abi=self.ERC20_CONTRACT_ABI)
            token1_decimals = token1_contract.functions.decimals().call()
            amount1_desired = int(amount1 * (10 ** token1_decimals))

            mint_params = {
                "token0": web3.to_checksum_address(token0),
                "token1": web3.to_checksum_address(token1),
                "fee": 500,
                "tickLower": -887270,
                "tickUpper": 887270,
                "amount0Desired": amount0_desired,
                "amount1Desired": amount1_desired,
                "amount0Min": 0,
                "amount1Min": 0,
                "recipient": web3.to_checksum_address(address),
                "deadline": int(time.time()) + 600
            }

            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.POTITION_MANAGER_ADDRESS), abi=self.ADD_LP_CONTRACT_ABI)

            lp_data = token_contract.functions.mint(mint_params)

            estimated_gas = lp_data.estimate_gas({"from": address})
            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            lp_tx = lp_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(lp_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            block_number = receipt.blockNumber

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     消息 :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def generate_multicall_data(self, address: str, from_token: str, to_token: str, swap_amount: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            token_contract = web3.eth.contract(address=web3.to_checksum_address(from_token), abi=self.ERC20_CONTRACT_ABI)
            decimals = token_contract.functions.decimals().call()
            amount_to_wei = int(swap_amount * (10 ** decimals))
            
            encoded_data = encode(
                ["address", "address", "uint256", "address", "uint256", "uint256", "uint256"],
                [
                    web3.to_checksum_address(from_token),
                    web3.to_checksum_address(to_token),
                    500,
                    web3.to_checksum_address(address),
                    amount_to_wei,
                    0,
                    0
                ]
            )

            multicall_data = [b'\x04\xe4\x5a\xaf' + encoded_data]

            return multicall_data
        except Exception as e:
            raise Exception(f"无法生成multicall数据: {str(e)}")
        
    async def perform_swap(self, account: str, address: str, from_token: str, to_token: str, swap_amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            await self.approving_token(account, address, self.SWAP_ROUTER_ADDRESS, from_token, swap_amount, use_proxy)

            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.SWAP_ROUTER_ADDRESS), abi=self.SWAP_CONTRACT_ABI)

            deadline = int(time.time()) + 300

            multicall_data = await self.generate_multicall_data(address, from_token, to_token, swap_amount, use_proxy)

            swap_data = token_contract.functions.multicall(deadline, multicall_data)

            estimated_gas = swap_data.estimate_gas({"from": address})
            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            swap_tx = swap_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(swap_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            block_number = receipt.blockNumber

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     消息 :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
    
    async def print_timer(self):
        for remaining in range(random.randint(self.min_delay, self.max_delay), 0, -1):
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}等待{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {remaining} {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}秒后进行下一笔交易...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)
    
    async def user_login(self, address: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/user/login?address={address}&signature={self.signatures[address]}&wallet=OKX+Wallet&invite_code={self.ref_code}"
        headers = {
            **self.headers,
            "Authorization": "Bearer null",
            "Content-Length": "0"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}消息   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def user_profile(self, address: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/user/profile?address={address}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        if "code" in result and result["code"] != 0:
                            await asyncio.sleep(3)
                            continue
                        return result
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                    continue

        return None
    
    async def sign_in(self, address: str, proxy=None, retries=10):
        url = f"{self.BASE_API}/sign/in?address={address}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": "0"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        if "code" in result and result["code"] not in [0, 1]:
                            await asyncio.sleep(3)
                            continue
                        return result
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                    continue

            return None
    
    async def faucet_status(self, address: str, proxy=None, retries=10):
        url = f"{self.BASE_API}/faucet/status?address={address}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        if "code" in result and result["code"] != 0:
                            await asyncio.sleep(3)
                            continue
                        return result
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                    continue

            return None
            
    async def claim_faucet(self, address: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/faucet/daily?address={address}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": "0"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        if "code" in result and result["code"] not in [0, 1]:
                            await asyncio.sleep(3)
                            continue
                        return result
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                    continue

            return None
            
    async def verify_task(self, address: str, tx_hash: str, proxy=None, retries=30):
        url = f"{self.BASE_API}/task/verify?address={address}&task_id=103&tx_hash={tx_hash}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": "0"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        if "code" in result and result["code"] != 0:
                            await asyncio.sleep(3)
                            continue
                        return result
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     消息 :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

            return None
            
    async def process_user_login(self, address: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}代理     :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            login = await self.user_login(address, proxy)
            if login and login.get("code") == 0:
                self.access_tokens[address] = login["data"]["jwt"]

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}状态 :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} 登录成功 {Style.RESET_ALL}"
                )
                return True

            # if rotate_proxy:
            #     self.log(
            #         f"{Fore.CYAN+Style.BRIGHT}状态 :{Style.RESET_ALL}"
            #         f"{Fore.RED+Style.BRIGHT} 登录失败, {Style.RESET_ALL}"
            #         f"{Fore.YELLOW+Style.BRIGHT} 正在轮换代理... {Style.RESET_ALL}"
            #     )
            #     proxy = self.rotate_proxy_for_account(address)
            #     await asyncio.sleep(3)  
            #     continue

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}状态 :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} 登录失败 {Style.RESET_ALL}"
            )
            return False
    
    async def process_perform_transfer(self, account: str, address: str, receiver: str, use_proxy: bool):
        tx_hash, block_number = await self.perform_transfer(account, address, receiver, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     状态  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} 交易成功 {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     区块   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     交易哈希 :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     区块浏览器:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )

            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT}等待验证任务...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(3)

            # proxy = self.get_next_proxy_for_account(address) if use_proxy else None

            # verify = await self.verify_task(address, tx_hash, proxy)
            # if verify and verify.get("code") == 0:
            #     self.log(
            #         f"{Fore.CYAN+Style.BRIGHT}     验证  :{Style.RESET_ALL}"
            #         f"{Fore.GREEN+Style.BRIGHT} 成功 {Style.RESET_ALL}                   "
            #     )
            # else:
            #     self.log(
            #         f"{Fore.CYAN+Style.BRIGHT}     验证  :{Style.RESET_ALL}"
            #         f"{Fore.RED+Style.BRIGHT} 失败 {Style.RESET_ALL}                   "
            #     )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     状态  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} 交易失败 {Style.RESET_ALL}"
            )

    async def process_perform_wrapped(self, account: str, address: str, use_proxy: bool):
        tx_hash, block_number = await self.perform_wrapped(account, address, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     状态  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} 包装 {self.wrap_amount} PHRS 为 WPHRS 成功 {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     区块   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     交易哈希 :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     区块浏览器:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     状态  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} 交易失败 {Style.RESET_ALL}"
            )

    async def process_perform_unwrapped(self, account: str, address: str, use_proxy: bool):
        tx_hash, block_number = await self.perform_unwrapped(account, address, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     状态  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} 解包 {self.wrap_amount} WPHRS 为 PHRS 成功 {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     区块   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     交易哈希 :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     区块浏览器:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     状态  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} 交易失败 {Style.RESET_ALL}"
            )

    async def process_perform_add_liquidity(self, account: str, address: str, add_lp_option: str, token0: str, token1: str, amount0: float, amount1: float, ticker0: str, ticker1: str, use_proxy: bool):
        tx_hash, block_number = await self.perform_add_liquidity(account, address, add_lp_option, token0, token1, amount0, amount1, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     状态  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} 添加 LP 给 {amount0} {ticker0} / {amount1} {ticker1} 成功 {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     区块   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     交易哈希 :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     区块浏览器:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     状态  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} 交易失败 {Style.RESET_ALL}"
            )

    async def process_perform_swap(self, account: str, address: str, from_token: str, to_token: str, from_ticker: str, to_ticker: str, swap_amount: float, use_proxy: bool):
        tx_hash, block_number = await self.perform_swap(account, address, from_token, to_token, swap_amount, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     状态  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} 兑换 {swap_amount} {from_ticker} 为 {to_ticker} 成功 {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     区块   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     交易哈希 :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     区块浏览器:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     状态  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} 交易失败 {Style.RESET_ALL}"
            )

    async def process_option_1(self, address: str, use_proxy: bool):
        # 签到
        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        profile = await self.user_profile(address, proxy)
        if profile and profile.get("msg") == "ok":
            points = profile.get("data", {}).get("user_info", {}).get("TotalPoints", 0)

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}余额   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {points} PTS {Style.RESET_ALL}"
            )

        sign_in = await self.sign_in(address, proxy)
        if sign_in and sign_in.get("msg") == "ok":
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}签到  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} 成功 {Style.RESET_ALL}"
            )
        elif sign_in and sign_in.get("msg") == "already signed in today":
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}签到  :{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} 已经领取过了 {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}签到  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} 未领取 {Style.RESET_ALL}"
            )

        faucet_status = await self.faucet_status(address, proxy)
        if faucet_status and faucet_status.get("msg") == "ok":
            is_able = faucet_status.get("data", {}).get("is_able_to_faucet", False)

            if is_able:
                claim = await self.claim_faucet(address, proxy)
                if claim and claim.get("msg") == "ok":
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Faucet    :{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} 0.2 PHRS {Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT}领取成功{Style.RESET_ALL}"
                    )
                elif claim and claim.get("msg") == "user has not bound X account":
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Faucet    :{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} 不符合领取条件 {Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} 需要绑定X账户 {Style.RESET_ALL}"
                    )
                else:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Faucet    :{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} 未领取 {Style.RESET_ALL}"
                    )
            else:
                faucet_available_ts = faucet_status.get("data", {}).get("avaliable_timestamp", None)
                faucet_available_wib = datetime.fromtimestamp(faucet_available_ts).astimezone(wib).strftime('%x %X %Z')
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Faucet    :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} 已经领取过了 {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT} 可以领取的时间: {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{faucet_available_wib}{Style.RESET_ALL}"
                )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Faucet    :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} 获取状态信息失败 {Style.RESET_ALL}"
            )

    async def process_option_2(self, account: str, address: str, use_proxy: bool):
        self.log(f"{Fore.CYAN+Style.BRIGHT}转账  :{Style.RESET_ALL}                       ")
        await asyncio.sleep(3)  

        for i in range(self.tx_count):
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}交易 - {i+1}{Style.RESET_ALL}                       "
            )

            receiver = self.generate_random_receiver()

            balance = await self.get_token_balance(address, "PHRS", use_proxy)
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     余额 :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance} PHRS {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     数量  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.tx_amount} PHRS {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     接收人:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {receiver} {Style.RESET_ALL}"
            )

            if not balance or balance <= self.tx_amount:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     状态  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} PHRS代币余额不足 {Style.RESET_ALL}"
                )
                break

            await self.process_perform_transfer(account, address, receiver, use_proxy)
            await self.print_timer()

    async def process_option_3(self, account: str, address: str, use_proxy):
        if self.wrap_option == 1:
            self.log(f"{Fore.CYAN+Style.BRIGHT}包装   :{Style.RESET_ALL}                      ")

            balance = await self.get_token_balance(address, "PHRS", use_proxy)
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     余额 :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance} PHRS {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     数量  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.wrap_amount} PHRS {Style.RESET_ALL}"
            )

            if not balance or balance <=  self.wrap_amount:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     状态  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} PHRS代币余额不足 {Style.RESET_ALL}"
                )
                return
            
            await self.process_perform_wrapped(account, address, use_proxy)
        
        elif self.wrap_option == 2:
            self.log(f"{Fore.CYAN+Style.BRIGHT}解包 :{Style.RESET_ALL}                      ")

            balance = await self.get_token_balance(address, self.WPHRS_CONTRACT_ADDRESS, use_proxy)
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     余额 :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance} WPHRS {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     数量  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.wrap_amount} WPHRS {Style.RESET_ALL}"
            )

            if not balance or balance <=  self.wrap_amount:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     状态  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} WPHRS代币余额不足 {Style.RESET_ALL}"
                )
                return
            
            await self.process_perform_unwrapped(account, address, use_proxy)

    async def process_option_4(self, account: str, address: str, use_proxy: bool):
        self.log(f"{Fore.CYAN+Style.BRIGHT}添加流动性 :{Style.RESET_ALL}                       ")

        for i in range(self.add_lp_count):
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}添加流动性{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {i+1} / {self.add_lp_count} {Style.RESET_ALL}                           "
            )

            add_lp_option, token0, token1, amount0, amount1, ticker0, ticker1 = self.generate_add_lp_option()

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     类型    :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} {ticker0} / {ticker1} {Style.RESET_ALL}                "
            )

            token0_balance = await self.get_token_balance(address, token0, use_proxy)
            token1_balance = await self.get_token_balance(address, token1, use_proxy)

            self.log(f"{Fore.CYAN+Style.BRIGHT}     余额 :{Style.RESET_ALL}")
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}        > {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{token0_balance} {ticker0}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}        > {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{token1_balance} {ticker1}{Style.RESET_ALL}"
            )

            self.log(f"{Fore.CYAN+Style.BRIGHT}     数量  :{Style.RESET_ALL}")
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}        > {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{amount0} {ticker0}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}        > {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{amount1} {ticker1}{Style.RESET_ALL}"
            )

            if not token0_balance or token0_balance <= amount0:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     状态  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {ticker0}余额不足 {Style.RESET_ALL}"
                )
                break
            if not token1_balance or token1_balance <= amount1:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     状态  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {ticker1}余额不足 {Style.RESET_ALL}"
                )
                break

            await self.process_perform_add_liquidity(account, address, add_lp_option, token0, token1, amount0, amount1, ticker0, ticker1, use_proxy)
            await self.print_timer()

    async def process_option_5(self, account: str, address: str, use_proxy: bool):
        self.log(f"{Fore.CYAN+Style.BRIGHT}兑换      :{Style.RESET_ALL}                       ")

        for i in range(self.swap_count):
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}兑换{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {i+1} / {self.swap_count} {Style.RESET_ALL}                           "
            )

            from_token, to_token, from_ticker, to_ticker, swap_amount = self.generate_swap_option()

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     类型    :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} {from_ticker} {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} {to_ticker} {Style.RESET_ALL}"
            )

            balance = await self.get_token_balance(address, from_token, use_proxy)
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     余额 :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance} {from_ticker} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     数量  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {swap_amount} {from_ticker} {Style.RESET_ALL}"
            )

            if not balance or balance <= swap_amount:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     状态  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {from_ticker}余额不足 {Style.RESET_ALL}"
                )
                continue

            await self.process_perform_swap(account, address, from_token, to_token, from_ticker, to_ticker, swap_amount, use_proxy)
            await self.print_timer()

    async def process_option_6(self):
        faroswap = Faroswap()
        await faroswap.main()
    
    async def process_option_7(self):
        dn = DomainName()
        # 启动注册流程，参数可自定义
        dn.run(reg_per_key=1, max_concurrency=5)

    async def process_accounts(self, account: str, address: str, option: int, use_proxy: bool, rotate_proxy: bool):
        logined = await self.process_user_login(address, use_proxy, rotate_proxy)
        if logined:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}选项    :{Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT} 运行所有功能 {Style.RESET_ALL}"
            )

            await self.process_option_1(address, use_proxy)
            await asyncio.sleep(1)

            await self.process_option_2(account, address, use_proxy)
            await asyncio.sleep(1)

            await self.process_option_3(account, address, use_proxy)
            await asyncio.sleep(1)
            
            await self.process_option_4(account, address, use_proxy)
            await asyncio.sleep(1)

            await self.process_option_5(account, address, use_proxy)
            await asyncio.sleep(1)

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            
            option = 6
            use_proxy_choice = 2
            rotate_proxy = "n"

            while True:
                use_proxy = True

                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}总账户数: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies(use_proxy_choice)
                
                separator = "=" * 25
                for account in accounts:
                    if account:
                        address = self.generate_address(account)
                        signature = self.generate_signature(account)

                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if not address or not signature:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}状态    :{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Private Key无效或版本不支持 {Style.RESET_ALL}"
                            )
                            continue

                        self.signatures[address] = signature

                        await self.process_accounts(account, address, option, use_proxy, rotate_proxy)
                        await asyncio.sleep(3)

                await self.process_option_6()
                await asyncio.sleep(1)
                await self.process_option_7()
                await asyncio.sleep(1)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*72)
                # 

                seconds = 24 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ 等待{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}所有账户已处理完毕.{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}未找到文件 'accounts.txt'.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}错误: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = PharosTestnet()
        asyncio.run(bot.main())

    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ 退出 ] Pharos Testnet - BOT{Style.RESET_ALL}"                              
        )