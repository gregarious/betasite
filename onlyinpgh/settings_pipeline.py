PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'
PIPELINE_TEMPLATE_NAMESPACE = 'window.TPL'
PIPELINE_TEMPLATE_FUNC = 'Handlebars.compile'
PIPELINE_TEMPLATE_EXT = '.html'
PIPELINE_DISABLE_WRAPPER = True
# TODO: add CSS handling
# PIPELINE_CSS = {}

PIPELINE_JS = {
    'all_libs': {   # all non-base libraries
        'source_filenames': (
            'js/libs/underscore.js',
            'js/libs/backbone.js',
            'js/libs/handlebars-1.0.0.beta.6.js',
        ),
        'output_filename': 'js/libs.js',
    },
    'jquery_ui': {
        'source_filenames': (
            # soon will build custom jquery ui packages here, but need to look how  this will effect css
            'js/libs/jquery-ui/ui/jquery-ui-1.8.18.custom.min.js',
            'js/libs/jquery-ui/plugins/*',
        ),
        'output_filename': 'js/jquery-ui-custom.js',
    },
    'site_scripts': {
        'source_filenames': (
            'js/scripts/feed.js',
            'js/scripts/map.js',
            'js/scripts/misc.js',
        ),
        'output_filename': 'js/scenable.js'
    },
    'templates': {
        'source_filenames': (
            'js/templates/*',
        ),
        'output_filename': 'js/templates.js',
    },
}
