// Minimal Ruishu browser-environment observation proxy.
// Use as the default mod.js starting point. Keep this small.

function createProxy(name, target) {
    return new Proxy(target || {}, {
        get(obj, prop, receiver) {
            const value = Reflect.get(obj, prop, receiver);
            console.log('[rs-proxy:get]', name, String(prop), typeof value);
            return value;
        },
        set(obj, prop, value, receiver) {
            console.log('[rs-proxy:set]', name, String(prop), typeof value);
            return Reflect.set(obj, prop, value, receiver);
        },
        apply(fn, thisArg, args) {
            console.log('[rs-proxy:apply]', name, args);
            return Reflect.apply(fn, thisArg, args);
        }
    });
}

function ensureObject(path, fallback) {
    const parts = path.split('.');
    let root = globalThis;
    for (let i = 0; i < parts.length - 1; i++) {
        const key = parts[i];
        if (!root[key]) root[key] = {};
        root = root[key];
    }
    const leaf = parts[parts.length - 1];
    if (!root[leaf]) root[leaf] = fallback || {};
    root[leaf] = createProxy(path, root[leaf]);
}

globalThis.window = globalThis.window || globalThis;
globalThis.self = globalThis.self || globalThis.window;
globalThis.navigator = globalThis.navigator || {
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    platform: 'Win32',
    language: 'zh-CN',
    languages: ['zh-CN', 'zh'],
    webdriver: false
};
globalThis.location = globalThis.location || {
    href: 'https://example.com/',
    origin: 'https://example.com',
    protocol: 'https:',
    host: 'example.com',
    hostname: 'example.com',
    port: '',
    pathname: '/',
    search: '',
    hash: ''
};
globalThis.document = globalThis.document || {};

let cookieValue = '';
Object.defineProperty(globalThis.document, 'cookie', {
    configurable: true,
    get() {
        console.log('[rs-proxy:get]', 'document.cookie', cookieValue);
        return cookieValue;
    },
    set(value) {
        console.log('[rs-proxy:set]', 'document.cookie', value);
        const part = String(value).split(';')[0];
        const name = part.split('=')[0];
        const pieces = cookieValue ? cookieValue.split('; ').filter(item => item.split('=')[0] !== name) : [];
        pieces.push(part);
        cookieValue = pieces.join('; ');
    }
});

globalThis.document.createElement = globalThis.document.createElement || function createElement(tagName) {
    console.log('[rs-proxy:call]', 'document.createElement', tagName);
    if (String(tagName).toLowerCase() === 'a') {
        const anchor = {};
        Object.defineProperty(anchor, 'href', {
            configurable: true,
            get() { return this._href || ''; },
            set(value) {
                const parsed = new URL(String(value), globalThis.location.href);
                this._href = parsed.href;
                this.protocol = parsed.protocol;
                this.host = parsed.host;
                this.hostname = parsed.hostname;
                this.port = parsed.port;
                this.pathname = parsed.pathname;
                this.search = parsed.search;
                this.hash = parsed.hash;
                this.origin = parsed.origin;
            }
        });
        return anchor;
    }
    return { tagName: String(tagName).toUpperCase(), style: {}, children: [] };
};

globalThis.document.getElementById = globalThis.document.getElementById || function getElementById(id) {
    console.log('[rs-proxy:call]', 'document.getElementById', id);
    return null;
};
globalThis.document.appendChild = globalThis.document.appendChild || function appendChild(node) { return node; };
globalThis.document.removeChild = globalThis.document.removeChild || function removeChild(node) { return node; };

ensureObject('navigator', globalThis.navigator);
ensureObject('location', globalThis.location);
ensureObject('document', globalThis.document);
