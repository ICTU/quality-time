import { bool, object, oneOfType, string } from "prop-types"
import { Grid, Message } from "semantic-ui-react"

export function ErrorMessage({ formatAsText, message, title }) {
    return (
        <Grid.Row>
            <Grid.Column>
                <Message negative>
                    <Message.Header>{title}</Message.Header>
                    {formatAsText ? (
                        message
                    ) : (
                        <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-all" }}>
                            {message}
                        </pre>
                    )}
                </Message>
            </Grid.Column>
        </Grid.Row>
    )
}
ErrorMessage.propTypes = {
    formatAsText: bool,
    message: oneOfType([object, string]),
    title: string,
}
