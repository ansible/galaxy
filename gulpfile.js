var gulp = require('gulp');
var less = require('gulp-less');
var dest = require('gulp-dest');
var watch = require('gulp-watch');

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
