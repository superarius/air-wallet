let warpwallet = require('./warpwallet')

generate = (passphrase, salt, currency) => {
    warpwallet.generateWallet(passphrase, salt, currency, (_, result) => {
      if (result) {
        console.log(JSON.stringify(result));
      }
    });
}

// user input
const choices = ['bitcoin', 'ethereum'];
if (process.argv.length<5) {
  process.exit(0);
}
const currency = process.argv[2];
const pwd = process.argv[3];
const salt = process.argv[4];
if (!choices.includes(currency)) {
  process.exit(0)
}

generate(pwd, salt, currency)