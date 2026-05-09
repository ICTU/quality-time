import request from "supertest"
import { expect, it, vi } from "vitest"

import { app } from "./index.js"

const pdf = new Uint16Array(42)

const page = {
    addStyleTag: async () => {},
    goto: async () => {},
    pdf: async () => {
        return pdf.buffer
    },
    waitForSelector: async () => {},
}

const mockBrowser = {
    connected: true,
    newPage: async () => page,
}

vi.mock("puppeteer-core", () => ({
    default: {
        launch: async () => mockBrowser,
    },
}))

it("reports healthy", async () => {
    mockBrowser.connected = true
    const res = await request(app).get("/api/health")
    expect(res.status).toBe(200)
    expect(res.text).toBe("OK")
})

it("reports unhealthy", async () => {
    mockBrowser.connected = undefined
    const res = await request(app).get("/api/health")
    expect(res.status).toBe(503)
    expect(res.text).toBe("Chromium not connected")
})

it("renders a PDF", async () => {
    const consoleMock = vi.spyOn(console, "log").mockImplementation(() => undefined)
    mockBrowser.connected = true
    const res = await request(app).get("/api/render")
    expect(res.status).toBe(200)
    expect(res.get("Content-Type")).toBe("application/pdf")
    expect(consoleMock).toHaveBeenCalledWith("URL http://www:80/undefined: opened")
    expect(consoleMock).toHaveBeenCalledWith(
        "URL http://www:80/undefined: loader hidden, measurement entities loaded, and animations finished",
    )
    expect(consoleMock).toHaveBeenCalledWith("URL http://www:80/undefined: PDF created")
})

it("returns 500 on error", async () => {
    vi.spyOn(console, "error").mockImplementation(() => undefined)
    mockBrowser.connected = true
    page.goto = async () => {
        throw new Error("no such page")
    }
    const res = await request(app).get("/api/render")
    expect(res.status).toBe(500)
    expect(res.get("Content-Type")).toBe("text/plain; charset=utf-8")
})
