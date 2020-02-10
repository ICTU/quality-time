import React from 'react';
import { Image, Icon } from 'semantic-ui-react';
import md5 from 'md5';

export function Avatar({ email }) {
    return (
        email ? <Image avatar src={`https://www.gravatar.com/avatar/${md5(email)}?d=identicon`} alt="Avatar" /> : <Icon name="user" />
    )
}