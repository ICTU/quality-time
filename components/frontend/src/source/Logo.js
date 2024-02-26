import { Image } from 'semantic-ui-react';
import { string } from 'prop-types';
import { api_version } from '../api/fetch_server_api';

export function Logo({ alt, logo }) {
    return (
        <Image src={`api/${api_version}/logo/${logo}`} alt={`${alt} logo`} size="mini" spaced="right" />
    )
}
Logo.propTypes = {
    alt: string,
    logo: string,
}
