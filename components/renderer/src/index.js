import express from "express";
import { Buffer } from "node:buffer";
import puppeteer from "puppeteer-core";
import { sanitizeUrl } from "@braintree/sanitize-url";

const app = express();
app.disable("x-powered-by");
const RENDERER_PORT = process.env.RENDERER_PORT || 9000;
const PROXY = `${process.env.PROXY_HOST || "www"}:${process.env.PROXY_PORT || 80}`;
const PROTOCOL = process.env.PROXY_PROTOCOL || "http";
let browser;

app.get("/api/health", async (_req, res) => {
    // This endpoint is used by the Docker health check command (that in turn uses src/healthcheck.cjs) to report the
    // health of the renderer component
    const healthy = browser.connected ?? false;
    res.status(healthy ? 200 : 503).send(healthy ? "OK" : "Chromium not connected");
});

app.get("/api/render", async (req, res) => {
    let webPage;
    try {
        const url = sanitizeUrl(`${PROTOCOL}://${PROXY}/${req.query.path}`);
        webPage = await browser.newPage();
        await webPage.goto(url, {
            waitUntil: "networkidle2",
            timeout: 60000,
        });
        console.log(`URL ${url}: opened`);
        await webPage.addStyleTag({ content: ".MuiPaper-elevation: {-webkit-filter: blur(0);}" }); // Fix box shadows
        await webPage.waitForSelector(".MuiCircularProgress-root", { hidden: true }); // Initial loader
        await webPage.waitForSelector(".MuiSkeleton-root", { hidden: true }); // Measurement entities placeholder
        await webPage.waitForSelector("#dashboard.animated");
        console.log(`URL ${url}: loader hidden, measurement entities loaded, and animations finished`);
        const pdf = Buffer.from(
            await webPage.pdf({
                printBackground: true,
                format: "A4",
                timeout: 60000,
                scale: 0.5, // With scale 0.5 the dashboard fits exactly. Larger scale makes the dashboard too wide.
                margin: {
                    top: "25px",
                    bottom: "25px",
                    left: "25px",
                    right: "25px",
                },
            }),
        );
        console.log(`URL ${url}: PDF created`);
        res.contentType("application/pdf");
        res.send(pdf);
    } catch (error) {
        console.error(error);
        res.sendStatus(500);
    } finally {
        await webPage.close();
    }
});

app.listen(RENDERER_PORT, async () => {
    try {
        browser = await puppeteer.launch({
            executablePath: "/usr/bin/chromium-browser",
            defaultViewport: { width: 1500, height: 1000 },
            args: ["--disable-dev-shm-usage", "--no-sandbox"],
            // Opt in to new Chrome headless implementation, see https://developer.chrome.com/articles/new-headless/:
            headless: "new",
        });
        console.log(`Renderer started on port ${RENDERER_PORT}. Using proxy ${PROXY}`);
    } catch (error) {
        console.log(error);
    }
});
