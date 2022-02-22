import React, { useContext } from 'react';
import { Image, Icon } from 'semantic-ui-react';
import md5 from 'md5';
import { DarkMode } from '../context/DarkMode';

export function Avatar({ email }) {
    const darkMode = useContext(DarkMode)
    return (
        email ? <Image avatar src={`https://www.gravatar.com/avatar/${md5(email)}?d=identicon`} alt="Avatar" /> : <Icon color={darkMode ? "grey": null} name="user" />
    )
}