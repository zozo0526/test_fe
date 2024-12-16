module.exports = {
  presets: [
    ['@babel/preset-env', {
      targets: {
        ie: '11'
      }
    }],
    '@vue/cli-plugin-babel/preset'
  ]
}
