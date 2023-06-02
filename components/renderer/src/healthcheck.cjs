const http = require('http');

const options = {
    host: 'localhost',
    method: 'GET',
    port: process.env.RENDERER_PORT || 9000,
    path: '/api/health',
};

const healthCheck = http.request(options, (response) => {
    process.exit(response.statusCode == 200 ? 0 : 1);
});

healthCheck.on('error', function() {
    process.exit(1);
});

healthCheck.end();
