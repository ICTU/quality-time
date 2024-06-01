import { func, objectOf, string } from "prop-types"
import { useContext } from "react"

import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION } from "../context/Permissions"
import { SingleChoiceInput } from "../fields/SingleChoiceInput"
import { Header } from "../semantic_ui_react_wrappers"
import { subjectPropType } from "../sharedPropTypes"

export function subjectTypes(subjectTypesMapping) {
    const options = []
    Object.entries(subjectTypesMapping).forEach(([key, subjectType]) => {
        options.push({
            key: key,
            text: subjectType.name,
            value: key,
            content: <Header as="h4" content={subjectType.name} subheader={subjectType.description} />,
        })
    })
    return options
}
subjectTypes.propTypes = {
    subjectTypesMapping: objectOf(subjectPropType),
}

export function SubjectType({ subjectType, setValue }) {
    return (
        <SingleChoiceInput
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label="Subject type"
            options={subjectTypes(useContext(DataModel).subjects)}
            set_value={(value) => setValue(value)}
            value={subjectType}
        />
    )
}
SubjectType.propTypes = {
    subjectType: string,
    setValue: func,
}
