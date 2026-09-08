import type { NextConfig } from "next";

const backendOrigin = (process.env.API_INTERNAL_URL ?? "http://localhost:8000/api").replace(
  /\/api$/,
  "",
);

const nextConfig: NextConfig = {
  output: "standalone",
  images: {
    formats: ["image/webp"],
    qualities: [75, 80, 82, 85, 90],
    minimumCacheTTL: 86400,
  },
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${backendOrigin}/api/:path*` },
      { source: "/media/:path*", destination: `${backendOrigin}/media/:path*` },
    ];
  },
};

export default nextConfig;
