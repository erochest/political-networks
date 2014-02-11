#!/usr/bin/env python

"""\
This flattens the JSON structures into a flattened tuple.

NB: THIS THROWS AWAY DATA. For instance, if there is more than one industry,
only the first is listed.
"""


from __future__ import absolute_import, unicode_literals, print_function

import argparse
import codecs
import csv
import json
import sys


COLUMNS = (
        'id',
        'universal-name',
        'name',
        'website',
        'company-type',
        'industry',
        'location',
        )


def try_get(struct, keys, default=None):
    """\
    This walks a structure to get a value. If a key or index is missing, the default
    is returned.
    """
    if not keys:
        return struct
    try:
        return try_get(struct[keys[0]], keys[1:])
    except (KeyError, IndexError):
        return default


def flatten(company):
    """This flattens a company dictionary tree into a tuple."""
    address = [
            try_get(company, ['locations', 'values', 0, 'address', 'street1']),
            try_get(company, ['locations', 'values', 0, 'address', 'city']),
            try_get(company, ['locations', 'values', 0, 'address', 'postalCode']),
            ]
    return (
            company.get('id'),
            company.get('universalName'),
            company.get('name'),
            company.get('websiteUrl'),
            company.get('companyType', {}).get('code'),
            try_get(company, ['industries', 'values', 0, 'code']),
            ', '.join( line for line in address if line is not None ),
            )


def encode_all(seq):
    return tuple(
            cell.encode('utf8') if isinstance(cell, unicode) else cell
            for cell in seq
            )


def parse_args(args=None):
    args = sys.argv[1:] if args is None else args
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-i', '--input', dest='input', action='store',
                        help='The input JSON file.')
    parser.add_argument('-o', '--output', dest='output', action='store',
                        help='The output file for the CSV.')

    opts = parser.parse_args(args)

    if opts.input is None or opts.output is None:
        parser.error('You must supply both input and output parameters.')

    return opts


def main():
    args = parse_args()

    with codecs.open(args.input, encoding='utf8') as fin, \
         open(args.output, 'wb') as fout:
        writer = csv.writer(fout)
        writer.writerow(COLUMNS)
        writer.writerows(
                encode_all(flatten(company)) for company in json.load(fin)
                )


if __name__ == '__main__':
    main()
