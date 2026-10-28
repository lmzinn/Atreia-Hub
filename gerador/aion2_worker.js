// Cloudflare Worker for "Meu personagem" on the published site: the official Aion 2 site only answers its own pages,
// so the page asks this Worker, which asks the official site and hands the answer back.
// It passes on only the six read-only addresses below and only answers the pages listed in ORIGINS.
// Setup: Cloudflare dashboard > Workers & Pages > Create > Hello World, paste this file, Deploy,
// then put the Worker address (https://<name>.<account>.workers.dev) in API_REMOTE of gerador/guide_template.html.
const ROUTES = {
  search: 'https://api-search.plaync.com/aion2global/search/v2/character',
  servers: 'https://aion2.plaync.com/en-us/api/gameinfo/servers',
  info: 'https://aion2.plaync.com/api/character/info',
  equipment: 'https://aion2.plaync.com/api/character/equipment',
  item: 'https://aion2.plaync.com/api/character/equipment/item',
  daevanion: 'https://aion2.plaync.com/api/character/daevanion/detail',
};
const ORIGINS = ['https://lmzinn.github.io', 'null'];  // 'null': the page opened as a file
const local = o => /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(o);

export default {
  async fetch(request) {
    const origin = request.headers.get('Origin') || '';
    const allowed = ORIGINS.includes(origin) || local(origin);
    const cors = {'Access-Control-Allow-Origin': allowed ? origin : ORIGINS[0], Vary: 'Origin'};
    if (request.method === 'OPTIONS') return new Response(null, {headers: {...cors, 'Access-Control-Allow-Methods': 'GET'}});
    if (request.method !== 'GET' || !allowed) return new Response('{"error":"not allowed"}', {status: 403, headers: cors});
    const url = new URL(request.url), key = url.pathname.replace(/^\/(aion2\/)?/, '');
    if (!ROUTES[key]) return new Response('{"error":"unknown route"}', {status: 404, headers: cors});
    const answer = await fetch(ROUTES[key] + url.search, {headers: {'User-Agent': 'Mozilla/5.0', Accept: 'application/json'},
      cf: {cacheTtl: key === 'servers' ? 86400 : 60}});
    return new Response(answer.body, {status: answer.status,
      headers: {...cors, 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store'}});
  },
};
