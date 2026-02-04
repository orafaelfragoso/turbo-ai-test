import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output mode for containerized deployments
  output: 'standalone',
  
  // Configure environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
};

export default nextConfig;
