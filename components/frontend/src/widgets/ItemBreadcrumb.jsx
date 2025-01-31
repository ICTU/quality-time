import NavigateNextIcon from "@mui/icons-material/NavigateNext"
import { Breadcrumbs } from "@mui/material"
import { string } from "prop-types"

export function ItemBreadcrumb(props) {
    return (
        <Breadcrumbs separator={<NavigateNextIcon fontSize="small" />}>
            <span>{props.report}</span>
            {props.subject && <span>{props.subject}</span>}
            {props.metric && <span>{props.metric}</span>}
            {props.source && <span>{props.source}</span>}
        </Breadcrumbs>
    )
}
ItemBreadcrumb.propTypes = {
    metric: string,
    report: string,
    source: string,
    subject: string,
}
