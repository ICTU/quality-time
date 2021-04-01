
import React from 'react';

export const EDIT_REPORT_PERMISSION = "edit_reports"
export const EDIT_ENTITY_PERMISSION = "edit_entities"

export const ReadOnlyContext = React.createContext(true);

export function ReadOnlyOrEditable({ readOnlyComponent, editableComponent }) {
    return (
      <ReadOnlyContext.Consumer>
        {(readOnly) => (readOnly ? readOnlyComponent : editableComponent)}
      </ReadOnlyContext.Consumer>
    )
}