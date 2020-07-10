const Raiden = require("raiden").Raiden;
const contracts = require("./deployment_rinkeby.json").contracts
const LocalStorage = require("node-localstorage").LocalStorage
const utils = require("ethers").utils

class RaidenService {

    get raiden() {
        if (this._raiden === undefined) {
            throw new Error('Raiden instance was not initialized');
        } else {
            return this._raiden;
        }
    }

    constructor() {
        this._raiden = undefined;
        this.localStorage = new LocalStorage('./raiden_state');

    }

    async connect() {
        try {
            console.log(contracts);
            const raiden = await Raiden.create(
                "https://rinkeby.infura.io/v3/44dc092b7766435dbbca8598767b5a5c",
                "0x8a5a292ca61fb7a6969a56a27be1a2b7d3c14644effa33400ad09af316df345f",
                this.localStorage,
                contracts
            );
            this._raiden = raiden;
        } catch (e) {
            console.log(e);
        }

    }

    async transfer(token, target, amount) {
        try {
          await this.raiden.getAvailability(target);
          await this.raiden.transfer(token, target, utils.parseEther(amount));
        } catch (e) {
          throw new TransferFailed(e);
        }
      }

    async getBalance() {
        const balance = await this.raiden.getBalance();
        return utils.formatEther(balance);
    }

    async getTokenBalance(token) {
        const balance = await this.raiden.getTokenBalance(token);
        return utils.formatEther(balance); 
    }
}

class TransferFailed extends Error {}

module.exports = RaidenService

