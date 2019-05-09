import React from 'react';
import { Card, Segment } from 'semantic-ui-react';

export function CardDashboard(props) {
    const big_cards_per_row = Math.min(Math.max(props.big_cards.length, 5), 7);
    const small_cards_per_row = Math.min(Math.max(props.small_cards.length, 8), 10);
    return (
        <Segment>
            <Card.Group doubling stackable itemsPerRow={big_cards_per_row}>
                {props.big_cards}
            </Card.Group>
            <Card.Group doubling stackable itemsPerRow={small_cards_per_row}>
                {props.small_cards}
            </Card.Group>
        </Segment>
    );
}
