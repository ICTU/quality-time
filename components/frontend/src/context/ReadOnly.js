
import React from 'react';

export const EDIT_REPORT_PERMISSION = "edit_reports"
export const EDIT_ENTITY_PERMISSION = "edit_entities"

export const ReadOnlyContext = React.createContext(true);

export function ReadOnlyOrEditable({ requiredPermissions, readOnlyComponent, editableComponent }) {

    function editable(permissions) {
        return requiredPermissions.every(permission => permissions.includes(permission))
    };

    return (
      <ReadOnlyContext.Consumer>
        {(permissions) => (editable(permissions) ? editableComponent : readOnlyComponent)}
      </ReadOnlyContext.Consumer>
    )
}