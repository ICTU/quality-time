import { useContext } from "react"
import { Message as SemanticUIMessage } from "semantic-ui-react"

import { DarkMode } from "../context/DarkMode"
import { addInvertedClassNameWhenInDarkMode } from "./dark_mode"

export function Message(props) {
    return <SemanticUIMessage {...addInvertedClassNameWhenInDarkMode(props, useContext(DarkMode))} />
}

Message.Content = SemanticUIMessage.Content
Message.Header = SemanticUIMessage.Header
Message.Item = SemanticUIMessage.Item
Message.List = SemanticUIMessage.List
