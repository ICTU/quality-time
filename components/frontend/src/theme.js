import { grey, orange } from "@mui/material/colors"
import { alpha, createTheme, responsiveFontSizes } from "@mui/material/styles"

// Construct the theme in a few phases so we can reuse components defined in earlier phases

const theme1 = createTheme({
    colorSchemes: {
        dark: true, // Add a dark theme (light theme is available by default)
    },
    components: {
        MuiTooltip: {
            defaultProps: { arrow: true },
            styleOverrides: { tooltip: { fontSize: "0.9rem" } },
        },
        MuiTextField: {
            defaultProps: { variant: "filled" },
        },
        MuiPickersTextField: {
            defaultProps: { variant: "filled" }, // Should be the same as MuiTextField, see https://mui.com/x/migration/migration-pickers-v7/
        },
    },
    palette: {
        primary: {
            main: "#0F569C", // Slightly darker blue than default
        },
        secondary: {
            main: "#502c09", // Secondary color created with https://m2.material.io/design/color/the-color-system.html#tools-for-picking-colors
        },
    },
    typography: {
        fontFamily: "sans-serif", // Use browser font
    },
})

const theme2 = createTheme(theme1, {
    palette: {
        contrastThreshold: 4.5,
        todo: theme1.palette.augmentColor({ color: { main: grey[600] }, name: "todo" }),
        doing: theme1.palette.augmentColor({ color: { main: theme1.palette.info.main }, name: "doing" }),
        done: theme1.palette.augmentColor({ color: { main: theme1.palette.success.main }, name: "done" }),
        target_not_met: theme1.palette.augmentColor({
            color: { main: theme1.palette.error.main },
            name: "target_not_met",
        }),
        target_met: theme1.palette.augmentColor({ color: { main: theme1.palette.success.main }, name: "target_met" }),
        near_target_met: theme1.palette.augmentColor({ color: { main: orange[300] }, name: "near_target_met" }),
        debt_target_met: theme1.palette.augmentColor({ color: { main: grey[500] }, name: "debt_target_met" }),
        informative: theme1.palette.augmentColor({ color: { main: theme1.palette.info.main }, name: "informative" }),
        unknown: theme1.palette.augmentColor({ color: { main: grey[300] }, name: "unknown" }),
        total: theme1.palette.augmentColor({ color: { main: grey[800] }, name: "total" }),
        positive_status: theme1.palette.augmentColor({
            color: { main: theme1.palette.success.main },
            name: "positive_status",
        }),
        negative_status: theme1.palette.augmentColor({
            color: { main: theme1.palette.error.main },
            name: "negative_status",
        }),
        warning_status: theme1.palette.augmentColor({ color: { main: orange[300] }, name: "warning_status" }),
        active_status: theme1.palette.augmentColor({ color: { main: grey[500] }, name: "active_status" }),
        unknown_status: theme1.palette.augmentColor({ color: { main: grey[300] }, name: "unknown_status" }),
        edit_scope_source: theme1.palette.augmentColor({ color: { main: grey[300] }, name: "edit_scope_source" }),
        edit_scope_metric: theme1.palette.augmentColor({
            color: { main: theme1.palette.primary.main },
            name: "edit_scope_metric",
        }),
        edit_scope_subject: theme1.palette.augmentColor({
            color: { main: orange[300] },
            name: "edit_scope_subject",
        }),
        edit_scope_report: theme1.palette.augmentColor({
            color: { main: theme1.palette.warning.main },
            name: "edit_scope_report",
        }),
        edit_scope_reports: theme1.palette.augmentColor({
            color: { main: theme1.palette.error.main },
            name: "edit_scope_reports",
        }),
        entity_status_count_badge: theme1.palette.augmentColor({
            color: { main: grey[300] },
            name: "entity_status_count_badge",
        }),
    },
    typography: {
        h1: {
            fontSize: theme1.typography.h4.fontSize,
            fontWeight: 700,
        },
        h2: {
            fontSize: theme1.typography.h5.fontSize,
            fontWeight: 600,
        },
        h3: {
            fontSize: theme1.typography.h6.fontSize,
        },
        h4: {
            fontSize: theme1.typography.subtitle1.fontSize,
        },
        h5: {
            fontSize: theme1.typography.subtitle2.fontSize,
        },
    },
})

const bgcolorTransparency = 0.2
const hoverTransparency = 0.25

const theme3 = createTheme(theme2, {
    palette: {
        target_not_met: {
            bgcolor: alpha(theme2.palette.target_not_met.main, bgcolorTransparency),
            hover: alpha(theme2.palette.target_not_met.main, hoverTransparency),
        },
        target_met: {
            bgcolor: alpha(theme2.palette.target_met.main, bgcolorTransparency),
            hover: alpha(theme2.palette.target_met.main, hoverTransparency),
        },
        near_target_met: {
            bgcolor: alpha(theme2.palette.near_target_met.main, bgcolorTransparency),
            hover: alpha(theme2.palette.near_target_met.main, hoverTransparency),
        },
        debt_target_met: {
            bgcolor: alpha(theme2.palette.debt_target_met.main, bgcolorTransparency),
            hover: alpha(theme2.palette.debt_target_met.main, hoverTransparency),
        },
        informative: {
            bgcolor: alpha(theme2.palette.informative.main, bgcolorTransparency),
            hover: alpha(theme2.palette.informative.main, hoverTransparency),
        },
        unknown: {
            bgcolor: alpha(theme2.palette.unknown.main, bgcolorTransparency),
            hover: alpha(theme2.palette.unknown.main, hoverTransparency),
        },
        positive_status: {
            bgcolor: alpha(theme2.palette.positive_status.main, bgcolorTransparency),
            hover: alpha(theme2.palette.positive_status.main, hoverTransparency),
        },
        negative_status: {
            bgcolor: alpha(theme2.palette.negative_status.main, bgcolorTransparency),
            hover: alpha(theme2.palette.negative_status.main, hoverTransparency),
        },
        warning_status: {
            bgcolor: alpha(theme2.palette.warning_status.main, bgcolorTransparency),
            hover: alpha(theme2.palette.warning_status.main, hoverTransparency),
        },
        active_status: {
            bgcolor: alpha(theme2.palette.active_status.main, bgcolorTransparency),
            hover: alpha(theme2.palette.active_status.main, hoverTransparency),
        },
        unknown_status: {
            bgcolor: alpha(theme2.palette.unknown_status.main, bgcolorTransparency),
            hover: alpha(theme2.palette.unknown_status.main, hoverTransparency),
        },
    },
})

export const theme = responsiveFontSizes(theme3)
