import React, { useContext } from 'react';
import { Image, Icon } from 'semantic-ui-react';
import md5 from 'md5';
import { DarkMode } from '../context/DarkMode';

export function Avatar({ email }) {
    const color = useContext(DarkMode) ? "grey" : null;
    return (
        email ? <Image avatar src={`https://www.gravatar.com/avatar/${md5(email)}?d=identicon`} alt="Avatar" /> : <Icon color={color} name="user" />
    )
}
