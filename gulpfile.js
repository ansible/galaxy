var gulp = require('gulp');
var less = require('gulp-less');
var dest = require('gulp-dest');

gulp.task('less', function() {
    return gulp.src(['./galaxy/static/less/*.less'])
        .pipe(less({
            compress: true
        }))
        .pipe(dest('galaxy/static/css', {ext: '.min.css'}))
        .pipe(gulp.dest('./'));
});
