import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    // Cloud.gov containers can report more host CPUs than their memory supports.
    cpus: 2,
    authInterrupts: true,
  },
};

export default nextConfig;
