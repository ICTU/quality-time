import { toast } from 'react-toastify';

export function showMessage(type, title, description) {
    const toast_message = title && description ? <><h4>{title}</h4><p>{description}</p></> : title;
    toast(toast_message, { type: type, autoClose: 20000 });
}

export function showConnectionMessage(json) {
    json.availability?.forEach(({ status_code, reason }) => {
        if (status_code === 200) {
            showMessage("success", "URL connection OK")
        } else {
            const status_code_text = status_code >= 0 ? "[HTTP status code " + status_code + "] " : "";
            showMessage("warning", "URL connection error", status_code_text + reason)
        }
    })
}