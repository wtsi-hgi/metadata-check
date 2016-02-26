
import argparse


class _HelpAction(argparse._HelpAction):

    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('--argA', required=False)
#parser.add_argument('--help', action=_HelpAction)

subparsers = parser.add_subparsers(dest='blah')
#subparsers.required = False
parsA = subparsers.add_parser('a', help='Parser A', parents=[parser])
parsA.add_argument('--aa', required=False)

parsB = subparsers.add_parser('b', help='Parser B', parents=[parser])

print((parser.format_help()))

#parser.add_argument('-', dest='__dummy', action="store_true", help=argparse.SUPPRESS)
parser.parse_args()

# parent = argparse.ArgumentParser()
# parent.add_argument('--arg_par', required=False)
#
#
# parser = argparse.ArgumentParser(prog='PROG', add_help=False)
# #parser.add_argument('--foo', action='store_true', required=False, help='foo help')
# subparsers = parser.add_subparsers(help='sub-command help')
# subparsers.required = True
# #default_parser = subparsers.add_parser('')
#
# # create the parser for the "a" command
# parser_a = subparsers.add_parser('a', parents=[parser], help='a help')
# parser_a.add_argument('--bar', type=int, required=False, help='bar help')
#
#
# # create the parser for the "b" command
# parser_b = subparsers.add_parser('b', parents=[parser], help='b help')
# parser_b.add_argument('--baz', choices='XYZ', required=False, help='baz help')
#
# parser.parse_args()
#
# # parser_samples = subparsers.add_parser('test_samples', parents=[parser], help='Run tests on samples')
# # parser_samples.add_argument('--irods_vs_seqsc', action='store_true', required=False,
# #                                 help='Add this flag if you want the samples to be checked for iRODS metadata consistency vs Sequencescape')
