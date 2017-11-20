const path = require('path'),
    webpack = require('webpack');

const staticPrefix = 'galaxy/static/',
    distPath = path.join(__dirname, staticPrefix, 'dist');

module.exports = {
    context: path.join(__dirname, staticPrefix),
    entry: './js/vendor.js',
    output: {
        filename: 'vendor.js',
        path: distPath
    },
    devtool: 'cheap-source-map',
    plugins: [
        new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/)
    ]
};
