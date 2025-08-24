// Learn more https://docs.expo.dev/guides/customizing-metro/
const path = require('path');
const { getDefaultConfig } = require('expo/metro-config');

/** @type {import('expo/metro-config').MetroConfig} */
const config = getDefaultConfig(__dirname);

// Add path aliases so runtime (Metro) resolves them like TypeScript does
config.resolver = config.resolver || {};
config.resolver.alias = {
  ...(config.resolver.alias || {}),
  '@': __dirname,
  '@lib': path.resolve(__dirname, 'lib'),
};

module.exports = config;
