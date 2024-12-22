import CircleIcon from "@mui/icons-material/Circle"
import { Stack, Typography } from "@mui/material"
import { func, number, objectOf, string } from "prop-types"
import { useContext } from "react"

import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION } from "../context/Permissions"
import { SingleChoiceInput } from "../fields/SingleChoiceInput"
import { subjectPropType } from "../sharedPropTypes"

export function subjectTypes(subjectTypesMapping, level = 0) {
    const options = []
    const bullet =
        level === 0 ? null : (
            <CircleIcon
                fontSize="inherit"
                sx={{
                    color: "inherit",
                    width: "0.5em",
                    marginRight: "0.5em",
                    paddingTop: "0.3em",
                }}
            />
        )
    Object.entries(subjectTypesMapping).forEach(([key, subjectType]) => {
        options.push({
            key: key,
            text: subjectType.name,
            value: key,
            content: (
                <Stack direction="row">
                    {bullet}
                    <p>
                        {subjectType.name}
                        <Typography variant="body2">{subjectType.description}</Typography>
                    </p>
                </Stack>
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
