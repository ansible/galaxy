const path = require('path'),
    webpack = require('webpack');

const staticPrefix = 'galaxy/static/',
    distPath = path.join(__dirname, staticPrefix, 'dist');

var entry = {
    vendor: ['./js/vendor.js'],
    accountApp: ['./js/accountApp.js']
};

module.exports = {
    context: path.join(__dirname, staticPrefix),
    entry: entry,
    output: {
        filename: '[name].js',
        path: distPath
    },
    devtool: 'cheap-source-map',
    plugins: [
        new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/)
    ]
};
