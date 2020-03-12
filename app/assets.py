from flask_assets import Environment, Bundle

datatable = Bundle(
    'datatables/jquery.dataTables.min.css',
    'css/jquery.dataTables.min.css',
    'datatables/extensions/Buttons/css/buttons.dataTables.min.css',
    filters='cssmin',
    output='css/data_table.min.css')

css_base = Bundle('css/main.css',
                  'css/bootstrap-select.css',
                  'css/jquery-confirm.min.css',
                  'css/variety.css',
                  datatable,
                  filters='cssmin',
                  output='css/all.min.css')

css_cover = Bundle('css/bootstrap.css',
                   'css/carousel.css',
                   'css/main.css',
                   filters='cssmin',
                   output='css/cover.min.css')

css_auth = Bundle('css/bootstrap.css',
                  'css/auth_base.css',
                  'css/main.css',
                  filters='cssmin',
                  output='css/auth.min.css')

css_fancybox = Bundle('fancybox/jquery.fancybox.css',
                      'fancybox/fancybox.css',
                      filters='cssmin',
                      output='css/fancybox.min.css')

js_comment = Bundle('js/jquery.min.js',
                    'js/bootstrap.min.js',
                    'js/jquery-confirm.min.js',
                    filters='jsmin',
                    output='js/comment.min.js')

js_datatable = Bundle('datatables/extensions/Buttons/js/*.js',
                      filters='jsmin',
                      output='js/data_table.min.js')

js_fancybox = Bundle('fancybox/jquery.fancybox.js',
                     'fancybox/jquery.fancybox.pack.js',
                     'js/jquery.albumSlider.min.js',
                     'fancybox/jquery.mousewheel-3.0.6.pack.js',
                     filters='jsmin',
                     output='js/fancybox.min.js')

js_base = Bundle(js_comment,
                 'datatables/jquery.dataTables.min.js',
                 'js/bootstrap-select.js',
                 'js/multiselect.min.js',
                 'js/main.js',
                 'js/layer/layer.js',
                 js_datatable,
                 filters='jsmin',
                 output='js/all.min.js')


def init_app(app):
    webassets = Environment(app)
    webassets.register('css_cover', css_cover)
    webassets.register('css_auth', css_auth)
    webassets.register('css_fancybox', css_fancybox)
    webassets.register('css_all', css_base)
    webassets.register('js_comment', js_comment)
    webassets.register('js_all', js_base)
    webassets.register('js_fancybox', js_fancybox)
    webassets.manifest = 'cache' if not app.debug else False
    webassets.cache = not app.debug
    webassets.debug = app.debug
