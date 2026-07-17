import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  images: {
    formats: ["image/webp"],
    qualities: [75, 80, 82, 85, 90],
    minimumCacheTTL: 86400,
  },
};

export default nextConfig;
