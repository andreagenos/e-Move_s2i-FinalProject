from web3 import Web3

def sendTransaction(message):
    w3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/b51ab601fbea4871845fe9f621bc9746'))
    address = '0x2F34362E3E74b4693610C231378e4C124562faA1'
    privateKey = '354ccbaac552bf0a4c3fd0004b50d4225b9d84732e0fc17bde7ffae2ba25eb80'
    nonce = w3.eth.get_transaction_count(address, 'pending')
    #w3.eth.get_transaction_count(address)
    gasPrice = w3.eth.gas_price
    value = w3.to_wei(0,'ether')
    signedTx = w3.eth.account.sign_transaction(dict(
        nonce=nonce,
        gasPrice=gasPrice,
        gas=100000,
        to='0x0000000000000000000000000000000000000000',
        value=value,
        data=message.encode('utf-8')
    ), privateKey)

    tx = w3.eth.send_raw_transaction(signedTx.rawTransaction)
    txId = w3.to_hex(tx)
    return txId

