import pluginJs from "@eslint/js"
import pluginPrettierConfigRecommended from "eslint-plugin-prettier/recommended"
import pluginSimpleImportSort from "eslint-plugin-simple-import-sort"
import globals from "globals"

export default [
    pluginJs.configs.recommended,
    pluginPrettierConfigRecommended,
    {
        files: ["**/*.js", "**/*.cjs"],
        plugins: {
            "simple-import-sort": pluginSimpleImportSort,
        },
        languageOptions: {
            globals: { ...globals.node },
        },
        rules: {
            "no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
            "n/no-unsupported-features/node-builtins": "off", // Don't complain about 'fetch', 'URL.createObjectURL', and 'navigator'
            "simple-import-sort/imports": "error",
            "simple-import-sort/exports": "error",
        },
    },
    {
        files: ["**/*.test.js", "**/*.test.jsx"],
        rules: {
            "no-import-assign": "off",
        },
    },
]
