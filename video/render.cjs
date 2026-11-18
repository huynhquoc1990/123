// Render index.html frame-by-frame to MP4.
// Usage:
//   node render.cjs                      -> out/qa_gas_iot_gateway.mp4 (with music)
//   node render.cjs --stills 3,15,45     -> out/still_<t>.png previews
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const FPS = 30;
const WORKERS = Number(process.env.WORKERS || 3);
const ROOT = __dirname;
const OUT = path.join(ROOT, 'out');
fs.mkdirSync(OUT, { recursive: true });

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(ROOT, 'index.html'));
  await page.waitForFunction(() => window.READY === true);
  return page;
}

async function renderChunk(browser, f0, f1, file) {
  const page = await openPage(browser);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(FPS), file], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = f0; f < f1; f++) {
    await page.evaluate(t => window.render(t), f / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - f0) % 150 === 0) console.log(`[${path.basename(file)}] ${f - f0}/${f1 - f0}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await page.close();
}

(async () => {
  const browser = await chromium.launch();
  const args = process.argv.slice(2);
  if (args[0] === '--stills') {
    const page = await openPage(browser);
    for (const t of args[1].split(',').map(Number)) {
      await page.evaluate(t => window.render(t), t);
      await page.screenshot({ path: path.join(OUT, `still_${t}.png`) });
    }
    await browser.close();
    return;
  }
  const page = await openPage(browser);
  const dur = await page.evaluate(() => window.DURATION);
  await page.close();
  const total = Math.round(dur * FPS);
  const per = Math.ceil(total / WORKERS);
  const parts = [];
  const jobs = [];
  for (let i = 0; i < WORKERS; i++) {
    const f0 = i * per, f1 = Math.min(total, (i + 1) * per);
    if (f0 >= f1) break;
    const file = path.join(OUT, `part${i}.mp4`);
    parts.push(file);
    jobs.push(renderChunk(browser, f0, f1, file));
  }
  await Promise.all(jobs);
  await browser.close();

  const list = path.join(OUT, 'parts.txt');
  fs.writeFileSync(list, parts.map(p => `file '${p}'`).join('\n'));
  const silent = path.join(OUT, 'video_silent.mp4');
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', silent]);

  const music = path.join(OUT, 'music.wav');
  if (!fs.existsSync(music)) execFileSync('python3', [path.join(ROOT, 'music.py'), music, String(dur)], { stdio: 'inherit' });
  const final = path.join(OUT, 'qa_gas_iot_gateway.mp4');
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', silent, '-i', music, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
    '-shortest', '-movflags', '+faststart', final]);
  for (const p of [...parts, list, silent]) fs.unlinkSync(p);
  console.log('Done ->', final);
})();
