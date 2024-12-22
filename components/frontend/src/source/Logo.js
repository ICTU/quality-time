import { string } from "prop-types"

export function Logo({ alt, logo }) {
    return <img src={`api/internal/logo/${logo}`} alt={`${alt} logo`} width="32px" height="32px" />
}
Logo.propTypes = {
    alt: string,
    logo: string,
}
