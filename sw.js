const CACHE_NAME='aroha-core-v1';
const APP_SHELL_ASSETS=['./','./index.html','./manifest.json','./tarot.html','./astro.html','./domains.html','./maramataka.js','./aroha_master_matrix_app.html'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE_NAME).then(c=>c.addAll(APP_SHELL_ASSETS)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(keys=>Promise.all(keys.map(k=>{if(k!==CACHE_NAME)return caches.delete(k)}))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;e.respondWith(caches.match(e.request).then(cached=>{if(cached)return cached;return fetch(e.request).then(net=>{if(!net||net.status!==200||(net.type!=='basic'&&net.type!=='cors'))return net;const clone=net.clone();caches.open(CACHE_NAME).then(c=>c.put(e.request,clone));return net}).catch(()=>{if(e.request.mode==='navigate')return caches.match('./index.html')})}))});
