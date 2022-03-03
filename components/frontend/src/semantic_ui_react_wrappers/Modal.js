import React, { useContext } from 'react';
import { Modal as SemanticUIModal } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';
import { addInvertedClassNameWhenInDarkMode } from './dark_mode';
import './Modal.css';

export function Modal(props) {
    return (
        <SemanticUIModal {...addInvertedClassNameWhenInDarkMode(props, useContext(DarkMode))} />
    )
}

Modal.Content = SemanticUIModal.Content
Modal.Header = SemanticUIModal.Header
