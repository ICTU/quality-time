const http = require("node:http")

const options = {
    host: "localhost",
    port: process.env.RENDERER_PORT || 9000,
    path: "/api/health",
}

function main() {
    let exitCode
    try {
        http.get(options, (response) => {
            exitCode = response.statusCode === 200 ? 0 : 1
        })
    } catch {
        exitCode = 1
    }
    return exitCode
}

module.exports = { main }

/* v8 ignore start */
if (require.main === module) {
    process.exit(main())
}
/* v8 ignore stop */
