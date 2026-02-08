import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable strict mode for better development experience
  reactStrictMode: true,

  // Enable standalone output for Docker deployment
  output: "standalone",

  // Disable linting and type checking during build for Docker
  // (These should be run in CI/CD before building)
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
