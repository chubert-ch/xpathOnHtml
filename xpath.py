#!/usr/bin/env python


# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this software except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import sys
from lxml import etree
import re
import os
import argparse
import unicodedata

parser = argparse.ArgumentParser(description='Find xml things specified by given xpaths')
parser.add_argument('xpath', help='xpath to search with, doesn''t need standard corefiling namespaces')
parser.add_argument('-p', '--paths', action='store_true', help='output paths of found files')
parser.add_argument('-l', '--linenumnode', action='store_true', help='output line number of node')
parser.add_argument('-F', '--fullnode', action='store_true', help='output entire node')
parser.add_argument('-i', '--inlinedfullnode', action='store_true', help='output entire node on one line')
parser.add_argument('-t', '--toplinenode', action='store_true', help='output top line of node')
parser.add_argument('-c', '--content', action='store_true', help='output content of node')
parser.add_argument('-n', '--nonamespace', action='store_true', help='xpath won''t attempt to infer namespaces')
parser.add_argument('-m', '--namespacemap', action='append', help='namespace mapping in the form of "prefix=http://example.com". Can repeat')
parser.add_argument('path', nargs='*', help='path to search in, can be a file, directory or list of files', default=['.'])
args=parser.parse_args()

back = '([/[(]|::)'
qname = '[a-zA-Z_][^(:[/]*'
forward = '(' + qname + '(?=$|[/\ []))'
singleQuoteString = "'[^']*'"
doubleQuoteString = '"[^"]*"'
regexString = doubleQuoteString + '|' + singleQuoteString + '|' + back + forward
#print regexString
regex=re.compile(regexString)
def myreplacement(m):
    if m.group(1):
        return m.group(1) + "cxh:" + m.group(2)
    else:
        return m.group(0)
paths = args.path

if os.path.isdir(args.path[0]):
  paths=(os.path.join(dir, file) for dir, dirs, files in os.walk(args.path[0], topdown=False) for file in files if (file.endswith(".xml") or file.endswith(".xbrl") or file.endswith(".xsd")))

try:
  for filePath in paths:
    if os.stat(filePath).st_size < 5:
      continue; #skip empty files
    try:
      doc_name = filePath
      tree = etree.parse(doc_name)
      ns = tree.getroot().nsmap
      xpath = args.xpath
      if args.namespacemap:
        for nmitem in args.namespacemap:
          splitmap = nmitem.split("=")
          if len(splitmap) == 2:
            ns[splitmap[0]] = splitmap[1]
      if None in ns:
        ns['cxh']=ns[None]
        del ns[None]
        if not args.nonamespace:
          xpath=regex.sub(myreplacement,xpath)
#          print xpath
#          print ns
      prefix=filePath + ":"
      if len(args.path)==1 and not os.path.isdir(args.path[0]):
        prefix=""
      res = tree.getroot().xpath(xpath, namespaces=ns)
      if type(res) is etree._ElementStringResult:
        res=[res]
      for node in res:
        toPrint = []
        if type(node) is etree._ElementStringResult:
          nodestr=node
          node=node.getparent()
        else:
          if type(node) is etree._ElementUnicodeResult:
            nodestr=unicodedata.normalize('NFKD', node).encode('ascii','ignore')
            node=node.getparent()
          else:
            nodestr=etree.tostring(node, pretty_print=True)
        if args.paths:
          toPrint.append(filePath)
        if args.linenumnode:
          toPrint.append(str(node.sourceline))
        if args.fullnode:
          toPrint.append(nodestr)
        if args.inlinedfullnode:
          toPrint.append(nodestr.replace('\n', ' ').replace('\r', ''))
        if args.toplinenode:
          toPrint.append(nodestr.splitlines()[0])
        if args.content:
          toPrint.append(etree.tostring(node, method="text"))
        if len(toPrint)==0:
          toPrint2=prefix + str(node.sourceline)+": "+nodestr.splitlines()[0]
        else:
          toPrint2=""
          for i in range(len(toPrint)-1):
            toPrint2+=toPrint[i]+": "
          if len(toPrint)>0:
            toPrint2+=toPrint.pop()
        print toPrint2

    except (etree.ParserError, etree.XMLSyntaxError) as e:
      sys.stderr.write(str(e)+"\n")
      sys.stderr.write(str(filePath)+"\n")
    except etree.XPathEvalError as e:
      if not "Undefined namespace prefix" in str(e):
        sys.stderr.write(str(e)+"\n")
        sys.stderr.write(str(xpath)+"   "+str(ns))
        sys.stderr.write(str(filePath)+"\n")

except IOError as e:
  sys.stderr.write(str(e)+"\n")

# vim: ft=python shiftwidth=2 ts=2 softtabstop=2 expandtab
