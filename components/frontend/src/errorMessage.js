import { Grid, Message } from "semantic-ui-react";


export function ErrorMessage({ title, message, formatAsText }) {
    return (
        <Grid.Row>
            <Grid.Column>
                <Message negative>
                    <Message.Header>{title}</Message.Header>
                    {formatAsText ? message : <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>{message}</pre>}
                </Message>
            </Grid.Column>
        </Grid.Row>
    )
}
