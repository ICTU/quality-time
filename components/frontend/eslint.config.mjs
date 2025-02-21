import { fixupConfigRules } from "@eslint/compat"
import pluginJs from "@eslint/js"
import pluginJest from "eslint-plugin-jest"
import pluginPrettierConfigRecommended from "eslint-plugin-prettier/recommended"
import pluginPromise from "eslint-plugin-promise"
import pluginReactJSXRuntime from "eslint-plugin-react/configs/jsx-runtime.js"
import pluginReactConfigRecommended from "eslint-plugin-react/configs/recommended.js"
import pluginSimpleImportSort from "eslint-plugin-simple-import-sort"
import globals from "globals"

export default [
    {
        settings: {
            react: {
                version: "detect",
            },
        },
    },
    pluginJs.configs.recommended,
    pluginJest.configs["flat/recommended"],
    ...fixupConfigRules(pluginReactConfigRecommended),
    ...fixupConfigRules(pluginReactJSXRuntime),
    pluginPrettierConfigRecommended,
    {
        files: ["**/*.js", "**/*.jsx"],
        plugins: {
            "simple-import-sort": pluginSimpleImportSort,
            promise: pluginPromise,
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
            "promise/always-return": "error",
            "promise/no-return-wrap": "error",
            "promise/param-names": "error",
            "promise/catch-or-return": ["error", { allowFinally: true }],
            "promise/no-native": "off",
            "promise/no-nesting": "warn",
            "promise/no-promise-in-callback": "warn",
            "promise/no-callback-in-promise": "warn",
            "promise/avoid-new": "warn",
            "promise/no-new-statics": "error",
            "promise/no-return-in-finally": "warn",
            "promise/valid-params": "warn",
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
