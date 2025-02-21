import UnfoldLessIcon from "@mui/icons-material/UnfoldLess"

import { stringsURLSearchQueryPropType } from "../../sharedPropTypes"
import { AppBarButton } from "./AppBarbutton"

export function CollapseButton({ expandedItems }) {
    return (
        <AppBarButton
            disabled={expandedItems.equals([])}
            onClick={() => expandedItems.reset()}
            startIcon={<UnfoldLessIcon />}
            tooltip={"Collapse all headers and metrics"}
        >
            Collapse all
        </AppBarButton>
    )
}
CollapseButton.propTypes = {
    expandedItems: stringsURLSearchQueryPropType,
}
