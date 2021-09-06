import { Grid, Message } from "semantic-ui-react";


export function ErrorMessage({ title, message }) {
    return (
        <Grid.Row>
            <Grid.Column>
                <Message negative>
                    <Message.Header>{title}</Message.Header>
                    <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>{message}</pre>
                </Message>
            </Grid.Column>
        </Grid.Row>
    )
}
