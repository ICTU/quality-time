import { string } from "prop-types"
import { Image } from "semantic-ui-react"

export function Logo({ alt, logo }) {
    return <Image src={`api/internal/logo/${logo}`} alt={`${alt} logo`} size="mini" spaced="right" />
}
Logo.propTypes = {
    alt: string,
    logo: string,
}
