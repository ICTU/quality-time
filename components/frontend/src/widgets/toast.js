import { Icon } from 'semantic-ui-react';
import { toast } from 'react-toastify';

export function show_message(type, title, description, icon) {
    const toast_type = {"success": toast.TYPE.SUCCESS, "warning": toast.TYPE.WARNING, "error": toast.TYPE.ERROR, "info": toast.TYPE.INFO}[type];
    const toast_icon = icon ? icon : {"success": "thumbs up", "warning": "warning circle", "error": "close", "info": "info circle"}[type];
    toast(<><h4><Icon name={toast_icon}/>{title}</h4><p>{description}</p></>, {type: toast_type, autoClose: 20000});
}

export function show_connection_messages(json) {
    json.availability?.forEach(({status_code, reason}) => {
        if (status_code === 200) {
            show_message("success", "URL connection OK")
        } else {
            const status_code_text = status_code >= 0 ? "[HTTP status code " + status_code + "] " : "";
            show_message("warning", "URL connection error", status_code_text + reason)
        }
    })
}