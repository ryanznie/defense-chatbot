/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    // API URL for the FastAPI backend
    BACKEND_URL: 'http://localhost:8000',
  },
}

module.exports = nextConfig
