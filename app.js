const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors({
    origin: 'https://checkmoney.iamgui.dev'
}));

// other routes and configurations
