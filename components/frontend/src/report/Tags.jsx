import { Grid, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material"
import { func, string } from "prop-types"
import { useContext, useState } from "react"

import { deleteTag, renameTag } from "../api/report"
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { TextField } from "../fields/TextField"
import { reportPropType } from "../sharedPropTypes"
import { getMetricTags, getReportTags } from "../utils"
import { DeleteButton } from "../widgets/buttons/DeleteButton"
import { TableRowWithDetails } from "../widgets/TableRowWithDetails"
import { Tag } from "../widgets/Tag"
import { InfoMessage } from "../widgets/WarningMessage"

function nrMetricsWithTag(report, tag) {
    let count = 0
    Object.values(report.subjects).forEach((subject) => {
        Object.values(subject.metrics).forEach((metric) => {
            if (getMetricTags(metric).includes(tag)) {
                count++
            }
        })
    })
    return count
}

function TagEditor({ reload, report, tag }) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    return (
        <Grid container spacing={{ xs: 1, sm: 2, md: 2 }} sx={{ alignItems: "center", margin: "10px" }}>
            <Grid size="grow">
                <TextField
                    disabled={disabled}
                    label="Tag"
                    onChange={(value) => renameTag(report.report_uuid, tag, value, reload)}
                    value={tag}
                />
            </Grid>
            {!disabled && (
                <Grid>
                    <DeleteButton
                        itemType="tag"
                        onClick={() => {
                            console.log(tag)
                            deleteTag(report.report_uuid, tag, reload)
                        }}
                    />
                </Grid>
            )}
        </Grid>
    )
}
TagEditor.propTypes = {
    reload: func.isRequired,
    report: reportPropType,
    tag: string.isRequired,
}

function TagRow({ reload, report, tag }) {
    const [expanded, setExpanded] = useState(false)
    return (
        <TableRowWithDetails
            details={<TagEditor reload={reload} report={report} tag={tag} />}
            expanded={expanded}
            onExpand={setExpanded}
        >
            <TableCell>
                <Tag tag={tag} />
            </TableCell>
            <TableCell align="right">{nrMetricsWithTag(report, tag)}</TableCell>
        </TableRowWithDetails>
    )
}
TagRow.propTypes = {
    reload: func.isRequired,
    report: reportPropType,
    tag: string.isRequired,
}

export function Tags({ reload, report }) {
    const tags = getReportTags(report)
    if (tags.length === 0)
        return <InfoMessage title="No tags">None of the metrics in this report have tags.</InfoMessage>
    return (
        <TableContainer>
            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell colSpan={2}>Tag</TableCell>
                        <TableCell align="right">Number of metrics having the tag</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {tags.map((tag) => (
                        <TagRow key={tag} reload={reload} report={report} tag={tag} />
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    )
}
Tags.propTypes = {
    reload: func.isRequired,
    report: reportPropType,
}
