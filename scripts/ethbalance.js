const ethers = require('ethers');
require("dotenv").config();

(async () => {
    const args = process.argv.slice(2, process.argv.length);
    const providerURL = process.env.ETH_PROVIDER_URL;
    const provider = new ethers.providers.JsonRpcProvider(providerURL);
    let output = {};
    for (let i=0; i<args.length; i++) {
        let balance = ethers.utils.formatEther(await provider.getBalance(args[i]));
        output[args[i]] = Number(balance);
    }
    console.log(JSON.stringify(output));
})();