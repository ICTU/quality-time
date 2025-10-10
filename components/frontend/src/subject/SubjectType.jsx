import CircleIcon from "@mui/icons-material/Circle"
import { MenuItem, Stack, Typography } from "@mui/material"
import { func, number, objectOf, string } from "prop-types"
import { useContext } from "react"

import { DataModel } from "../context/DataModel"
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { TextField } from "../fields/TextField"
import { subjectPropType } from "../sharedPropTypes"
import { getSubjectType, referenceDocumentationURL } from "../utils"
import { ReadTheDocsLink } from "../widgets/ReadTheDocsLink"

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
                    <Stack direction="column" sx={{ whiteSpace: "normal" }}>
                        {subjectType.name}
                        <Typography variant="body2">{subjectType.description}</Typography>
                    </Stack>
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
    const dataModel = useContext(DataModel)
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const subjectTypeName = getSubjectType(subjectType, dataModel.subjects).name
    return (
        <TextField
            disabled={disabled}
            helperText={<ReadTheDocsLink url={referenceDocumentationURL(subjectTypeName)} />}
            label="Subject type"
            onChange={(value) => setValue(value)}
            select
            value={subjectType}
        >
            {subjectTypes(dataModel.subjects).map((subjectType) => (
                <MenuItem key={subjectType.key} value={subjectType.value}>
                    {subjectType.content}
                </MenuItem>
            ))}
        </TextField>
    )
}
SubjectType.propTypes = {
    subjectType: string,
    setValue: func,
}
