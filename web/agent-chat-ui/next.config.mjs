/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    turbopack: true,
    serverActions: {
      bodySizeLimit: "50mb",
    },
  },
};

export default nextConfig;
