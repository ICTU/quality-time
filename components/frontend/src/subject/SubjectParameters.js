import { func, string } from "prop-types"
import { Grid } from "semantic-ui-react"

import { set_subject_attribute } from "../api/subject"
import { EDIT_REPORT_PERMISSION } from "../context/Permissions"
import { Comment } from "../fields/Comment"
import { StringInput } from "../fields/StringInput"
import { subjectPropType } from "../sharedPropTypes"
import { SubjectType } from "./SubjectType"

export function SubjectParameters({ subject, subject_uuid, subject_name, reload }) {
    return (
        <Grid stackable>
            <Grid.Row columns={3}>
                <Grid.Column>
                    <SubjectType
                        id={`${subject_uuid}-type`}
                        setValue={(value) => set_subject_attribute(subject_uuid, "type", value, reload)}
                        subjectType={subject.type}
                    />
                </Grid.Column>
                <Grid.Column>
                    <StringInput
                        id={`${subject_uuid}-title`}
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label="Subject title"
                        placeholder={subject_name}
                        set_value={(value) => set_subject_attribute(subject_uuid, "name", value, reload)}
                        value={subject.name}
                    />
                </Grid.Column>
                <Grid.Column>
                    <StringInput
                        id={`${subject_uuid}-subtitle`}
                        label="Subject subtitle"
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        set_value={(value) => set_subject_attribute(subject_uuid, "subtitle", value, reload)}
                        value={subject.subtitle}
                    />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row>
                <Grid.Column>
                    <Comment
                        id={`${subject_uuid}-comment`}
                        set_value={(value) => set_subject_attribute(subject_uuid, "comment", value, reload)}
                        value={subject.comment}
                    />
                </Grid.Column>
            </Grid.Row>
        </Grid>
    )
}
SubjectParameters.propTypes = {
    subject: subjectPropType,
    subject_uuid: string,
    subject_name: string,
    reload: func,
}
