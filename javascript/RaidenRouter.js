const Router = require("express").Router;
const RaidenService = require("./RaidenService");

const router = new Router();
const raidenservice = new RaidenService();

raidenservice.connect();
router.post('/payments/:token/:receiver',  transfer);
router.get('/balance', getBalance);
router.get('/balance/:token', getTokenBalance);

async function transfer(req, res, next) {
    console.log(`Received request for Token: ${req.params.token} and Receiver ${req.params.receiver} over the amount ${req.body.amount}`);
    try {
        await raidenservice.transfer(req.params.token, req.params.receiver, req.body.amount.toString());
        res.sendStatus(200);
    } catch (e) {
        next(e)
    }
}

async function getBalance(req, res, next) {
    console.log('Received balance request');
    try {
        const balance = await raidenservice.getBalance();
        console.log(balance);
        res.status(200).send(balance);
    } catch (e) {
        next(e);
    }
}

async function getTokenBalance(req, res, next) {
    try {
        console.log(`Got Token balance request for Token: ${req.params.token}`);
        const balance = await raidenservice.getTokenBalance(req.params.token);
        console.log(`the balance is: ${balance}`);
        res.status(200).send(balance)
        } catch (e) {
        next(e);
    }
}

module.exports = router;
