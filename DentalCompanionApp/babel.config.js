module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      [
        'module-resolver',
        {
          root: ['./'],
          alias: {
            '@': './',
            '@lib': './lib',
          },
        },
      ],
      'react-native-reanimated/plugin', // last
    ],
  };
};
