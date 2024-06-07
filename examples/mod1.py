import xrpl

testnet_url = "https://s.devnet.rippletest.net:51234/"


def get_account(seed):
    """
    get_account
    This method lets you get an existing account by providing a seed value.
    If you provide no seed value, the method creates a new account for you.
    """
    # Request a new client from the XRP Ledger.
    client = xrpl.clients.JsonRpcClient(testnet_url)
    # If no seed is provided, generate a new wallet. Otherwise, use the provided seed to get the wallet.
    if (seed == ''):
        new_wallet = xrpl.wallet.generate_faucet_wallet(client)
    else:
        new_wallet = xrpl.wallet.Wallet.from_seed(seed)
    return new_wallet


def get_account_info(accountId):
    """
    get_account_info
    """
    client = xrpl.clients.JsonRpcClient(testnet_url)
    # Create the account info request, passing the account ID and the ledger index
    # (in this case, the latest validated ledger).
    # validated means get the latest ledger that has been validated by the network. Also, can use current or an ID/Hash.
    acct_info = xrpl.models.requests.account_info.AccountInfo(
        account=accountId,
        ledger_index="validated"
    )
    response = client.request(acct_info)
    return response.result['account_data']


def send_xrp(seed, amount, destination):
    # get the wallet entity from the seed
    sending_wallet = xrpl.wallet.Wallet.from_seed(seed)
    # Create a new client
    client = xrpl.clients.JsonRpcClient(testnet_url)
    # Fetch account info to get the current balance
    account_info = xrpl.account_info.get_account_info(sending_wallet.address, client)
    balance_drops = int(account_info['result']['account_data']['Balance'])

    # Convert amount to drops
    amount_drops = xrpl.utils.xrp_to_drops(float(amount))

    # Estimate transaction fee (default is usually 10 drops, can vary)
    fee_drops = 10

    # Check if the balance is sufficient
    if balance_drops < amount_drops + fee_drops:
        return f"Insufficient funds: Balance is {balance_drops} drops, but need {amount_drops + fee_drops} drops (including fee)."
    # Create a payment transaction
    else:
        payment = xrpl.models.transactions.Payment(
            account=sending_wallet.address,
            # use xrp_to_drops to convert the amount to drops to avoid accuracy issues
            amount=xrpl.utils.xrp_to_drops(int(amount)),
            destination=destination,
        )
        try:
            response = xrpl.transaction.submit_and_wait(payment, client, sending_wallet)
        except xrpl.transaction.XRPLReliableSubmissionException as e:
            response = f"Submit failed: {e}"

        return response


if __name__ == '__main__':
    new_wallet = get_account('')
    address = new_wallet.classic_address
    info = get_account_info(address)
    print(f"Account Info for {address}: {info}")
    new_wallet2 = get_account('')
    address2 = new_wallet2.classic_address
    response = send_xrp(new_wallet.seed, 10, address2)
    print(f"Sent 500 XRP from {address} to {address2}: {response}")
    print()
