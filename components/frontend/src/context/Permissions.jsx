import { element } from "prop-types"
import React from "react"

import { permissionsPropType } from "../sharedPropTypes"

export const EDIT_REPORT_PERMISSION = "edit_reports"
export const EDIT_ENTITY_PERMISSION = "edit_entities"
export const PERMISSIONS = [EDIT_REPORT_PERMISSION, EDIT_ENTITY_PERMISSION]

export const Permissions = React.createContext(null)

export function accessGranted(permissions, requiredPermissions) {
    if (typeof requiredPermissions !== typeof []) {
        return false
    }
    if (requiredPermissions.length === 0) {
        return true
    }
    if ((permissions ?? []).length === 0) {
        return false
    }
    return requiredPermissions.every((permission) => permissions.includes(permission))
}
accessGranted.propTypes = {
    permissions: permissionsPropType,
    requiredPermissions: permissionsPropType,
}

export function ReadOnlyOrEditable({ requiredPermissions, readOnlyComponent, editableComponent }) {
    return (
        <Permissions.Consumer>
            {(permissions) => (accessGranted(permissions, requiredPermissions) ? editableComponent : readOnlyComponent)}
        </Permissions.Consumer>
    )
}
ReadOnlyOrEditable.propTypes = {
    requiredPermissions: permissionsPropType,
    readOnlyComponent: element,
    editableComponent: element,
}
