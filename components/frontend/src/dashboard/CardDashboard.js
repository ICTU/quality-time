import React, { useState } from 'react';
import { Segment } from 'semantic-ui-react';
import RGL, { WidthProvider } from "react-grid-layout";
import { ReadOnlyContext } from '../context/ReadOnly';

const ReactGridLayout = WidthProvider(RGL);

function card_divs(cards, cols, isDragging, card_width = 4, card_height = 6) {
    let divs = [];
    cards.forEach(
        (card, index) => divs.push(
            <div
                onClickCapture={(e) => { if (isDragging(e)) { e.stopPropagation() } }}
                key={card.key}
                data-grid={
                    {
                        i: card.key,
                        x: (card_width * index) % cols,
                        y: card_height * Math.trunc((card_width * index) / cols),
                        w: card_width,
                        h: card_height,
                        isResizable: false
                    }
                }
            >
                {card}
            </div>)
    );
    return divs;
}

export function CardDashboard({ cards, initial_layout, save_layout }) {
    const [dragging, setDragging] = useState(false);
    const [mousePos, setMousePos] = useState([0, 0, 0]);
    const [layout, setLayout] = useState(initial_layout);
    if (cards.length === 0) { return null }
    function onLayoutChange(new_layout) {
        if (JSON.stringify(new_layout) !== JSON.stringify(layout)) {
            setLayout(new_layout);
            save_layout(new_layout)
        }
    }
    function onDragStart(current_layout, oldItem, newItem, placeholder, event) {
        setDragging(true);
        const now = new Date();
        setMousePos([event.clientX, event.clientY, now.getTime()]);
    }
    function onDragStop(current_layout, oldItem, newItem, placeholder, event) {
        setTimeout(() => setDragging(false), 200);  // User was dragging, prevent click event propagation
    }
    function isDragging(event) {
        const now = new Date();
        const distanceX = Math.abs(event.clientX - mousePos[0]);
        const distanceY = Math.abs(event.clientY - mousePos[1]);
        const timedelta = now.getTime() - mousePos[2];
        return (distanceX > 10 || distanceY > 10 || timedelta > 250) ? dragging : false;
    }
    const cols = 32;
    const divs = card_divs(cards, cols, isDragging);
    return (
        <Segment>
            <ReadOnlyContext.Consumer>{(readOnly) => (
                <ReactGridLayout
                    cols={cols}
                    compactType={null}
                    isDraggable={!readOnly}
                    layout={layout}
                    onDragStart={onDragStart}
                    onDragStop={onDragStop}
                    onLayoutChange={onLayoutChange}
                    preventCollision={true}
                    rowHeight={24}
                >
                    {divs}
                </ReactGridLayout>)}
            </ReadOnlyContext.Consumer>
        </Segment>
    )
}
