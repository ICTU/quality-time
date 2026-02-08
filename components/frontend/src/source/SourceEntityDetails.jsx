import { MenuItem } from "@mui/material"
import Grid from "@mui/material/Grid"
import { DatePicker } from "@mui/x-date-pickers"
import dayjs from "dayjs"
import { func, node, oneOf, string } from "prop-types"
import { useContext } from "react"

import { setSourceEntityAttribute } from "../api/source"
import { accessGranted, EDIT_ENTITY_PERMISSION, Permissions } from "../context/Permissions"
import { TextField } from "../fields/TextField"
import { entityPropType, entityStatusPropType, reportPropType } from "../sharedPropTypes"
import { capitalize, getDesiredResponseTime } from "../utils"
import { Header } from "../widgets/Header"
import { SOURCE_ENTITY_STATUS_ACTION, SOURCE_ENTITY_STATUS_NAME } from "./source_entity_status"

function entityStatusOption(status, subheader) {
    return {
        key: status,
        text: SOURCE_ENTITY_STATUS_NAME[status],
        value: status,
        content: <Header level="h4" header={SOURCE_ENTITY_STATUS_ACTION[status]} subheader={subheader} />,
    }
}
entityStatusOption.propTypes = {
    status: entityStatusPropType,
    subheader: node,
}

function responseTimeClause(report, status, prefix = "for") {
    const responseTime = getDesiredResponseTime(report, status)
    return responseTime === null ? "" : ` ${prefix} ${responseTime} days`
}
responseTimeClause.propTypes = {
    status: entityStatusPropType,
    report: reportPropType,
    prefix: oneOf(["for", "within"]),
}

function entityStatusOptions(entityType, report) {
    return [
        entityStatusOption(
            "unconfirmed",
            `This ${entityType} should be reviewed in order to decide what to do with it.`,
        ),
        entityStatusOption(
            "confirmed",
            `This ${entityType} has been reviewed and should be addressed${responseTimeClause(report, "confirmed", "within")}.`,
        ),
        entityStatusOption(
            "fixed",
            `Ignore this ${entityType}${responseTimeClause(report, "fixed")} because it has been fixed or will be fixed shortly.`,
        ),
        entityStatusOption(
            "false_positive",
            // If the user marks then entity status as false positive, apparently the entity type is incorrect,
            // hence the false positive option has quotes around the entity type:
            `Ignore this "${entityType}"${responseTimeClause(report, "false_positive")} because it has been incorrectly identified as ${entityType}.`,
        ),
        entityStatusOption(
            "wont_fix",
            `Ignore this ${entityType}${responseTimeClause(report, "wont_fix")} because it will not be fixed.`,
        ),
    ]
}
entityStatusOptions.propTypes = {
    entityType: string,
    report: reportPropType,
}

export function SourceEntityDetails({
    entity,
    metricUuid,
    name,
    rationale,
    reload,
    report,
    status,
    statusEndDate,
    sourceUuid,
}) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_ENTITY_PERMISSION])
    return (
        <Grid container spacing={{ xs: 1, sm: 2, md: 2 }} columns={{ xs: 4, sm: 8, md: 12 }} sx={{ margin: "10px" }}>
            <Grid size={{ xs: 1, sm: 2, md: 3 }}>
                <TextField
                    disabled={disabled}
                    label={`${capitalize(name)} status`}
                    onChange={(value) =>
                        setSourceEntityAttribute(metricUuid, sourceUuid, entity.key, "status", value, reload)
                    }
                    select
                    value={status}
                >
                    {entityStatusOptions(name, report).map((option) => (
                        <MenuItem key={option.key} value={option.value}>
                            {option.content}
                        </MenuItem>
                    ))}
                </TextField>
            </Grid>
            <Grid size={{ xs: 1, sm: 2, md: 3 }}>
                <DatePicker
                    defaultValue={statusEndDate ? dayjs(statusEndDate) : null}
                    disabled={disabled}
                    label={`${capitalize(name)} status end date`}
                    onChange={(value) =>
                        setSourceEntityAttribute(metricUuid, sourceUuid, entity.key, "status_end_date", value, reload)
                    }
                    slotProps={{
                        field: { clearable: true },
                        textField: {
                            helperText: `Consider the status of this ${name} to be 'Unconfirmed' after the selected date.`,
                        },
                    }}
                    sx={{ width: "100%" }}
                    timezone="default"
                />
            </Grid>
            <Grid size={{ xs: 2, sm: 4, md: 6 }}>
                <TextField
                    disabled={disabled}
                    id={`${entity.key}-rationale`}
                    label={`${capitalize(name)} status rationale`}
                    multiline
                    onChange={(value) =>
                        setSourceEntityAttribute(metricUuid, sourceUuid, entity.key, "rationale", value, reload)
                    }
                    value={rationale}
                />
            </Grid>
        </Grid>
    )
}
SourceEntityDetails.propTypes = {
    entity: entityPropType,
    metricUuid: string,
    name: string,
    rationale: string,
    reload: func,
    report: reportPropType,
    status: entityStatusPropType,
    statusEndDate: string,
    sourceUuid: string,
}
