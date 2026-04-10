import { List, ListItem, ListItemText } from "@mui/material"

import { StatusIcon } from "../measurement/StatusIcon"
import { STATUS_SHORT_NAME, STATUSES } from "../metric/status"
import { DashboardCard } from "./DashboardCard"

export function LegendCard() {
    const listItems = STATUSES.map((status) => (
        <ListItem key={status} dense={true} sx={{ padding: "0px" }}>
            <StatusIcon status={status} />
            <ListItemText
                primary={STATUS_SHORT_NAME[status]}
                sx={{ marginLeft: "10px", marginTop: "2px", marginBottom: "2px" }}
            />
        </ListItem>
    ))

    return (
        <DashboardCard title="Legend" titleFirst={true}>
            <List sx={{ padding: "0px", whiteSpace: "nowrap" }}>{listItems}</List>
        </DashboardCard>
    )
}
