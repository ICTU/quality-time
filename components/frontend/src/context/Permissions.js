
import React from 'react';

export const EDIT_REPORT_PERMISSION = "edit_reports"
export const EDIT_ENTITY_PERMISSION = "edit_entities"
export const PERMISSIONS = [EDIT_REPORT_PERMISSION, EDIT_ENTITY_PERMISSION]

export const Permissions = React.createContext(null);

export function accessGranted(permissions, requiredPermissions) {
  if (!requiredPermissions) {
    return true
  }
  if (!permissions) {
    return false
  }
  return requiredPermissions.every(permission => permissions.includes(permission))
}

export function ReadOnlyOrEditable({ requiredPermissions, readOnlyComponent, editableComponent }) {
    return (
      <Permissions.Consumer>
        {(permissions) => ( accessGranted(permissions, requiredPermissions) ? editableComponent : readOnlyComponent)}
      </Permissions.Consumer>
    )
}
