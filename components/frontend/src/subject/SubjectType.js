import { func, string } from "prop-types"
import { useContext } from "react"

import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION } from "../context/Permissions"
import { SingleChoiceInput } from "../fields/SingleChoiceInput"
import { Header } from "../semantic_ui_react_wrappers"
import { dataModelPropType } from "../sharedPropTypes"

export function subjectTypes(dataModel) {
    const options = []
    Object.entries(dataModel.subjects).forEach(([key, subjectType]) => {
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
    dataModel: dataModelPropType,
}

export function SubjectType({ subjectType, setValue }) {
    return (
        <SingleChoiceInput
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label="Subject type"
            options={subjectTypes(useContext(DataModel))}
            set_value={(value) => setValue(value)}
            value={subjectType}
        />
    )
}
SubjectType.propTypes = {
    subjectType: string,
    setValue: func,
}
