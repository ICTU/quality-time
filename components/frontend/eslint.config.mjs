import pluginJs from "@eslint/js"
import pluginReact from "@eslint-react/eslint-plugin"
import pluginJest from "eslint-plugin-jest"
import pluginPrettierConfigRecommended from "eslint-plugin-prettier/recommended"
import pluginSimpleImportSort from "eslint-plugin-simple-import-sort"
import globals from "globals"

export default [
    pluginJs.configs.recommended,
    pluginJest.configs["flat/recommended"],
    pluginReact.configs.recommended,
    pluginPrettierConfigRecommended,
    {
        files: ["**/*.js", "**/*.jsx"],
        plugins: {
            "simple-import-sort": pluginSimpleImportSort,
        },
        languageOptions: {
            globals: { ...globals.browser, ...globals.node },
            parserOptions: {
                ecmaFeatures: {
                    jsx: true,
                },
            },
        },
        rules: {
            "no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
            "n/no-unsupported-features/node-builtins": "off", // Don't complain about 'fetch', 'URL.createObjectURL', and 'navigator'
            "@eslint-react/no-prop-types": "off",
            "@eslint-react/no-use-context": "off",
            "simple-import-sort/imports": "error",
            "simple-import-sort/exports": "error",
        },
    },
    {
        files: ["**/*.test.js", "**/*.test.jsx"],
        rules: {
            "no-import-assign": "off",
            "jest/expect-expect": ["error", { assertFunctionNames: ["expect*"] }],
        },
    },
]
