from warpoptions import *
description="""
Preprocesses the fields so that they are in standard fortran
order and stores them in a pickle dictionary.  A config file is 
save alongside the pickle dictionary.  These files are then
to be used with the FieldLoader class.
"""
#Handle command line arguments and default values with argparse.
parser.description = description
parser.formatter_class=argparse.RawDescriptionHelpFormatter
parser.add_argument('raw_field_file', type=str, 
                    help='The path to the field file that will be preprocessed.')
parser.add_argument('-f', '--format', dest="formattype", type=str, 
                    help='Source of the raw_field_file.  Right now, only Poisson is ' + 
                    'supported.  If this is not specified, the program automatically ' + 
                    'detects the file type from its extensions.',
                    default="")
parser.add_argument('-c', '--config_front', dest="config_front", type=str,
                    help='Path to which the extension .cfg will' +
                    'be added and in which the processed field parameters are stored.  Default' +
                    'is the raw_field_file without its extension.', default=None) 
parser.add_argument('-k', '--pickle_front', dest="pickle_front", type=str,
                    help='Path to which _electric.pckl and/or _magnetic.pckl will' +
                    'be added and in which the processed field is stored.  Default' +
                    'is the raw_field_file without its extension.', default=None) 
args = parser.parse_args()
from fields.field_preprocessor import FieldPreProcessor

print "Argument dictionary: " 
print "\t" + "\n\t".join([k + " = " + str(v) for k, v in vars(args).iteritems()])

field_preprocessor = FieldPreProcessor(args.raw_field_file,
                      formattype = args.formattype)
field_preprocessor.archive(args.pickle_front,args.config_front)
