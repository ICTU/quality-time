import { func, number, objectOf, string } from "prop-types"
import { useContext } from "react"
import { HeaderContent, HeaderSubheader } from "semantic-ui-react"

import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION } from "../context/Permissions"
import { SingleChoiceInput } from "../fields/SingleChoiceInput"
import { Header, Icon } from "../semantic_ui_react_wrappers"
import { subjectPropType } from "../sharedPropTypes"

export function subjectTypes(subjectTypesMapping, level = 0) {
    const options = []
    const headingLevel = `h${Math.min(level, 2) + 4}` // Ensure the heading level is at least h4 and at most h6
    const bullet = level === 0 ? null : <Icon name="circle" size="tiny" style={{ paddingLeft: `${level}em` }} />
    Object.entries(subjectTypesMapping).forEach(([key, subjectType]) => {
        options.push({
            key: key,
            text: subjectType.name,
            value: key,
            content: (
                <Header as={headingLevel}>
                    {bullet}
                    <HeaderContent>
                        {subjectType.name}
                        <HeaderSubheader>{subjectType.description}</HeaderSubheader>
                    </HeaderContent>
                </Header>
            ),
        })
        options.push(...subjectTypes(subjectType?.subjects ?? [], level + 1))
    })
    return options
}
subjectTypes.propTypes = {
    subjectTypesMapping: objectOf(subjectPropType),
    level: number,
}

export function SubjectType({ subjectType, setValue }) {
    return (
        <SingleChoiceInput
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label="Subject type"
            options={subjectTypes(useContext(DataModel).subjects)}
            set_value={(value) => setValue(value)}
            sort={false}
            value={subjectType}
        />
    )
}
SubjectType.propTypes = {
    subjectType: string,
    setValue: func,
}
