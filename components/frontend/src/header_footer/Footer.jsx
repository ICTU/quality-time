import BugReportIcon from "@mui/icons-material/BugReport"
import CopyrightIcon from "@mui/icons-material/Copyright"
import FeedbackIcon from "@mui/icons-material/Feedback"
import GitHubIcon from "@mui/icons-material/GitHub"
import HistoryIcon from "@mui/icons-material/History"
import MenuBookIcon from "@mui/icons-material/MenuBook"
import PersonIcon from "@mui/icons-material/Person"
import ScienceIcon from "@mui/icons-material/Science"
import {
    AppBar,
    Box,
    Container,
    Divider,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Stack,
    Typography,
} from "@mui/material"
import { grey } from "@mui/material/colors"
import Grid from "@mui/material/Grid"
import { element, object, oneOfType, string } from "prop-types"

import { alignmentPropType, childrenPropType, datePropType, reportPropType } from "../sharedPropTypes"
import { DOCUMENTATION_URL, REPOSITORY_URL } from "../utils"

function FooterItem({ children, icon, url }) {
    const color = grey[300]
    let item = <ListItemText sx={{ color: color, textAlign: icon ? "left" : "center" }}>{children}</ListItemText>
    if (icon) {
        item = (
            <>
                <ListItemIcon sx={{ color: color, minWidth: 28 }}>{icon}</ListItemIcon>
                {item}
            </>
        )
    }
    if (url) {
        item = (
            <ListItemButton href={url} rel="noreferrer" target="_blank" sx={{ padding: 0 }}>
                {item}
            </ListItemButton>
        )
    }
    return <ListItem disablePadding>{item}</ListItem>
}
FooterItem.propTypes = {
    children: childrenPropType,
    icon: element,
    url: string,
}

function FooterColumn({ children, header, textAlign }) {
    return (
        <Stack>
            <Typography sx={{ color: "white", textAlign: textAlign }}>{header || <>&zwnj;</>}</Typography>
            <List dense>{children}</List>
        </Stack>
    )
}
FooterColumn.propTypes = {
    children: childrenPropType,
    header: oneOfType([object, string]),
    textAlign: alignmentPropType,
}

function AboutAppColumn() {
    return (
        <FooterColumn header={<>Quality-time v{import.meta.env.VITE_APP_VERSION}</>}>
            <FooterItem icon={<ScienceIcon />} url="https://www.ictu.nl/about-us">
                Created by ICTU
            </FooterItem>
            <FooterItem icon={<CopyrightIcon />} url={`${REPOSITORY_URL}/blob/master/LICENSE`}>
                License
            </FooterItem>
            <FooterItem icon={<HistoryIcon />} url={`${DOCUMENTATION_URL}/changelog.html`}>
                Changelog
            </FooterItem>
            <FooterItem icon={<GitHubIcon />} url={REPOSITORY_URL}>
                Source code
            </FooterItem>
        </FooterColumn>
    )
}

function SupportColumn() {
    return (
        <FooterColumn header="Support">
            <FooterItem icon={<MenuBookIcon />} url={DOCUMENTATION_URL}>
                Documentation
            </FooterItem>
            <FooterItem icon={<PersonIcon />} url={`${DOCUMENTATION_URL}/usage.html`}>
                User manual
            </FooterItem>
            <FooterItem icon={<BugReportIcon />} url={`${REPOSITORY_URL}/issues`}>
                Known issues
            </FooterItem>
            <FooterItem icon={<FeedbackIcon />} url={`${REPOSITORY_URL}/issues/new`}>
                Report an issue
            </FooterItem>
        </FooterColumn>
    )
}

function AboutReportColumn({ lastUpdate, report }) {
    lastUpdate = lastUpdate ?? new Date()
    // When exporting to PDF, globalThis.location.href may not be the correct URL. This is fixed by having the user's
    // browser pass the correct URL as search parameter and use that instead:
    const reportURL = new URLSearchParams(globalThis.location.search).get("report_url") ?? globalThis.location.href
    return (
        <FooterColumn header="About this report" textAlign="center">
            <FooterItem url={reportURL}>{report.title}</FooterItem>
            <FooterItem>{report.subtitle}</FooterItem>
            <FooterItem>{lastUpdate.toLocaleDateString()}</FooterItem>
            <FooterItem>{lastUpdate.toLocaleTimeString()}</FooterItem>
        </FooterColumn>
    )
}
AboutReportColumn.propTypes = {
    lastUpdate: datePropType,
    report: reportPropType,
}

function QuoteColumn() {
    const quotes = [
        ["If it hurts, do it more frequently,", "and bring the pain forward.", "Jez Humble"],
        ["Quality without results is pointless.", "Results without quality is boring.", "Johan Cruyff"],
        ["Quality is free,", "but only to those who are willing to pay heavily for it.", "DeMarco and Lister"],
        ["Quality means doing it right", "even when no one is looking.", "Henry Ford"],
        ["Quality... you know what it is,", "yet you don't know what it is.", "Robert M. Pirsig"],
    ]
    const randomQuote = quotes[Math.floor(Math.random() * quotes.length)]
    return (
        <FooterColumn>
            <FooterItem>
                <em>{randomQuote[0]}</em>
            </FooterItem>
            <FooterItem>
                <em>{randomQuote[1]}</em>
            </FooterItem>
            <FooterItem>{randomQuote[2]}</FooterItem>
        </FooterColumn>
    )
}

export function Footer({ lastUpdate, report }) {
    return (
        <AppBar component="footer" position="relative" sx={{ displayPrint: "none", flex: 0 }}>
            <Container maxWidth="md" sx={{ padding: "60px" }}>
                <Grid container spacing={2} columns={{ xs: 1, sm: 3 }}>
                    <Grid size={1}>
                        <AboutAppColumn />
                    </Grid>
                    <Grid size={1}>
                        {report ? <AboutReportColumn lastUpdate={lastUpdate} report={report} /> : <QuoteColumn />}
                    </Grid>
                    <Grid size={1}>
                        <Box display="flex" justifyContent="flex-end">
                            <SupportColumn />
                        </Box>
                    </Grid>
                </Grid>
                <Divider aria-hidden="true">
                    <img alt="" src="./favicon.ico" width="30px" />
                </Divider>
            </Container>
        </AppBar>
    )
}
Footer.propTypes = {
    lastUpdate: datePropType,
    report: reportPropType,
}
