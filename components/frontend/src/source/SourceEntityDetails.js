import { func, node, oneOf, string } from "prop-types"
import { Grid, Header } from "semantic-ui-react"

import { set_source_entity_attribute } from "../api/source"
import { EDIT_ENTITY_PERMISSION } from "../context/Permissions"
import { DateInput } from "../fields/DateInput"
import { SingleChoiceInput } from "../fields/SingleChoiceInput"
import { TextInput } from "../fields/TextInput"
import { entityPropType, entityStatusPropType, reportPropType } from "../sharedPropTypes"
import { capitalize, getDesiredResponseTime } from "../utils"
import { LabelWithDate } from "../widgets/LabelWithDate"
import { SOURCE_ENTITY_STATUS_ACTION, SOURCE_ENTITY_STATUS_NAME } from "./source_entity_status"

function entityStatusOption(status, subheader) {
    return {
        key: status,
        text: SOURCE_ENTITY_STATUS_NAME[status],
        value: status,
        content: <Header as="h5" content={SOURCE_ENTITY_STATUS_ACTION[status]} subheader={subheader} />,
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
    metric_uuid,
    name,
    rationale,
    reload,
    report,
    status,
    status_end_date,
    source_uuid,
}) {
    return (
        <Grid stackable>
            <Grid.Row>
                <Grid.Column width={4}>
                    <SingleChoiceInput
                        requiredPermissions={[EDIT_ENTITY_PERMISSION]}
                        label={`${capitalize(name)} status`}
                        options={entityStatusOptions(name, report)}
                        set_value={(value) =>
                            set_source_entity_attribute(metric_uuid, source_uuid, entity.key, "status", value, reload)
                        }
                        value={status}
                        sort={false}
                    />
                </Grid.Column>
                <Grid.Column width={4}>
                    <DateInput
                        requiredPermissions={[EDIT_ENTITY_PERMISSION]}
                        label={
                            <LabelWithDate
                                date={status_end_date}
                                labelId={entity.key}
                                label={`${capitalize(name)} status end date`}
                                help={`Consider the status of this ${name} to be 'Unconfirmed' after the selected date.`}
                            />
                        }
                        placeholder="YYYY-MM-DD"
                        set_value={(value) =>
                            set_source_entity_attribute(
                                metric_uuid,
                                source_uuid,
                                entity.key,
                                "status_end_date",
                                value,
                                reload,
                            )
                        }
                        value={status_end_date}
                    />
                </Grid.Column>
                <Grid.Column width={8}>
                    <TextInput
                        requiredPermissions={[EDIT_ENTITY_PERMISSION]}
                        label={`${capitalize(name)} status rationale`}
                        placeholder={`Rationale for the ${name} status...`}
                        rows={Math.min(5, rationale?.split("\n").length ?? 1)}
                        set_value={(value) =>
                            set_source_entity_attribute(
                                metric_uuid,
                                source_uuid,
                                entity.key,
                                "rationale",
                                value,
                                reload,
                            )
                        }
                        value={rationale}
                    />
                </Grid.Column>
            </Grid.Row>
        </Grid>
    )
}
SourceEntityDetails.propTypes = {
    entity: entityPropType,
    metric_uuid: string,
    name: string,
    rationale: string,
    reload: func,
    report: reportPropType,
    status: entityStatusPropType,
    status_end_date: string,
    source_uuid: string,
}
