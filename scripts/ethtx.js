const ethers = require('ethers');
require("dotenv").config();

(async () => {
    const args = process.argv;
    const providerURL = process.env.ETH_PROVIDER_URL;
    const provider = new ethers.providers.JsonRpcProvider(providerURL);
    let command = args[2];
    let priv = args[3];
    let receiver = args[4];
    if (priv.substring(0, 2) != '0x') {
        priv = '0x'+priv;
    }
    const wallet = new ethers.Wallet(priv, provider);
    if (command == 'send') {
        let amount = ethers.utils.parseEther(args[5]);
        let tx = {
            to: receiver,
            value: amount,
        }
        let txreceipt = await wallet.sendTransaction(tx);
        console.log(txreceipt.hash);
    } else if (command == 'sweep') {
        let gasPrice = await provider.getGasPrice();
        let totalGas = gasPrice*21000;
        let balance = await provider.getBalance(wallet.address);
        let amount = balance-totalGas;
        let tx = {
            to: receiver,
            value: amount.toString(),
            gasLimit: 21000,
            gasPrice: gasPrice,
        }
        let txreceipt = await wallet.sendTransaction(tx);
        console.log(txreceipt.hash);
    }
})();