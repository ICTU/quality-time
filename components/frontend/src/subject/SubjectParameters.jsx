import Grid from "@mui/material/Grid"
import { func, string } from "prop-types"
import { useContext } from "react"

import { set_subject_attribute } from "../api/subject"
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { CommentField } from "../fields/CommentField"
import { TextField } from "../fields/TextField"
import { subjectPropType } from "../sharedPropTypes"
import { SubjectType } from "./SubjectType"

export function SubjectParameters({ subject, subject_uuid, subject_name, reload }) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    return (
        <Grid container spacing={{ xs: 1, sm: 1, md: 2 }} columns={{ xs: 1, sm: 1, md: 3 }}>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <SubjectType
                    id={`${subject_uuid}-type`}
                    setValue={(value) => set_subject_attribute(subject_uuid, "type", value, reload)}
                    subjectType={subject.type}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={disabled}
                    id={`${subject_uuid}-title`}
                    label="Subject title"
                    placeholder={subject_name}
                    onChange={(value) => set_subject_attribute(subject_uuid, "name", value, reload)}
                    value={subject.name}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={disabled}
                    id={`${subject_uuid}-subtitle`}
                    label="Subject subtitle"
                    onChange={(value) => set_subject_attribute(subject_uuid, "subtitle", value, reload)}
                    value={subject.subtitle}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 3 }}>
                <CommentField
                    disabled={disabled}
                    id={`${subject_uuid}-comment`}
                    onChange={(value) => set_subject_attribute(subject_uuid, "comment", value, reload)}
                    value={subject.comment}
                />
            </Grid>
        </Grid>
    )
}
SubjectParameters.propTypes = {
    subject: subjectPropType,
    subject_uuid: string,
    subject_name: string,
    reload: func,
}
