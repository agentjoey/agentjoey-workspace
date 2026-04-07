/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable static export for optimal performance
  // Remove this if you need SSR features
  output: 'export',
  distDir: 'dist',
  
  // Image optimization for static export
  images: {
    unoptimized: true,
  },
  
  // Monorepo support
  transpilePackages: ['@repo/ui', '@repo/utils', '@repo/hooks'],
};

export default nextConfig;
