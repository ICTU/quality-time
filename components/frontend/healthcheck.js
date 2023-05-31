const http = require('http');

const options = {
    host: 'localhost',
    method: 'GET',
    port: process.env.FRONTEND_PORT || 5000,
    path: '/favicon.ico',
};

const healthCheck = http.request(options, (response) => {
    process.exit(response.statusCode == 200 ? 0 : 1);
});

healthCheck.on('error', function() {
    process.exit(1);
});

healthCheck.end();
