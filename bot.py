# -*- coding: utf-8 -*-
from web3 import Web3
import time
import requests

# Connect to the Monad network via Infura RPC
infura_url = "https://testnet-rpc.monad.xyz"
web3 = Web3(Web3.HTTPProvider(infura_url, request_kwargs={'timeout': 60}))

# Check if the connection is successful
if not web3.is_connected():
    raise Exception("Failed to connect to Monad network")

# Constants
CHAIN_ID = 10143  # Monad Chain ID
MAX_RETRIES = 3  # Maximum retries per transaction
PRIVATE_KEY = ""  # Hardcoded private key (replace with caution)

# Function to send ETH transaction to a single wallet
def send_eth_transaction_to_wallet(private_key, amount, to_address):
    sender_address = web3.eth.account.from_key(private_key).address
    value_to_send = web3.to_wei(amount, 'ether')

    for attempt in range(MAX_RETRIES):
        try:
            nonce = web3.eth.get_transaction_count(sender_address)
            gas_price = web3.eth.gas_price * 1.1
            estimated_gas_limit = web3.eth.estimate_gas({
                'from': sender_address,
                'to': to_address,
                'value': value_to_send
            })
            gas_limit = int(estimated_gas_limit * 1.2)

            tx = {
                'nonce': nonce,
                'to': to_address,
                'value': value_to_send,
                'gas': gas_limit,
                'gasPrice': int(gas_price),
                'chainId': CHAIN_ID
            }

            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)  # Fixed rawTransaction attribute
            print(f"Sent {amount} ETH to {to_address}. Tx Hash: {web3.to_hex(tx_hash)}")
            return True  # Successfully sent
        except requests.exceptions.HTTPError as e:
            print(f"HTTPError on attempt {attempt+1}: {e}")
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(5)
            else:
                print("Transaction failed after maximum retries.")
    return False

# Function to load wallet addresses from wallets.txt
def load_wallet_addresses(filename="wallets.txt"):
    with open(filename, "r") as file:
        wallets = [line.strip() for line in file.readlines()]
    return wallets

# Get user input for the ETH amount
def get_user_input():
    amount = float(input("Enter the amount of ETH to send to each wallet: "))  # Prompt the user for ETH amount
    return amount

# Load wallet addresses and send transactions
wallets = load_wallet_addresses()  # Load the wallet addresses from wallets.txt
amount = get_user_input()  # Get user input for amount

# Send the specified amount of ETH to each wallet in the list
for to_address in wallets:
    send_eth_transaction_to_wallet(PRIVATE_KEY, amount, to_address)
    time.sleep(5)  # Add a small delay between transactions
