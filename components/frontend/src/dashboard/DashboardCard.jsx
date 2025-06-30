import { Card, CardActionArea, CardContent, CardHeader } from "@mui/material"
import { bool, element, func, oneOfType, string } from "prop-types"

import { childrenPropType } from "../sharedPropTypes"

export function DashboardCard({ children, onClick, selected, title, titleFirst }) {
    const color = selected ? "info.main" : "divider"
    const header = (
        <CardHeader
            title={title}
            // The selected class is for test purposes only
            slotProps={{ title: { className: selected ? "selected" : "", noWrap: true, variant: "h6" } }}
            sx={{
                padding: "0px",
                paddingTop: titleFirst ? "10px" : "0px",
                textAlign: "center",
                verticalAlign: "center",
            }}
        />
    )
    // The components below get a height of 100% to make sure they fill the available space of their container
    return (
        <Card
            onClick={onClick}
            sx={{
                border: 1,
                borderColor: color,
                height: "100%",
                "&:hover": { boxShadow: "4", borderColor: "text.primary" },
            }}
        >
            <CardActionArea disableRipple={!onClick} sx={{ height: "100%" }}>
                <CardContent sx={{ paddingBottom: titleFirst ? "0px" : "10px", paddingTop: "0px", height: "100%" }}>
                    {titleFirst && header}
                    {children}
                    {!titleFirst && header}
                </CardContent>
            </CardActionArea>
        </Card>
    )
}
DashboardCard.propTypes = {
    children: childrenPropType,
    onClick: func,
    selected: bool,
    title: oneOfType([element, string]),
    titleFirst: bool,
}
