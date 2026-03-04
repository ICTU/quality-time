import "@testing-library/jest-dom"

import { toHaveNoViolations } from "jest-axe"

expect.extend(toHaveNoViolations)

// Suppress MUI anchorEl "not in document layout" warnings in jsdom (zero-sized rects).
// Our issue: https://github.com/ICTU/quality-time/issues/12719
// Upstream issue: https://github.com/mui/material-ui/issues/47792
globalThis.MUI_TEST_ENV = true
