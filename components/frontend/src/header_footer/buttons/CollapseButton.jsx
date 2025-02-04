import UnfoldLessIcon from "@mui/icons-material/UnfoldLess"
import { Button, Tooltip } from "@mui/material"

import { stringsURLSearchQueryPropType } from "../../sharedPropTypes"

export function CollapseButton({ expandedItems }) {
    return (
        <Tooltip title={"Collapse all headers and metrics"}>
            <span /* https://mui.com/material-ui/react-tooltip/#disabled-elements */>
                <Button
                    color="inherit"
                    disabled={expandedItems.equals([])}
                    onClick={() => expandedItems.reset()}
                    startIcon={<UnfoldLessIcon />}
                    sx={{ height: "100%" }}
                >
                    Collapse all
                </Button>
            </span>
        </Tooltip>
    )
}
CollapseButton.propTypes = {
    expandedItems: stringsURLSearchQueryPropType,
}
