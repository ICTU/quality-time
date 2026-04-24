import { ButtonBase as MUIButtonBase } from "@mui/material"
import { func, string } from "prop-types"

import { childrenPropType } from "../../sharedPropTypes"

export function ButtonBase({ ariaLabel, children, onClick }) {
    return (
        <MUIButtonBase
            aria-label={ariaLabel}
            focusRipple
            onClick={onClick}
            sx={{
                display: "block",
                textAlign: "inherit",
                fontSize: "inherit",
                height: "100%",
                padding: 2,
                width: "100%",
                "&:hover, &.Mui-focusVisible": {
                    backgroundColor: "action.hover",
                },
            }}
        >
            {children}
        </MUIButtonBase>
    )
}
ButtonBase.propTypes = {
    ariaLabel: string,
    children: childrenPropType,
    onClick: func,
}
