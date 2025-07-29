from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, BasicAuth
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, random, json, time, re, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Faroswap:
    def __init__(self) -> None:
        self.HEADERS = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://faroswap.xyz",
            "Referer": "https://faroswap.xyz/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": FakeUserAgent().random
        }
        self.RPC_URL = "https://api.zan.top/node/v1/pharos/testnet/54b49326c9f44b6e8730dc5dd4348421"
        self.PHRS_CONTRACT_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
        self.WPHRS_CONTRACT_ADDRESS = "0x3019B247381c850ab53Dc0EE53bCe7A07Ea9155f"
        self.USDC_CONTRACT_ADDRESS = "0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED"
        self.USDT_CONTRACT_ADDRESS = "0xD4071393f8716661958F766DF660033b3d35fD29"
        self.WETH_CONTRACT_ADDRESS = "0x4E28826d32F1C398DED160DC16Ac6873357d048f"
        self.WBTC_CONTRACT_ADDRESS = "0x8275c526d1bCEc59a31d673929d3cE8d108fF5c7"
        self.MIXSWAP_ROUTER_ADDRESS = "0x3541423f25A1Ca5C98fdBCf478405d3f0aaD1164"
        self.DVM_ROUTER_ADDRESS = "0x4b177AdEd3b8bD1D5D747F91B9E853513838Cd49"
        self.POOL_ROUTER_ADDRESS = "0x73cafc894dbfc181398264934f7be4e482fc9d40"
        self.TICKERS = [
            "PHRS", 
            "WPHRS", 
            "USDC", 
            "USDT", 
            "WETH",
            "WBTC"
        ]
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
            {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]},
            {"type":"function","name":"deposit","stateMutability":"payable","inputs":[],"outputs":[]},
            {"type":"function","name":"withdraw","stateMutability":"nonpayable","inputs":[{"name":"wad","type":"uint256"}],"outputs":[]}
        ]''')
        self.UNISWAP_V2_CONTRACT_ABI = [
            {
                "type": "function",
                "name": "addDVMLiquidity",
                "stateMutability": "payable",
                "inputs": [
                    { "internalType": "address", "name": "dvmAddress", "type": "address" },
                    { "internalType": "uint256", "name": "baseInAmount", "type": "uint256" },
                    { "internalType": "uint256", "name": "quoteInAmount", "type": "uint256" },
                    { "internalType": "uint256", "name": "baseMinAmount", "type": "uint256" },
                    { "internalType": "uint256", "name": "quoteMinAmount", "type": "uint256" },
                    { "internalType": "uint8", "name": "flag", "type": "uint8" },
                    { "internalType": "uint256", "name": "deadLine", "type": "uint256" }
                ],
                "outputs": [
                    { "internalType": "uint256", "name": "shares", "type": "uint256" },
                    { "internalType": "uint256", "name": "baseAdjustedInAmount", "type": "uint256" },
                    { "internalType": "uint256", "name": "quoteAdjustedInAmount", "type": "uint256" }
                ]
            }
        ]
        amount = float(random.uniform(0.001, 0.009))
        amount = round(amount, 4)
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.used_nonce = {}
        self.dp_or_wd_option = None
        self.swap_count = 15
        self.phrs_swap_amount = amount
        self.wphrs_swap_amount = amount
        self.usdc_swap_amount = amount
        self.usdt_swap_amount = amount
        self.weth_swap_amount = amount
        self.wbtc_swap_amount = amount
        self.add_lp_count = 30
        self.phrs_add_lp_amount = amount/2
        self.wphrs_add_lp_amount = amount/2
        self.usdc_add_lp_amount = amount/2
        self.usdt_add_lp_amount = amount/2
        self.weth_add_lp_amount = amount/2
        self.wbtc_add_lp_amount = amount/2
        self.min_delay = 3
        self.max_delay = 5

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )


    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_pools(self):
        filename = "pools.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
    
    async def load_proxies(self, use_proxy_choice: bool):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/refs/heads/main/proxies/http.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}FaroSwap 生态交互: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
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
    
    def build_proxy_config(self, proxy=None):
        if not proxy:
            return None, None, None

        if proxy.startswith("socks"):
            connector = ProxyConnector.from_url(proxy)
            return connector, None, None

        elif proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", proxy)
            if match:
                username, password, host_port = match.groups()
                clean_url = f"http://{host_port}"
                auth = BasicAuth(username, password)
                return None, clean_url, auth
            else:
                return None, proxy, None

        raise Exception("Unsupported Proxy Type.")
    
    def generate_address(self, account: str):
        try:
            account = Account.from_key(account)
            address = account.address
            
            return address
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Generate Address Failed {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}                  "
            )
            return None
        
    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account
        except Exception as e:
            return None

    # 这段代码定义了一个名为 generate_swap_option 的方法，其中 valid_pairs 是一个列表推导式，目的是生成所有可用的代币兑换对（from_t, to_t）。
    # 具体逻辑如下：
    # - 遍历 self.TICKERS 中的所有代币，from_t 作为兑换的源代币，to_t 作为目标代币。
    # - 只有当 from_t 和 to_t 不相同时才会被选中（即不能自己兑换自己）。
    # - 并且排除了 PHRS 和 WPHRS 之间的直接兑换（无论是 PHRS->WPHRS 还是 WPHRS->PHRS 都不允许）。
    # 这样做的目的是为了生成一组有效的、可用的兑换对，供后续随机选择使用。
    def generate_swap_option(self,f,t):
        valid_pairs = [
            (from_t, to_t) for from_t in self.TICKERS for to_t in self.TICKERS
            if from_t != to_t and  (
                (from_t == f and to_t == t) 
            )
        ]
        # print(valid_pairs)
        from_ticker, to_ticker = random.choice(valid_pairs)

        def get_contract(ticker):
            if ticker == "PHRS":
                return self.PHRS_CONTRACT_ADDRESS
            return getattr(self, f"{ticker}_CONTRACT_ADDRESS")

        def get_amount(ticker):
            return getattr(self, f"{ticker.lower()}_swap_amount")

        from_token = get_contract(from_ticker)
        to_token = get_contract(to_ticker)
        amount = get_amount(from_ticker)

        swap_option = f"{from_ticker} to {to_ticker}"

        return  {
            "swap_option": swap_option,
            "from_token": from_token,
            "to_token": to_token,
            "ticker": from_ticker,
            "amount": amount
        }
    
    def generate_lp_option(self):
        tickers = ["USDC", "USDT"]

        valid_pairs = [
            (base_t, quote_t)
            for base_t in tickers
            for quote_t in tickers
            if base_t != quote_t
        ]

        base_ticker, quote_ticker = random.choice(valid_pairs)

        def get_contract(ticker):
            return getattr(self, f"{ticker}_CONTRACT_ADDRESS")

        def get_amount(ticker):
            return getattr(self, f"{ticker.lower()}_add_lp_amount")

        base_token = get_contract(base_ticker)
        quote_token = get_contract(quote_ticker)
        amount = get_amount(base_ticker)

        lp_option = f"{base_ticker} to {quote_ticker}"

        return {
            "lp_option": lp_option,
            "base_token": base_token,
            "quote_token": quote_token,
            "base_ticker": base_ticker,
            "quote_ticker": quote_ticker,
            "amount": amount
        }
        
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
                if attempt < retries:
                    await asyncio.sleep(3)
                    continue
                raise Exception(f"Failed to Connect to RPC: {str(e)}")
        
    async def get_token_balance(self, address: str, contract_address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            if contract_address == self.PHRS_CONTRACT_ADDRESS:
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
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
        
    async def send_raw_transaction_with_retries(self, account, web3, tx, retries=5):
        for attempt in range(retries):
            try:
                signed_tx = web3.eth.account.sign_transaction(tx, account)
                raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_hash = web3.to_hex(raw_tx)
                return tx_hash
            except TransactionNotFound:
                pass
            except Exception as e:
                pass
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Hash Not Found After Maximum Retries")

    async def wait_for_receipt_with_retries(self, web3, tx_hash, retries=5):
        for attempt in range(retries):
            try:
                receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
                return receipt
            except TransactionNotFound:
                pass
            except Exception as e:
                pass
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Receipt Not Found After Maximum Retries")
        
    
    
    async def approving_token(self, account: str, address: str, router_address: str, asset_address: str, amount_to_wei: int, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            
            spender = web3.to_checksum_address(router_address)
            token_contract = web3.eth.contract(address=web3.to_checksum_address(asset_address), abi=self.ERC20_CONTRACT_ABI)

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
                    "nonce": self.used_nonce[address],
                    "chainId": web3.eth.chain_id,
                })

                tx_hash = await self.send_raw_transaction_with_retries(account, web3, approve_tx)
                receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

                block_number = receipt.blockNumber
                self.used_nonce[address] += 1

                explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
                
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Approve :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
                )
                await self.print_timer()

            return True
        except Exception as e:
            raise Exception(f"Approving Token Contract Failed: {str(e)}")

    async def perform_swap(self, account: str, address: str, from_token: str, to_token: str, amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            
            if from_token != self.PHRS_CONTRACT_ADDRESS:
                decimals = web3.eth.contract(
                    address=web3.to_checksum_address(from_token), 
                    abi=self.ERC20_CONTRACT_ABI
                ).functions.decimals().call()
                await self.approving_token(account, address, self.MIXSWAP_ROUTER_ADDRESS, from_token, int(amount * (10 ** decimals)), use_proxy)
            else:
                decimals = 18

            amount_to_wei = int(amount * (10 ** decimals))

            dodo_route = await self.get_dodo_route(address, from_token, to_token, amount_to_wei, use_proxy)
            if not dodo_route:
                return None, None

            value = dodo_route.get("data", {}).get("value")
            calldata = dodo_route.get("data", {}).get("data")
            gas_limit = dodo_route.get("data", {}).get("gasLimit", 300000)

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            swap_tx = {
                "to": self.MIXSWAP_ROUTER_ADDRESS,
                "from": address,
                "data": calldata,
                "value": int(value),
                "gas": int(gas_limit),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            }

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, swap_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            block_number = receipt.blockNumber
            self.used_nonce[address] += 1

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def perform_add_dvm_liquidity(self, account: str, address: str, pair_address: str, base_token: str, quote_token: str, amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            dvm_address = web3.to_checksum_address(pair_address)
            in_amount = int(amount * (10 ** 6))
            min_amount = int(in_amount * (1 - 0.1 / 100))
            deadline = int(time.time()) + 600

            await self.approving_token(account, address, self.POOL_ROUTER_ADDRESS, base_token, in_amount, use_proxy)
            await self.approving_token(account, address, self.POOL_ROUTER_ADDRESS, quote_token, in_amount, use_proxy)

            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.DVM_ROUTER_ADDRESS), abi=self.UNISWAP_V2_CONTRACT_ABI)

            add_lp_data = token_contract.functions.addDVMLiquidity(
                dvm_address, in_amount, in_amount, min_amount, min_amount, 0, deadline
            )

            estimated_gas = add_lp_data.estimate_gas({"from": address, "value": 0})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            add_lp_tx = add_lp_data.build_transaction({
                "from": address,
                "value": 0,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, add_lp_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            block_number = receipt.blockNumber
            self.used_nonce[address] += 1

            return tx_hash, block_number

        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def print_timer(self):
        for remaining in range(random.randint(self.min_delay, self.max_delay), 0, -1):
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {remaining} {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Seconds For Next Tx...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)
        
    def print_question(self):

        while True:
            try:
                # print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Free Proxyscrape Proxy{Style.RESET_ALL}")
                # print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                # print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                # choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())
                choose = 2
                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Free Proxyscrape" if choose == 1 else 
                        "With Private" if choose == 2 else 
                        "Without"
                    )
                    # print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                # rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()
                rotate = "n"

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return choose, rotate
    
    async def check_connection(self, proxy_url=None):
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            return True
        except (Exception, ClientResponseError) as e:
            self.log(
                f"{Fore.CYAN + Style.BRIGHT}Status       :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Connection Not 200 OK {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
    
    async def get_dodo_route(self, address: str, from_token: str, to_token: str, amount: int, use_proxy: bool, retries=5):
        for attempt in range(retries):
            deadline = int(time.time()) + 600
            url = (
                f"https://api.dodoex.io/route-service/v2/widget/getdodoroute?chainId=688688&deadLine={deadline}"
                f"&apikey=a37546505892e1a952&slippage=3.225&source=dodoV2AndMixWasm&toTokenAddress={to_token}"
                f"&fromTokenAddress={from_token}&userAddr={address}&estimateGas=true&fromAmount={amount}"
            )
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                    async with session.get(url=url, headers=self.HEADERS, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        result = await response.json()
                        if result.get("status") != 200:
                            err_msg = result.get("data", "Quote Not Available")
                            raise ValueError(err_msg)

                        return result
            except (Exception, ClientResponseError) as e:
                if attempt < retries:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Fetch Dodo Route Failed: {str(e)} {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}({attempt+1}/{retries}){Style.RESET_ALL}"
                    )
                    await asyncio.sleep(3)
                    continue

                return None
            
    async def process_check_connection(self, address: int, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy        :{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy)
            if not is_valid:
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(address)
                    continue

                return False
            
            return True

    
    async def process_perform_swap(self, account: str, address: str, from_token: str, to_token: str, amount: float, use_proxy: bool):
        tx_hash, block_number = await self.perform_swap(account, address, from_token, to_token, amount, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Swap Success {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )

    async def process_perform_add_dvm_liquidity(self, account: str, address: str, pair_address: str, base_token: str, quote_token: str, amount: float, use_proxy: bool):
        tx_hash, block_number = await self.perform_add_dvm_liquidity(account, address, pair_address, base_token, quote_token, amount, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Add Liquidity Pool Success {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )


    async def process_option_3(self, account: str, address: str, use_proxy: bool):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Random Swap  :{Style.RESET_ALL}                       ")

        for i in range(self.swap_count):
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}Swap{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {i+1} / {self.swap_count} {Style.RESET_ALL}                           "
            )
            for aaa in [('PHRS', 'USDC'), ('PHRS', 'USDT')]:
                option = self.generate_swap_option(aaa[0],aaa[1])
                swap_option = option["swap_option"]
                from_token = option["from_token"]
                to_token = option["to_token"]
                ticker = option["ticker"]
                amount = option["amount"]

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Option  :{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} {swap_option} {Style.RESET_ALL}"
                )

                balance = await self.get_token_balance(address, from_token, use_proxy)
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Balance :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {balance} {ticker} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Amount  :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {amount} {ticker} {Style.RESET_ALL}"
                )

                if not balance or balance <= amount:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} Insufficient {ticker} Token Balance {Style.RESET_ALL}"
                    )
                    continue

                await self.process_perform_swap(account, address, from_token, to_token, amount, use_proxy)
                await self.print_timer()

    async def process_option_4(self, account: str, address: str, use_proxy: bool):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Add Liquidity:{Style.RESET_ALL}                       ")

        for i in range(self.add_lp_count):
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}Pool{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {i+1} / {self.add_lp_count} {Style.RESET_ALL}                           "
            )

            option = self.generate_lp_option()
            lp_option = option["lp_option"]
            base_token = option["base_token"]
            quote_token = option["quote_token"]
            base_ticker = option["base_ticker"]
            quote_ticker = option["quote_ticker"]
            amount = option["amount"]

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Option  :{Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT} {lp_option} {Style.RESET_ALL}"
            )

            base_balance = await self.get_token_balance(address, base_token, use_proxy)
            quote_balance = await self.get_token_balance(address, quote_token, use_proxy)

            self.log(f"{Fore.CYAN+Style.BRIGHT}     Balance :{Style.RESET_ALL}")
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}        ● {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{base_balance} {base_ticker}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}        ● {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{quote_balance} {quote_ticker}{Style.RESET_ALL}"
            )

            self.log(f"{Fore.CYAN+Style.BRIGHT}     Amount  :{Style.RESET_ALL}")
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}        ● {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{amount} {base_ticker}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}        ● {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{amount} {quote_ticker}{Style.RESET_ALL}"
            )

            if not base_balance or base_balance <= amount:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Insufficient {base_ticker} Token Balance {Style.RESET_ALL}"
                )
                continue

            if not quote_balance or quote_balance <= amount:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Insufficient {quote_ticker} Token Balance {Style.RESET_ALL}"
                )
                continue

            pair_address = (
                self.pools[0]["USDC_USDT"] if base_ticker == "USDC" else
                self.pools[0]["USDT_USDC"]
            )

            if not pair_address:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Pool Address Not Found in pools.json {Style.RESET_ALL}"
                )
                break
            
            await self.process_perform_add_dvm_liquidity(account, address, pair_address, base_token, quote_token, amount, use_proxy)
            await self.print_timer()
        
    async def process_accounts(self, account: str, address: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
        if is_valid:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Status       :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Web3 Not Connected {Style.RESET_ALL}"
                )
                return
            
            self.used_nonce[address] = web3.eth.get_transaction_count(address, "pending")


            await self.process_option_3(account, address, use_proxy)

            await self.process_option_4(account, address, use_proxy)
        
    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            
            use_proxy_choice, rotate_proxy = self.print_question()

            self.pools = self.load_pools()


            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            # self.clear_terminal()

            if use_proxy:
                await self.load_proxies(use_proxy_choice)
            
            separator = "=" * 25
            # 增加指定线程数量，使用 asyncio.Semaphore 控制并发线程数
            import asyncio

            async def process_all_accounts(accounts, use_proxy, rotate_proxy, max_concurrent=5):
                semaphore = asyncio.Semaphore(max_concurrent)
                tasks = []

                async def sem_task(account, address):
                    async with semaphore:
                        await self.process_accounts(account, address, use_proxy, rotate_proxy)

                for account in accounts:
                    if account:
                        address = self.generate_address(account)
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )
                        if not address:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}Status       :{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Invalid Private Key or Library Version Not Supported {Style.RESET_ALL}"
                            )
                            continue
                        tasks.append(sem_task(account, address))
                await asyncio.gather(*tasks)
                await asyncio.sleep(3)

            # 你可以在这里指定线程数量，比如 max_concurrent=5
            await process_all_accounts(accounts, use_proxy, rotate_proxy, max_concurrent=5)
            # for account in accounts:
            #     if account:
            #         address = self.generate_address(account)

            #         self.log(
            #             f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
            #             f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
            #             f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
            #         )

            #         if not address:
            #             self.log(
            #                 f"{Fore.CYAN + Style.BRIGHT}Status       :{Style.RESET_ALL}"
            #                 f"{Fore.RED + Style.BRIGHT} Invalid Private Key or Library Version Not Supported {Style.RESET_ALL}"
            #             )
            #             continue

            #     await self.process_accounts(account, address, use_proxy, rotate_proxy)
            #     await asyncio.sleep(3)

            self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*72)

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = Faroswap()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Faroswap - BOT{Style.RESET_ALL}                                       "                              
        )