// Render index.html frame-by-frame to MP4.
// Usage:
//   python3 build_voice.py               -> voiceover + timing.js (optional)
//   node render.cjs                      -> out/he_thong_cap_phat_nhien_lieu.mp4 (music + voice)
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
  const timing = path.join(ROOT, 'timing.js');
  execFileSync('python3', [path.join(ROOT, 'music.py'), music, String(dur), ...(fs.existsSync(timing) ? [timing] : [])], { stdio: 'inherit' });
  const voice = path.join(OUT, 'voice.wav');
  const final = path.join(OUT, 'he_thong_cap_phat_nhien_lieu.mp4');
  const audio = fs.existsSync(voice)
    ? ['-i', music, '-i', voice, '-filter_complex',
       '[2:a]highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=90,volume=1.25,asplit=2[vo][sc];' +
       '[1:a]volume=0.42[m];[m][sc]sidechaincompress=threshold=0.02:ratio=6:attack=15:release=450[duck];' +
       '[duck][vo]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-15:TP=-1.5:LRA=11,aresample=44100[a]', '-map', '0:v', '-map', '[a]']
    : ['-i', music];
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', silent, ...audio, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
    '-shortest', '-movflags', '+faststart', final]);
  for (const p of [...parts, list, silent]) fs.unlinkSync(p);
  console.log('Done ->', final);
})();
