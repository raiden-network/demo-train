const express = require("express");
const logger = require("morgan");
const bodyParser = require("body-parser");
const router = require("./RaidenRouter");

// Creates and configures an ExpressJS web server.
class App {

    //Run configuration methods on the Express instance.
    constructor() {
        this.express = express();
        this.middleware();
        this.routes();
    }

    // Configure Express middleware.
    middleware() {
        this.express.use(logger('dev'));
        this.express.use(bodyParser.json());
        this.express.use(bodyParser.urlencoded({ extended: false }));
    }

    // Configure API endpoints.
    routes() {
        this.express.use('/api/v1', router)
    }

};

module.exports = new App().express
