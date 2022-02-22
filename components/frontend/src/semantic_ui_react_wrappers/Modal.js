import React, { useContext } from 'react';
import { Modal as SemanticUIModal } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';
import './Modal.css';

export function Modal(props) {
    return (
        <SemanticUIModal className={useContext(DarkMode) ? "inverted" : ""} {...props} />
    )
}

Modal.Content = SemanticUIModal.Content
Modal.Header = SemanticUIModal.Header
