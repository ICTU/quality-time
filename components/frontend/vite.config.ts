import browserslistToEsbuild from "browserslist-to-esbuild"
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

export default defineConfig({
    base: "",
    plugins: [
        react({
            jsxImportSource: "@emotion/react",
            babel: {
                plugins: ["@emotion/babel-plugin"],
            },
        }),
    ],
    resolve: {
        conditions: ["mui-modern", "module", "browser", "development|production"],
    },
    server: {
        open: true, // Ensure that the browser opens upon server start
        port: 3000, // Set default port to 3000
        proxy: { "/api": "http://localhost:5001" },
        watch: {
            ignored: ["**/node_modules/**", "**/build/**", "**/dist/**"], // Ignore large directories
        },
    },
    build: {
        target: browserslistToEsbuild([">0.2%", "not dead", "not op_mini all"]),
    },
    test: {
        globals: true,
        coverage: {
            include: ["src"],
            reporter: ["text", "lcov", "html"],
            skipFull: true,
        },
        environment: "jsdom",
        mockReset: true,
        setupFiles: "./src/setupTests.js",
        testTimeout: 15000,
    },
})
