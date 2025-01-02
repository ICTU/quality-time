import Grid from "@mui/material/Grid2"
import { func, string } from "prop-types"

import { set_metric_attribute, set_metric_debt } from "../api/metric"
import { EDIT_REPORT_PERMISSION } from "../context/Permissions"
import { Comment } from "../fields/Comment"
import { DateInput } from "../fields/DateInput"
import { SingleChoiceInput } from "../fields/SingleChoiceInput"
import { IssuesRows } from "../issue/IssuesRows"
import { metricPropType, reportPropType } from "../sharedPropTypes"
import { LabelWithDate } from "../widgets/LabelWithDate"
import { LabelWithHyperLink } from "../widgets/LabelWithHyperLink"
import { Target } from "./Target"

function AcceptTechnicalDebt({ metric, metric_uuid, reload }) {
    const labelId = `accept-debt-label-${metric_uuid}`
    return (
        <SingleChoiceInput
            aria-labelledby={labelId}
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label={
                <LabelWithHyperLink
                    labelId={labelId}
                    label="Accept technical debt?"
                    url="https://en.wikipedia.org/wiki/Technical_debt"
                />
            }
            value={metric.accept_debt ? "yes" : "no"}
            options={[
                { key: "yes", text: "Yes", value: "yes" },
                {
                    key: "yes_completely",
                    text: "Yes, and also set technical debt target and end date",
                    value: "yes_completely",
                },
                { key: "no", text: "No", value: "no" },
                {
                    key: "no_completely",
                    text: "No, and also clear technical debt target and end date",
                    value: "no_completely",
                },
            ]}
            set_value={(value) => {
                const acceptDebt = value.startsWith("yes")
                if (value.endsWith("completely")) {
                    set_metric_debt(metric_uuid, acceptDebt, reload)
                } else {
                    set_metric_attribute(metric_uuid, "accept_debt", acceptDebt, reload)
                }
            }}
        />
    )
}
AcceptTechnicalDebt.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
}

function TechnicalDebtEndDate({ metric, metric_uuid, reload }) {
    const labelId = `technical-debt-end-date-label-${metric_uuid}`
    const help = (
        <>
            <p>Accept technical debt until this date.</p>
            <p>
                After this date, or when the issues below have all been resolved, whichever happens first, the technical
                debt should be resolved and the technical debt target is no longer evaluated.
            </p>
        </>
    )
    let debtEndDateTime = null
    if (metric.debt_end_date) {
        debtEndDateTime = new Date(metric.debt_end_date)
        debtEndDateTime.setHours(23, 59, 59)
    }
    return (
        <DateInput
            ariaLabelledBy={labelId}
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label={
                <LabelWithDate date={debtEndDateTime} labelId={labelId} help={help} label="Technical debt end date" />
            }
            placeholder="YYYY-MM-DD"
            set_value={(value) => set_metric_attribute(metric_uuid, "debt_end_date", value, reload)}
            value={metric.debt_end_date ?? ""}
        />
    )
}
TechnicalDebtEndDate.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
}

export function MetricDebtParameters({ metric, metric_uuid, reload, report }) {
    return (
        <Grid alignItems="flex-end" container spacing={{ xs: 1, sm: 1, md: 2 }} columns={{ xs: 1, sm: 3, md: 6 }}>
            <Grid size={{ xs: 1, sm: 1, md: 2 }}>
                <AcceptTechnicalDebt metric={metric} metric_uuid={metric_uuid} reload={reload} />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 2 }}>
                <Target
                    key={metric.debt_target}
                    label="Technical debt target"
                    target_type="debt_target"
                    metric={metric}
                    metric_uuid={metric_uuid}
                    reload={reload}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 2 }}>
                <TechnicalDebtEndDate metric={metric} metric_uuid={metric_uuid} reload={reload} />
            </Grid>
            <IssuesRows metric={metric} metric_uuid={metric_uuid} reload={reload} report={report} />
            <Grid size={{ xs: 1, sm: 3, md: 6 }}>
                <Comment
                    set_value={(value) => set_metric_attribute(metric_uuid, "comment", value, reload)}
                    value={metric.comment}
                />
            </Grid>
        </Grid>
    )
}
MetricDebtParameters.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
    report: reportPropType,
}
