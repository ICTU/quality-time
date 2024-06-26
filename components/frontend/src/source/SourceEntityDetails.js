import { func, node, string } from "prop-types"
import { Grid, Header } from "semantic-ui-react"

import { set_source_entity_attribute } from "../api/source"
import { EDIT_ENTITY_PERMISSION } from "../context/Permissions"
import { DateInput } from "../fields/DateInput"
import { SingleChoiceInput } from "../fields/SingleChoiceInput"
import { TextInput } from "../fields/TextInput"
import { entityPropType, entityStatusPropType, reportPropType } from "../sharedPropTypes"
import { capitalize, getDesiredResponseTime } from "../utils"
import { LabelWithDate } from "../widgets/LabelWithDate"
import { source_entity_status_name as status_name } from "./source_entity_status"

function entityStatusOption(status, text, content, subheader) {
    return {
        key: status,
        text: text,
        value: status,
        content: <Header as="h5" content={content} subheader={subheader} />,
    }
}
entityStatusOption.propTypes = {
    status: entityStatusPropType,
    text: string,
    content: node,
    subheader: node,
}

function entityStatusOptions(entityType, report) {
    const unconfirmedSubheader = `This ${entityType} should be reviewed to decide what to do with it.`
    const confirmedSubheader = `This ${entityType} has been reviewed and should be addressed within ${getDesiredResponseTime(report, "confirmed")} days.`
    const fixedSubheader = `Ignore this ${entityType} for ${getDesiredResponseTime(report, "fixed")} days because it has been fixed or will be fixed shortly.`
    const falsePositiveSubheader = `Ignore this "${entityType}" for ${getDesiredResponseTime(report, "false_positive")} days because it has been incorrectly identified as ${entityType}.`
    const wontFixSubheader = `Ignore this ${entityType} for ${getDesiredResponseTime(report, "wont_fix")} days because it will not be fixed.`
    return [
        entityStatusOption("unconfirmed", status_name.unconfirmed, "Unconfirm", unconfirmedSubheader),
        entityStatusOption("confirmed", status_name.confirmed, "Confirm", confirmedSubheader),
        entityStatusOption("fixed", status_name.fixed, "Resolve as fixed", fixedSubheader),
        entityStatusOption(
            "false_positive",
            status_name.false_positive,
            "Resolve as false positive",
            falsePositiveSubheader,
        ),
        entityStatusOption("wont_fix", status_name.wont_fix, "Resolve as won't fix", wontFixSubheader),
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
