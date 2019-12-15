
import React from 'react';

export const ReadOnlyContext = React.createContext(true);

export function ReadOnlyOrEditable({ readOnlyComponent, editableComponent }) {
    return (
      <ReadOnlyContext.Consumer>
        {(readOnly) => (readOnly ? readOnlyComponent : editableComponent)}
      </ReadOnlyContext.Consumer>
    )
}