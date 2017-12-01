const gulp = require('gulp');
const less = require('gulp-less');
const dest = require('gulp-dest');
const watch = require('gulp-watch');
const uglify = require('gulp-uglify');
const concat = require('gulp-concat');
const rename = require('gulp-rename');
const gutil = require('gulp-util');
const proxy    = require('http-proxy-middleware')
const sync     = require('browser-sync')
const history  = require('connect-history-api-fallback')


gulp.task('server', function() {
    const proxyDjango = proxy('/', {target: 'http://localhost:8888', xfwd: true})

    sync.init({
        notify: false,
        open: false,
        port: 8000,
        server: {
            baseDir: '/galaxy',
            middleware: [proxyDjango, history()]
        }
    });
});

gulp.task('accountApp', function() {
    return gulp.src([
        './galaxy/static/js/accountApp/*.js',
        './galaxy/static/js/commonDirectives/*.js',
        './galaxy/static/js/commonServices/*.js'
    ])
    .pipe(concat('galaxy.accountApp.js'))
    .pipe(uglify({ 'mangle': true, 'compress': true }))
    .pipe(rename({extname: ".min.js"})) 
    .pipe(gulp.dest('./galaxy/static/dist'));
});

gulp.task('detailApp', function() {
    return gulp.src([
        './galaxy/static/js/detailApp/*.js',
        './galaxy/static/js/commonDirectives/*.js',
        './galaxy/static/js/commonServices/*.js'
    ])
    .pipe(concat('galaxy.detailApp.js'))
    .pipe(uglify({ 'mangle': true, 'compress': true }))
    .pipe(rename({extname: ".min.js"})) 
    .pipe(gulp.dest('./galaxy/static/dist'));
});

gulp.task('listApp', function() {
    return gulp.src([
        './galaxy/static/js/listApp/*.js',
        './galaxy/static/js/commonDirectives/*.js',
        './galaxy/static/js/commonServices/*.js'
    ])
    .pipe(concat('galaxy.listApp.js'))
    .pipe(uglify({ 'mangle': true, 'compress': true }))
    .pipe(rename({extname: ".min.js"})) 
    .pipe(gulp.dest('./galaxy/static/dist'));
});

gulp.task('exploreApp', function() {
    return gulp.src([
        './galaxy/static/js/exploreApp/*.js',
        './galaxy/static/js/commonDirectives/*.js',
        './galaxy/static/js/commonServices/*.js'
    ])
    .pipe(concat('galaxy.exploreApp.js'))
    .pipe(uglify({ 'mangle': true, 'compress': true }))
    .pipe(rename({extname: ".min.js"})) 
    .pipe(gulp.dest('./galaxy/static/dist'));
});

gulp.task('importStatusApp', function() {
    return gulp.src([
        './galaxy/static/js/importStatusApp/*.js',
        './galaxy/static/js/commonDirectives/*.js',
        './galaxy/static/js/commonServices/*.js'
    ])
    .pipe(concat('galaxy.importStatusApp.js'))
    .pipe(uglify({ 'mangle': true, 'compress': true }))
    .pipe(rename({extname: ".min.js"})) 
    .pipe(gulp.dest('./galaxy/static/dist'));
});

gulp.task('roleAddApp', function() {
    return gulp.src([
        './galaxy/static/js/roleAddApp/*.js',
        './galaxy/static/js/commonDirectives/*.js',
        './galaxy/static/js/commonServices/*.js'
    ])
    .pipe(concat('galaxy.roleAddApp.js'))
    .pipe(uglify({ 'mangle': true, 'compress': true }))
    .pipe(rename({extname: ".min.js"})) 
    .pipe(gulp.dest('./galaxy/static/dist'));
});

gulp.task('userStarredApp', function() {
    return gulp.src([
        './galaxy/static/js/userStarredApp/*.js',
        './galaxy/static/js/commonDirectives/*.js',
        './galaxy/static/js/commonServices/*.js'
    ])
    .pipe(concat('galaxy.userStarredApp.js'))
    .pipe(uglify({ 'mangle': true, 'compress': true }))
    .pipe(rename({extname: ".min.js"}))
    .pipe(gulp.dest('./galaxy/static/dist'));
});


gulp.task('less', function() {
    return gulp.src(['./galaxy/static/less/galaxy.less'])
        .pipe(less({
            compress: true
        }))
        .on('error', gutil.log)
        .pipe(dest('galaxy/static/css', {ext: '.min.css'}))
        .pipe(gulp.dest('./'));
});

gulp.task('less-watch', ['less'], function (done) {
    sync.reload();
    done();
});

gulp.task('generic-watch', function(done) {
    sync.reload();
    done();
});

gulp.task('watch', function () {
    gulp.watch('./galaxy/static/less/*.less', ['less-watch']);
    gulp.watch('./galaxy/static/js/*/*.js', ['generic-watch']);
    gulp.watch('./galaxy/static/partials/*.html', ['generic-watch']);
});

gulp.task('default', ['less', 'server', 'watch']);
gulp.task('build', ['less', 'accountApp', 'listApp', 'detailApp', 'exploreApp', 'roleAddApp', 'importStatusApp']);
