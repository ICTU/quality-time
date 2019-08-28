import React from 'react';
import { Input } from './Input';

export function PasswordInput(props) {
    return (
        <Input
            {...props}
            autoComplete="new-password"
            type="password"
        />
    )
}