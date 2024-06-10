const http = require("http")

const options = {
    headers: { Connection: "close" },
    host: "localhost",
    method: "GET",
    path: "/favicon.ico",
    port: process.env.FRONTEND_PORT || 5000,
}

const healthCheck = http.request(options, (response) => {
    process.exitCode = response.statusCode == 200 ? 0 : 1
})

healthCheck.on("error", function () {
    process.exitCode = 1
})

healthCheck.end()
