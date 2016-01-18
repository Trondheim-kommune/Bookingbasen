module.exports = function(grunt) {

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        concat: {
            options: {
                separator: '\n'
            },
            dist: {
                src: [
                    "lib/jquery-ui-1.10.3.custom.min.js",
                    "src/TimeSlot.js",
                    "src/TimeSlotView.js",
                    'src/*.js',
                    'src/CalendarViews.js'
                ],
                dest: 'dist/<%= pkg.name %>.js'
            }
        },
        uglify: {
            options: {
                banner: '/*! <%= pkg.name %> <%= grunt.template.today("dd-mm-yyyy") %> */\n'
            },
            dist: {
                files: {
                    'dist/<%= pkg.name %>.min.js': ['<%= concat.dist.dest %>']
                }
            }
        },

        jshint: {
            files: ['gruntfile.js', 'src/**/*.js', 'test/**/*.js'],
            options: {
                // options here to override JSHint defaults
                globals: {
                    jQuery: true,
                    console: true,
                    module: true,
                    document: true
                }
            }
        },
        buster: {
            test: {
                server: {
                    port: 1112
                }
            }
        },
        watch: {
            files: ['<%= jshint.files %>'],
            tasks: ['buster', 'default']
        },
        copy: {
            main: {
                files: [
                    {expand: true, flatten: true, src: '../img/*.png', dest: 'dist/'},
                    {expand: true, flatten: true, src: '../css/flod_calendar.css', dest: 'dist/'},
                    {expand: true, flatten: true, src: '../css/flod_calendar.css', dest: '../../flod_admin_frontend/flod_admin_frontend/static/css/'},
                    {expand: true, flatten: true, src: ['dist/*.js'], dest: '../../flod_frontend/flod_frontend/static/js/lib/'},
                    {expand: true, flatten: true, src: '../css/flod_calendar.css', dest: '../../flod_frontend/flod_frontend/static/css/'},
                    {expand: true, flatten: true, src: ['dist/*.js'], dest: '../../flod_admin_frontend/flod_admin_frontend/static/js/lib/'}
                ]

            },

            images: {
                files: [
                    {expand: true, flatten: true, src: ['../img/*.png'], dest:'../../flod_frontend/flod_frontend/static/images/'},
                    {expand: true, flatten: true, src: ['../img/*.png'], dest:'../../flod_admin_frontend/flod_admin_frontend/static/images/'}
                ]
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-uglify');

    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-buster');


    grunt.registerTask('default', ['concat', 'uglify']);

};
