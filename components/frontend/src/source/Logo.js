import React from 'react';
import { Image } from 'semantic-ui-react';
import { api_version } from '../api/fetch_server_api';

export function Logo(props) {
    return (
        <Image src={`api/${api_version}/logo/${props.logo}`} alt={`${props.alt} logo`} size="mini" spaced="right" />
    )
}