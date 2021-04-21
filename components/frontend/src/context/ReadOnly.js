
import React from 'react';

export const EDIT_REPORT_PERMISSION = "edit_reports"
export const EDIT_ENTITY_PERMISSION = "edit_entities"

export const ReadOnlyContext = React.createContext(null);

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
      <ReadOnlyContext.Consumer>
        {(permissions) => (accessGranted(permissions, requiredPermissions) ? editableComponent : readOnlyComponent)}
      </ReadOnlyContext.Consumer>
    )
}
