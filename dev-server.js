const http = require('http');
const fs = require('fs');
const path = require('path');

// 1. Load environment variables from local .env if present
const envPath = path.join(__dirname, '.env');
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf8');
  envContent.split('\n').forEach(line => {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) return;
    const idx = trimmed.indexOf('=');
    if (idx !== -1) {
      const key = trimmed.slice(0, idx).trim();
      const val = trimmed.slice(idx + 1).trim().replace(/^['"]|['"]$/g, '');
      process.env[key] = val;
    }
  });
  console.log('[Dev Server] Loaded environment variables from .env');
} else {
  console.log('[Dev Server] Tip: Create a .env file with your GMAIL_APP_PASSWORD to test sending emails.');
}

// 2. MIME Types map for static files
const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

const contactHandler = require('./api/contact');

const server = http.createServer(async (req, res) => {
  // Handle API route: /api/contact
  if (req.url === '/api/contact' || req.url.startsWith('/api/contact?')) {
    if (req.method === 'POST') {
      let body = '';
      req.on('data', chunk => { body += chunk; });
      req.on('end', async () => {
        try {
          req.body = body ? JSON.parse(body) : {};
        } catch (e) {
          req.body = {};
        }

        // Add Vercel response helper wrappers
        res.status = (statusCode) => {
          res.statusCode = statusCode;
          return res;
        };
        res.json = (data) => {
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify(data));
          return res;
        };

        try {
          await contactHandler(req, res);
        } catch (err) {
          console.error('[API Error]:', err);
          res.status(500).json({ success: false, message: 'Internal server error.' });
        }
      });
      return;
    } else {
      res.writeHead(405, { 'Content-Type': 'application/json' });
      return res.end(JSON.stringify({ success: false, message: 'Method not allowed. Use POST.' }));
    }
  }

  // Handle Static File Serving
  let reqPath = req.url.split('?')[0];
  if (reqPath === '/' || reqPath === '') {
    reqPath = '/index.html';
  }

  const filePath = path.join(__dirname, reqPath);

  // Security: prevent directory traversal
  if (!filePath.startsWith(__dirname)) {
    res.writeHead(403);
    return res.end('Forbidden');
  }

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      return res.end('404 Not Found');
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';

    res.writeHead(200, { 'Content-Type': contentType });
    fs.createReadStream(filePath).pipe(res);
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`\n=================================================`);
  console.log(`🚀 Portfolio Dev Server running at:`);
  console.log(`👉 http://localhost:${PORT}`);
  console.log(`📧 Contact API active at: http://localhost:${PORT}/api/contact`);
  console.log(`=================================================\n`);
});

