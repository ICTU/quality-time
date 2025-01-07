import { string } from "prop-types"

export function Logo({ alt, logo, marginBottom, width, height }) {
    return (
        <img
            style={{ marginBottom: marginBottom || "0px", height: height || "32px", width: width || "32px" }}
            src={`api/internal/logo/${logo}`}
            alt={`${alt} logo`}
        />
    )
}
Logo.propTypes = {
    alt: string,
    logo: string,
    marginBottom: string,
    width: string,
    height: string,
}
