PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'
PIPELINE_TEMPLATE_NAMESPACE = 'window.TPL'
PIPELINE_TEMPLATE_FUNC = 'Mustache.compile'
PIPELINE_TEMPLATE_EXT = '.mustache'
PIPELINE_DISABLE_WRAPPER = True
# TODO: add CSS handling
# PIPELINE_CSS = {    
# }

PIPELINE_JS = {
    'all_libs': {   # all non-base libraries
        'source_filenames': (
            'js/libs/underscore.js',
            'js/libs/mustache.js',
        ),
        'output_filename': 'js/libs.js',
    },
    'site_scripts': {
        'source_filenames': (
            'js/scripts/feed.js',
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
