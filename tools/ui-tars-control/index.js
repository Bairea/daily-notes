/**
 * UI-TARS NutJS 电脑控制 CLI。
 *
 * 作为 UI-TARS-desktop 项目的 NutJSOperator 的 CLI 封装，
 * 提供 screenshot / click / scroll / type / press 等基础操作，
 * 替代 TRAE 自带的 mcp_Computer_Use MCP 服务。
 *
 * 用法:
 *   node index.js screenshot [--out path.jpg]
 *   node index.js click --x 100 --y 200 [--button left|middle|right]
 *   node index.js scroll --direction up|down [--pages 1] [--x 500 --y 400]
 *   node index.js type --text "hello"
 *   node index.js press --key "enter"
 *   node index.js mouse-info             # 打印当前鼠标位置
 *   node index.js screen-info            # 打印屏幕分辨率
 */
const fs = require('fs');
const path = require('path');
const os = require('os');
const { NutJSOperator } = require('@ui-tars/operator-nut-js');

const operator = new NutJSOperator();

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const key = a.slice(2);
      const val = argv[i + 1];
      if (val === undefined || val.startsWith('--')) {
        args[key] = true;
      } else {
        args[key] = val;
        i++;
      }
    } else {
      args._.push(a);
    }
  }
  return args;
}

async function ensureScreenshotDir() {
  const dir = path.join(os.tmpdir(), 'ui-tars-screenshots');
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

async function main() {
  const args = parseArgs(process.argv);
  const cmd = args._[0] || 'help';

  switch (cmd) {
    case 'screenshot': {
      const { base64, scaleFactor } = await operator.screenshot();
      const dir = await ensureScreenshotDir();
      const outPath =
        args.out ||
        path.join(dir, `screenshot-${Date.now()}-${Math.round(Math.random() * 10000)}.jpg`);
      const buf = Buffer.from(base64, 'base64');
      fs.writeFileSync(outPath, buf);
      console.log(JSON.stringify({
        ok: true,
        file: outPath,
        uri: 'file:///' + outPath.replace(/\\/g, '/'),
        scaleFactor,
      }, null, 2));
      break;
    }

    case 'click': {
      const x = Number(args.x);
      const y = Number(args.y);
      const button = args.button || 'left';
      if (!Number.isFinite(x) || !Number.isFinite(y)) {
        console.error(JSON.stringify({ ok: false, error: '--x and --y are required (numbers)' }));
        process.exit(1);
      }
      const prediction = `click(start_box="(${x},${y})", mouse_button="${button}")`;
      const result = await operator.execute({
        prediction,
        parsedPrediction: {
          action_type: 'click',
          action_inputs: {
            start_box: `(${x},${y})`,
            start_coords: [x, y],
            mouse_button: button,
          },
          reflection: null,
          thought: '',
        },
        screenWidth: 0,
        screenHeight: 0,
        scaleFactor: 1,
        factors: [1, 1],
      });
      console.log(JSON.stringify({ ok: true, x, y, button, result }, null, 2));
      break;
    }

    case 'scroll': {
      const direction = args.direction || 'down';
      const pages = Number(args.pages || 1);
      const x = args.x ? Number(args.x) : undefined;
      const y = args.y ? Number(args.y) : undefined;
      if (!['up', 'down', 'left', 'right'].includes(direction)) {
        console.error(JSON.stringify({ ok: false, error: '--direction must be up|down|left|right' }));
        process.exit(1);
      }
      const prediction = `scroll(direction="${direction}", pages=${pages})`;
      const result = await operator.execute({
        prediction,
        parsedPrediction: {
          action_type: 'scroll',
          action_inputs: { direction, pages, start_coords: [x, y] },
          reflection: null,
          thought: '',
        },
        screenWidth: 0,
        screenHeight: 0,
        scaleFactor: 1,
        factors: [1, 1],
      });
      console.log(JSON.stringify({ ok: true, direction, pages, result }, null, 2));
      break;
    }

    case 'type': {
      const text = args.text || '';
      if (text === '' && !args.text) {
        console.error(JSON.stringify({ ok: false, error: '--text is required' }));
        process.exit(1);
      }
      const prediction = `type(content="${text}")`;
      const result = await operator.execute({
        prediction,
        parsedPrediction: {
          action_type: 'type',
          action_inputs: { content: text },
          reflection: null,
          thought: '',
        },
        screenWidth: 0,
        screenHeight: 0,
        scaleFactor: 1,
        factors: [1, 1],
      });
      console.log(JSON.stringify({ ok: true, length: text.length, result }, null, 2));
      break;
    }

    case 'press': {
      const key = args.key;
      if (!key) {
        console.error(JSON.stringify({ ok: false, error: '--key is required (e.g. enter, ctrl, space)' }));
        process.exit(1);
      }
      const prediction = `hotkey(key="${key}")`;
      const result = await operator.execute({
        prediction,
        parsedPrediction: {
          action_type: 'hotkey',
          action_inputs: { keys: [key] },
          reflection: null,
          thought: '',
        },
        screenWidth: 0,
        screenHeight: 0,
        scaleFactor: 1,
        factors: [1, 1],
      });
      console.log(JSON.stringify({ ok: true, key, result }, null, 2));
      break;
    }

    case 'mouse-info': {
      try {
        const { mouse } = require('@nut-tree/nut-js');
        const pos = await mouse.getPosition();
        console.log(JSON.stringify({ ok: true, x: pos.x, y: pos.y }, null, 2));
      } catch (e) {
        console.log(JSON.stringify({ ok: false, error: e.message }, null, 2));
      }
      break;
    }

    case 'screen-info': {
      try {
        const { screen } = require('@nut-tree/nut-js');
        const w = screen.width();
        const h = screen.height();
        console.log(JSON.stringify({ ok: true, width: w, height: h }, null, 2));
      } catch (e) {
        console.log(JSON.stringify({ ok: false, error: e.message }, null, 2));
      }
      break;
    }

    case 'help':
    default:
      console.log(`UI-TARS NutJS Computer Control CLI

Usage:
  node index.js screenshot [--out <path>]      Capture screen, save JPG, print JSON with file path
  node index.js click --x <num> --y <num> [--button left|middle|right]  Click at coordinates
  node index.js scroll --direction up|down|left|right [--pages 1] [--x X --y Y]  Scroll at/by coords
  node index.js type --text "<string>"         Type text at current cursor
  node index.js press --key "<keyname>"        Press a single key / hotkey component
  node index.js mouse-info                     Print current mouse position
  node index.js screen-info                    Print screen resolution
  node index.js help                           Show this message
`);
  }
}

main().catch((e) => {
  console.error(JSON.stringify({ ok: false, error: String(e), stack: e.stack }, null, 2));
  process.exit(1);
});
