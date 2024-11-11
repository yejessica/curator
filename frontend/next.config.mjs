/** @type {import('next').NextConfig} */
// const nextConfig = {};

// export default nextConfig;

// next.config.mjs
export default {
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: 'http://localhost:5000/:path*', // Proxy to Flask server
            },
        ];
    },
    reactStrictMode: true,
    experimental: {
        appDir: true, // Enable the App Router if not already enabled
    },
};

