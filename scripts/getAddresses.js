let warpwallet = require('./warpwallet')

let addresses = [];

generateAddress = (passphrase, salt, currency) => {
  warpwallet.generateWallet(passphrase, salt, currency, (_, result) => {
    if (result) {
      addresses.push(result.public);
    }
  });
}

// user input
const choices = ['bitcoin', 'ethereum']
if (process.argv.length<5) {
  process.exit(0);
}
const currency = process.argv[2];
const allPwds = process.argv.slice(3, process.argv.length);

if (!choices.includes(currency)) {
  process.exit(0);
}

if (allPwds.length%2!=0) {
  process.exit(0)
}

for (let i=0; i<allPwds.length/2; i++) {
  generateAddress(allPwds[2*i], allPwds[2*i+1], currency)
}

(async () => {
  while (addresses.length<allPwds.length/2){
    await new Promise(r => setTimeout(r, 2000))
  }
  console.log(JSON.stringify(addresses))
})()