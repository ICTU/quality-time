import { defineConfig } from "vitest/config";

export default defineConfig({
    test: {
        coverage: {
            include: ["src/**/*.cjs", "src/index.js"],
            exclude: ["src/**/.DS_Store"],
            reporter: [["text", { maxCols: 200 }], "lcov", "html"],
            skipFull: true,
            thresholds: {
                statements: 100,
                branches: 100,
                functions: 100,
                lines: 100,
            },
        },
    },
});
