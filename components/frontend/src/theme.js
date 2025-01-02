import { grey, orange } from "@mui/material/colors"
import { alpha, createTheme, responsiveFontSizes } from "@mui/material/styles"

export let theme = createTheme({
    colorSchemes: {
        dark: true, // Add a dark theme (light theme is available by default)
    },
    components: {
        MuiTooltip: {
            defaultProps: { arrow: true },
            styleOverrides: { tooltip: { fontSize: "1em" } },
        },
    },
})

theme = createTheme(theme, {
    palette: {
        contrastThreshold: 4.5,
        todo: theme.palette.augmentColor({ color: { main: grey[600] }, name: "todo" }),
        doing: theme.palette.augmentColor({ color: { main: theme.palette.info.main }, name: "doing" }),
        done: theme.palette.augmentColor({ color: { main: theme.palette.success.main }, name: "done" }),
        target_not_met: theme.palette.augmentColor({
            color: { main: theme.palette.error.main },
            name: "target_not_met",
        }),
        target_met: theme.palette.augmentColor({ color: { main: theme.palette.success.main }, name: "target_met" }),
        near_target_met: theme.palette.augmentColor({ color: { main: orange[300] }, name: "near_target_met" }),
        debt_target_met: theme.palette.augmentColor({ color: { main: grey[500] }, name: "debt_target_met" }),
        informative: theme.palette.augmentColor({ color: { main: theme.palette.info.main }, name: "informative" }),
        unknown: theme.palette.augmentColor({ color: { main: grey[300] }, name: "unknown" }),
        total: theme.palette.augmentColor({ color: { main: grey[800] }, name: "total" }),
    },
    typography: {
        h1: {
            fontSize: theme.typography.h4.fontSize,
            fontWeight: 700,
        },
        h2: {
            fontSize: theme.typography.h5.fontSize,
            fontWeight: 600,
        },
        h3: {
            fontSize: theme.typography.h6.fontSize,
        },
        h4: {
            fontSize: theme.typography.subtitle1.fontSize,
        },
        h5: {
            fontSize: theme.typography.subtitle2.fontSize,
        },
    },
})

const bgcolorTransparency = 0.2
const hoverTransparency = 0.25

theme = createTheme(theme, {
    palette: {
        target_not_met: {
            bgcolor: alpha(theme.palette.target_not_met.main, bgcolorTransparency),
            hover: alpha(theme.palette.target_not_met.main, hoverTransparency),
        },
        target_met: {
            bgcolor: alpha(theme.palette.target_met.main, bgcolorTransparency),
            hover: alpha(theme.palette.target_met.main, hoverTransparency),
        },
        near_target_met: {
            bgcolor: alpha(theme.palette.near_target_met.main, bgcolorTransparency),
            hover: alpha(theme.palette.near_target_met.main, hoverTransparency),
        },
        debt_target_met: {
            bgcolor: alpha(theme.palette.debt_target_met.main, bgcolorTransparency),
            hover: alpha(theme.palette.debt_target_met.main, hoverTransparency),
        },
        informative: {
            bgcolor: alpha(theme.palette.informative.main, bgcolorTransparency),
            hover: alpha(theme.palette.informative.main, hoverTransparency),
        },
        unknown: {
            bgcolor: alpha(theme.palette.unknown.main, bgcolorTransparency),
            hover: alpha(theme.palette.unknown.main, hoverTransparency),
        },
    },
})

theme = responsiveFontSizes(theme)
