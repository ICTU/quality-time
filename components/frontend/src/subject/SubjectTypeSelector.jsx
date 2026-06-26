import CircleIcon from "@mui/icons-material/Circle"
import { Stack, Typography } from "@mui/material"
import { func, number, objectOf, string } from "prop-types"
import { useContext } from "react"

import { DataModelContext } from "../context/DataModel"
import { accessGranted, EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import { subjectPropType } from "../sharedPropTypes"
import { getSubjectType, referenceDocumentationURL } from "../utils"
import { ItemTypeSelector } from "../widgets/ItemTypeSelector"
import { ItemTypeSelectorTextField } from "../widgets/ItemTypeSelectorTextField"
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
        options.push(
            {
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
            },
            ...subjectTypes(subjectType?.subjects ?? [], level + 1),
        )
    })
    return options
}
subjectTypes.propTypes = {
    subjectTypesMapping: objectOf(subjectPropType),
    level: number,
}

export function SubjectTypeSelector({ subjectType, setValue }) {
    const dataModel = useContext(DataModelContext)
    const permissions = useContext(PermissionsContext)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const subjectTypeName = getSubjectType(subjectType, dataModel.subjects).name
    return (
        <ItemTypeSelector
            itemSubtypes={subjectTypes(dataModel.subjects)}
            itemType="subject"
            onClick={(value) => setValue(value)}
            renderAnchor={(handleMenu) => (
                <ItemTypeSelectorTextField
                    disabled={disabled}
                    handleMenu={handleMenu}
                    helperText={<ReadTheDocsLink url={referenceDocumentationURL(subjectTypeName)} />}
                    label="Subject type"
                    value={subjectTypeName}
                />
            )}
            sort={false}
        />
    )
}
SubjectTypeSelector.propTypes = {
    subjectType: string,
    setValue: func,
}
