"""


"""
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db.models.fields import NOT_PROVIDED
from django.db.models.loading import get_models, get_apps, get_app
from django.core.exceptions import ImproperlyConfigured

YUMLME_URL = "http://yuml.me/diagram/%(style)s;scale:%(scale)s;dir:%(direction)s;/class/"

STYLES = {
    'nofunky' : 'Plain text, geometric box, plain lines',
    'plain'   : 'Plain text, geometric box, shadowed lines',
    'scruffy' : 'Hand-written text, paper box, shadowed lines'
}

DIRECTIONS = {
    'LR' : 'Left to right', 
    'RL' : 'Right to left',
    'TB' : 'Top down'
}

FIELD_LABELS = ['db_index', 'null', 'default']

def get_style_options_string():
    return ', '.join('"%s" - (%s)' % (k, v) for k, v in STYLES.items())

def get_direction_options_string():
    return ', '.join('"%s" - (%s)' % (k, v) for k, v in DIRECTIONS.items())

class YUMLFormatter(object):
    START      = '['
    END        = ']'
    PIPE       = '|'
    END_FIELD  = ';'
    START_TYPE = ': '
    END_TYPE   = ''
    INHERIT    = '^--'
    APP_MODEL  = '.'
    FAKE_FIELD = '...{bg:orange}'
    PK         = '(pk) '
    RELATION   = '%(card_from)s<-%(related)s%(symm)s%(card_to)s'
    THROUGH    = '<-.-%(related)s%(symm)s'

    @classmethod
    def wrap(kls, string):
        return kls.START + string + kls.END

    @classmethod
    def wrap_type(kls, string):
        return kls.START_TYPE + string + kls.END_TYPE

    @classmethod
    def wrap_field(kls, string):
        return string + kls.END_FIELD

    @classmethod
    def label(kls, model):
        return model._meta.app_label + kls.APP_MODEL + model._meta.object_name

    @classmethod
    def external(kls, model):
        return kls.wrap(kls.label(model) + kls.PIPE + kls.wrap_field(kls.FAKE_FIELD))

    @classmethod
    def inherit(kls, model, parent):
        return kls.wrap(kls.label(parent)) + kls.INHERIT + kls.wrap(kls.label(model))

    @classmethod
    def field(kls, field, labels=None):
        '''TODO: null and default?'''
        string = ''
        if field.primary_key:
            string += kls.PK
        if field.rel:
            t = kls.label(field.rel.to)
        else:
            t = field.__class__.__name__
            t = t.replace('Field', '')
        
        if labels:
            field_labels = []
            for label in labels:
                if label == 'db_index' and field.db_index:
                    field_labels.append('indexed')
                elif label == 'null' and field.null:
                    field_labels.append('null')
                elif label == 'default' and field.default != NOT_PROVIDED:
                    field_labels.append('Default: %s' % field.default)
            if field_labels:
                t += ' (%s)' % ' - '.join(field_labels)

        string += field.name + kls.wrap_type(t)
        return kls.wrap_field(string)

    @classmethod
    def rel_arrow(kls, model, relation):
        '''TODO:
        cardinality symm and related
        '''
        d = {
            'card_from' :'',
            'related'   : relation.related_name or '',
            'card_to'   :'',
            'symm'      :'',
        }
        return kls.RELATION % d

    @classmethod
    def through_arrow(kls, model, relation):
        '''TODO:
        cardinality symm and related
        '''
        d = {
            'related'   : relation.related_name or '',
            'symm'      :'',
        }
        return kls.THROUGH % d

    @classmethod
    def relation(kls, model, relation):
        return kls.wrap(kls.label(relation.to)) + kls.rel_arrow(model, relation) + kls.wrap(kls.label(model))

    @classmethod
    def through(kls, model, relation):
        return kls.wrap(kls.label(relation.to)) + kls.through_arrow(model, relation) + kls.wrap(kls.label(model))


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '-a', action='store_true', dest='all_applications',
            help='Automaticly include all applications from '
            'INSTALLED_APPS'
        ),
        make_option(
            '-e', action='store', dest='exclude',
            help='Exclude applications matching pattern.'
        ),
        make_option(
            '-o', action='store', dest='outputfile',
            help='Render output file. Type of output dependend '
            'on file extensions. Use png,jpg or pdf to render '
            'graph to image to.'
        ),
        make_option(
            '-d', action='store', dest='direction', default='TB',
            help='Choose the chart direction. Default: "TB". Available '
            'options: %s.' % get_direction_options_string()
        ),
        make_option(
            '--scale', '-p', action='store', dest='scale', type=int, 
            default=100, help='Set a scale percentage. Applies only for -o.'
        ),
        make_option(
            '--style', '-s', action='store', dest='style', default='nofunky',
            help='Choose the output style. Default: "nofunky". Available '
            'options: %s.' % get_style_options_string()
        ),
        make_option(
            '-l', action='append', dest='labels',
            help='Labels to add to the field attributes. Available labels: %s'
            % ', '.join(FIELD_LABELS)
        )
    )
    args = '[appname appname]'
    help = 'Generating model class diagram for yuml.me'
    label = 'application name'

    def validate_options(self, **opts):
        """
        Validates the options passed in the command line.

        Raises:
            CommandError if invalid options are passed in
        """
        if not opts['style'] in STYLES:
            raise CommandError('Invalid style - "%s"' % opts['style'])
        if not opts['direction'] in DIRECTIONS:
            raise CommandError('Invalid direction - "%s"' % opts['direction'])

    def handle(self, *args, **options):
        """
        Args:
            *args (str): List of applications to diagram

        Kwargs:
            **options: All options from the main OptionParser
        """
        self.validate_options(**options)

        if len(args) < 1:
            if options['all_applications']:
                applications = get_apps()
            else:
                raise CommandError("Need one or more arguments for appname.")
        else:
            try:
                applications = [get_app(label) for label in args]
            except ImproperlyConfigured as e:
                raise CommandError("Specified application not found: %s" % e)

        statements = self.yumlfy(applications, options['labels'])

        if options['outputfile']:
            self.render(statements, **options)
        else:
            self.stdout.write('%s' % statements)

    def yumlfy(self, applications, labels):
        F = YUMLFormatter()
        model_list = []
        arrow_list = []
        external_model = set()
        for app_module in applications:
            models = get_models(app_module)
            for m in models:
                string = F.label(m) + F.PIPE
                fields = [f for f in m._meta.fields if not f.auto_created]
                for field in fields:
                    string += F.field(field, labels=labels)
                    if field.rel:
                        arrow_list.append(F.relation(m, field.rel))
                        if get_app(field.rel.to._meta.app_label) not in applications:
                            external_model.add(field.rel.to)
                fields = [f for f in m._meta.many_to_many]
                for field in fields:
                    string += F.field(field)
                    if field.rel.through._meta.auto_created:
                        arrow_list.append(F.relation(m, field.rel))
                    else:
                        arrow_list.append(F.through(m, field.rel))
                    if get_app(field.rel.to._meta.app_label) not in applications:
                        external_model.add(field.rel.to)
                model_list.append(F.wrap(string))
                for parent in m._meta.parents:
                    arrow_list.append(F.inherit(m, parent))
                    if get_app(parent._meta.app_label) not in applications:
                        external_model.add(parent)

        for ext in external_model:
            model_list.append(F.external(ext))

        return model_list + arrow_list

    def render(self, statements, **options):
        from django.utils.six.moves.urllib.parse import urlencode
        from django.utils.six.moves.urllib.request import urlopen
        from django.utils.six.moves.urllib.error import HTTPError
        import os

        output_file = options['outputfile']
        output_ext  = os.path.splitext(output_file)[1]
        dsl_text    = ",".join(statements)

        data = urlencode({'dsl_text': dsl_text})
        data = data.encode('ascii')
        url  = YUMLME_URL % options
        self.stdout.write('Calling: %s' % url)
        try:
            yuml_response = urlopen(url, data)
        except HTTPError as e:
            raise CommandError("Error occured while creating dsl, %s" % e)

        png_file = yuml_response.read().decode('utf-8')
        get_file = png_file.replace('.png', output_ext)
        url = 'http://yuml.me/%s' % get_file
        self.stdout.write('Calling: %s' % url)
        try:
            yuml_response = urlopen(url, data)
        except HTTPError as e:
            raise CommandError("Error occured while generating %s, %s"
                               % (output_file, e))

        resp = yuml_response.read()
        f = open(output_file, 'wb')
        f.write(resp)
        f.close()
