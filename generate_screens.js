// Selenium in py didn't work, but puppeteer did, so here is some terrible JS :D

const puppeteer = require('puppeteer');

const websites = [
    'https://gijs6.nl',
    'https://ckv.gijs6.nl',
    'https://school.gijs6.nl',
    'https://gijs6.nl/blog'
];

async function takeScreenshot(url) {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    await page.setViewport({ width: 1280, height: 720 });

    await page.goto(url, { waitUntil: 'networkidle0' });

    const filename = url.replace(/https?:\/\//, '').replace(/\//g, '_') + '.png';

    await page.screenshot({ path: `./static/projectimages/${filename}` });
    console.log(`Screenshot saved for ${url} as ${filename}`);

    await browser.close();
}

(async () => {
    for (let url of websites) {
        await takeScreenshot(url);
    }
})();
