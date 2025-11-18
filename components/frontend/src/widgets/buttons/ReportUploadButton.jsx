import UploadFileIcon from "@mui/icons-material/UploadFile"
import { Button, Tooltip } from "@mui/material"
import { styled } from "@mui/material/styles"
import { func } from "prop-types"

import { importReport } from "../../api/report"
import { showMessage } from "../toast"

const VisuallyHiddenInput = styled("input")({
    clip: "rect(0 0 0 0)",
    clipPath: "inset(50%)",
    height: 1,
    overflow: "hidden",
    position: "absolute",
    bottom: 0,
    left: 0,
    whiteSpace: "nowrap",
    width: 1,
})

export function ReportUploadButton({ reload }) {
    return (
        <Tooltip title="Import a new report here">
            <Button
                component="label"
                role={undefined}
                startIcon={<UploadFileIcon />}
                variant="outlined"
                tabIndex="-1" // Skip the button when tabbing, because only the input needs keyboard focus
            >
                {"Import report"}
                <VisuallyHiddenInput
                    accept=".json"
                    data-testid="report-import-input"
                    type="file"
                    onChange={(event) => {
                        if (event.target.files.length > 0) {
                            event.target.files[0]
                                .text()
                                .then((text) => importReport(JSON.parse(text), reload))
                                .catch(({ message }) => showMessage("error", "Import failed", message))
                        }
                    }}
                />
            </Button>
        </Tooltip>
    )
}
ReportUploadButton.propTypes = {
    reload: func,
}
