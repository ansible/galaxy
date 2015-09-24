var gulp = require('gulp');
var less = require('gulp-less');
var dest = require('gulp-dest');
var watch = require('gulp-watch');
var uglify = require('gulp-uglify');
var concat = require('gulp-concat');
var rename = require('gulp-rename');
 
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

gulp.task('less', function() {
    return gulp.src(['./galaxy/static/less/galaxy.less'])
        .pipe(less({
            compress: true
        }))
        .pipe(dest('galaxy/static/css', {ext: '.min.css'}))
        .pipe(gulp.dest('./'));
});

gulp.task('watch', function () {
    gulp.watch('./galaxy/static/less/*.less',['less']);
});

gulp.task('default', ['less','watch']);
gulp.task('build', ['less', 'accountApp', 'listApp', 'detailApp', 'exploreApp']);
