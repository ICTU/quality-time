import { Button, Tooltip } from "@mui/material"
import { grey } from "@mui/material/colors"
import { bool, element, func, object, string } from "prop-types"

import { childrenPropType } from "../../sharedPropTypes"

export function AppBarButton({ children, disabled, loading, onClick, startIcon, sx, tooltip }) {
    return (
        <Tooltip title={tooltip}>
            <span /* https://mui.com/material-ui/react-tooltip/#disabled-elements */>
                <Button
                    aria-label={tooltip}
                    color="inherit"
                    disabled={disabled}
                    loading={loading}
                    loadingPosition="start"
                    onClick={() => onClick()}
                    startIcon={startIcon}
                    sx={{ ...sx, height: "100%", "&:disabled": { color: grey[400] } }}
                >
                    {children}
                </Button>
            </span>
        </Tooltip>
    )
}
AppBarButton.propTypes = {
    children: childrenPropType,
    disabled: bool,
    loading: bool,
    onClick: func,
    startIcon: element,
    sx: object,
    tooltip: string,
}
