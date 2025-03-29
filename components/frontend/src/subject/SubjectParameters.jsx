import Grid from "@mui/material/Grid"
import { func, string } from "prop-types"
import { useContext } from "react"

import { setSubjectAttribute } from "../api/subject"
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { CommentField } from "../fields/CommentField"
import { TextField } from "../fields/TextField"
import { subjectPropType } from "../sharedPropTypes"
import { SubjectType } from "./SubjectType"

export function SubjectParameters({ subject, subjectUuid, subjectName, reload }) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    return (
        <Grid container spacing={{ xs: 1, sm: 1, md: 2 }} columns={{ xs: 1, sm: 1, md: 3 }}>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <SubjectType
                    id={`${subjectUuid}-type`}
                    setValue={(value) => setSubjectAttribute(subjectUuid, "type", value, reload)}
                    subjectType={subject.type}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={disabled}
                    id={`${subjectUuid}-title`}
                    label="Subject title"
                    placeholder={subjectName}
                    onChange={(value) => setSubjectAttribute(subjectUuid, "name", value, reload)}
                    value={subject.name}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={disabled}
                    id={`${subjectUuid}-subtitle`}
                    label="Subject subtitle"
                    onChange={(value) => setSubjectAttribute(subjectUuid, "subtitle", value, reload)}
                    value={subject.subtitle}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 3 }}>
                <CommentField
                    disabled={disabled}
                    id={`${subjectUuid}-comment`}
                    onChange={(value) => setSubjectAttribute(subjectUuid, "comment", value, reload)}
                    value={subject.comment}
                />
            </Grid>
        </Grid>
    )
}
SubjectParameters.propTypes = {
    subject: subjectPropType,
    subjectUuid: string,
    subjectName: string,
    reload: func,
}
