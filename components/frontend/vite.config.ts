import os from "node:os"
import path from "node:path"
import process from "node:process"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
    base: "",
    plugins: [
        react({
            jsxImportSource: "@emotion/react",
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
    test: {
        globals: true,
        coverage: {
            include: ["src"],
            exclude: ["src/index.jsx", "src/**/.DS_Store"],
            reporter: [["text", { maxCols: 200 }], "lcov", "html"],
            reportsDirectory: "build",
            skipFull: true,
            thresholds: {
                statements: 100,
                branches: 100,
                functions: 100,
                lines: 100,
            },
        },
        deps: {
            optimizer: {
                web: {
                    enabled: true,
                },
            },
        },
        environment: "jsdom",
        mockReset: true,
        setupFiles: "./src/setupTests.js",
        testTimeout: 15000,
        execArgv: ["--localstorage-file", path.resolve(os.tmpdir(), `vitest-${process.pid}.localstorage`)], // See https://github.com/vitest-dev/vitest/issues/8757
    },
})
