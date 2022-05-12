import express from "express";
import puppeteer from "puppeteer";
import { sanitizeUrl } from "@braintree/sanitize-url";

const app = express();
const RENDERER_PORT = process.env.RENDERER_PORT || 9000;
const PROXY = `${process.env.PROXY_HOST || 'www'}:${process.env.PROXY_PORT || 80}`;

app.get("/api/health", async (_req, res) => {
    res.status(200).send("OK")
})

app.get("/api/render", async (req, res) => {
    try {
        const url = sanitizeUrl(`http://${PROXY}/${req.query.path}`);
        const browser = await puppeteer.launch({
            defaultViewport: { width: 1200, height: 800 },
            args: ['--disable-dev-shm-usage', '--no-sandbox'],
            headless: true,
        });
        const webPage = await browser.newPage();
        await webPage.goto(url, {
            waitUntil: "networkidle2",
            timeout: 60000
        });
        const pdf = await webPage.pdf({
            printBackground: true,
            format: "A4",
            timeout: 60000,
            scale: 0.7,
            margin: {
                top: "25px",
                bottom: "25px",
                left: "25px",
                right: "25px"
            }
        });
        await browser.close();
        res.contentType("application/pdf");
        res.send(pdf);
    } catch (error) {
        console.error(error)
        res.sendStatus(500)
    }
})

app.listen(RENDERER_PORT, () => {
    console.log(`Renderer started on port ${RENDERER_PORT}. Using proxy ${PROXY}`);
});
