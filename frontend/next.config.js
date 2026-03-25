/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // In production, frontend calls the API directly via NEXT_PUBLIC_API_URL
    // In development, proxy /api/* to the local backend
    if (process.env.NEXT_PUBLIC_API_URL) {
      return [];
    }
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || '',
  },
};

module.exports = nextConfig;
