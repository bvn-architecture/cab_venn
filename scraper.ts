require("dotenv").config();

const playwright = require("playwright");
const { /*chromium,*/ devices } = require("playwright");
const iPhone = devices["iPad (gen 7) landscape"];

const spawn = require("child_process").spawn;

(async () => {
  const my_chromium = playwright["chromium"];
  const browser = await my_chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: iPhone.viewport,
    userAgent: iPhone.userAgent
  });
  const page = await context.newPage();

  //   const client = await browser.pageTarget(page).createCDPSession();
  //   await client.send("Page.setDownloadBehavior", {
  //     behavior: "allow",
  //     downloadPath: "."
  //   });

  await page.setDefaultTimeout(90 * 1000);

  await page.goto("https://plus.cabcharge.com.au/");
  await page.click(".login__button");
  await page.type("[name=email]", process.env.USERNAME);
  await page.type("[name=password]", process.env.PASSWORD);
  await page.click(
    "#auth0-lock-container-1 > div > div.auth0-lock-center > " +
      "form > div > div > div > button"
  );
  await page.waitForNavigation();
  await page.waitForSelector(".travelTable");
  //   await page.screenshot({
  //     path: "screenshot1.png"
  //   });
  console.log("got the travel table");
  await page.waitFor(1000);
  await page.click("button.downloadTripData");
  await page.waitFor(1000);

  await page.click("#simple-menu .downloadTripData");

  //   await page.screenshot({
  //     path: "screenshot2.png"
  //   });
  await page.waitFor(15000);

  // spawn new child process to call the python script
  const python = spawn("python", ["tag_venn_no_download.py"]);
  // collect data from script
  python.stdout.on("data", (data: any) => {
    console.log(`stdout: ${data}`);
  });

  python.stderr.on("data", (data: any) => {
    console.error(`stderr: ${data}`);
  });

  python.on("close", (code: any) => {
    console.log(`child process exited with code ${code}`);
    browser.close();
  });
})();

// error TS1375: 'await' expressions are only allowed at the top level of a file when that file is a module, but this file has no imports or exports. Consider adding an empty 'export {}' to make this file a module.
export {};
