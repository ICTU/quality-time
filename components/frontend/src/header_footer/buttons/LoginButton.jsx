import PersonIcon from "@mui/icons-material/Person"
import {
    Alert,
    AlertTitle,
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Stack,
    TextField,
} from "@mui/material"
import { func } from "prop-types"
import { useState } from "react"

import { login } from "../../api/auth"

export function LoginButton({ setUser }) {
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState("")
    const [open, setOpen] = useState(false)

    function closeDialog() {
        setOpen(false)
        setError("")
    }

    function submit() {
        login(username, password)
            .then(function (json) {
                if (json.ok) {
                    setUser(username, json.email, new Date(Date.parse(json.session_expiration_datetime)))
                } else {
                    setError("credentials")
                }
                return null
            })
            .catch(function (_error) {
                setError("connection")
            })
    }

    let alertTitle = "Heads up"
    let alertContent =
        "Changes you make after you log in, such as adding metrics, changing metric targets, and marking issues as false positive, are logged."
    if (error === "connection") {
        alertTitle = "Connection error"
        alertContent = "Can't reach the server. Please check your connection."
    }
    if (error === "credentials") {
        alertTitle = "Invalid credentials"
        alertContent = "Username and/or password are invalid. Please try again."
    }
    return (
        <>
            <Button color="inherit" onClick={() => setOpen(true)}>
                <PersonIcon />
                Login
            </Button>
            <Dialog onClose={() => closeDialog()} open={open}>
                <DialogTitle>Login</DialogTitle>
                <DialogContent>
                    <Stack spacing={2} padding={1}>
                        <TextField
                            autoFocus
                            id="username"
                            label="Username"
                            name="username"
                            onChange={(event) => setUsername(event.target.value)}
                        />
                        <TextField
                            id="password"
                            name="password"
                            type="password"
                            label="Password"
                            onChange={(event) => setPassword(event.target.value)}
                        />
                        <Alert severity={error ? "error" : "warning"}>
                            <AlertTitle>{alertTitle}</AlertTitle>
                            {alertContent}
                        </Alert>
                    </Stack>
                </DialogContent>
                <DialogActions>
                    <Button name="cancel" onClick={() => closeDialog()} color="secondary">
                        Cancel
                    </Button>
                    <Button name="submit" onClick={() => submit()}>
                        Submit
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    )
}
LoginButton.propTypes = {
    setUser: func,
}
