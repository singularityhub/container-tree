#!/usr/bin/python

# Copyright (C) 2019 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest
import tempfile
import shutil
import json
import os


print("############################################################ test_utils")

class TestUtils(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        
    def test_write_read_files(self):
        '''test_write_read_files will test the functions write_file and read_file
        '''
        print("Testing utils.write_file")
        from containertree.utils import write_file
        tmpfile = tempfile.mkstemp()[1]
        os.remove(tmpfile)
        write_file(tmpfile,"mocos!")
        self.assertTrue(os.path.exists(tmpfile))        

        print("Testing utils.read_file...")
        from containertree.utils import read_file
        content = read_file(tmpfile)
        self.assertEqual("mocos!", content)

        from containertree.utils import write_json
        print("Testing utils.write_json.")
        print("...Case 1: Providing bad json")
        bad_json = {"IWuvWaffles?'}":[{True}, "2", 3]}
        tmpfile = tempfile.mkstemp()[1]
        os.remove(tmpfile)        
        with self.assertRaises(TypeError) as cm:
            write_json(bad_json, tmpfile)

        print("...Case 2: Providing good json")        
        good_json = {"IWuvWaffles!": [True, "2", 3]}
        tmpfile = tempfile.mkstemp()[1]
        os.remove(tmpfile)
        write_json(good_json,tmpfile)
        with open(tmpfile,'r') as filey:
            content = json.loads(filey.read())
        self.assertTrue(isinstance(content, dict))
        self.assertTrue("IWuvWaffles!" in content)

        print("Testing utils.print_json")
        from containertree.utils import print_json
        result=print_json({1:1})
        self.assertEqual('{\n    "1": 1\n}', result)

        print("Testing recursive find")
        from containertree.utils import recursive_find
        files = list(recursive_find(tempfile.gettempdir()))
        self.assertTrue(tmpfile in files)

        print("Testing get_tmpdir.")
        from containertree.utils import get_tmpdir
        tmpdir = get_tmpdir(prefix="skittles")
        self.assertTrue(os.path.exists(tmpdir))

        print("Testing get_tmpfile")
        from containertree.utils import get_tmpfile
        tmpfile = get_tmpfile(prefix="marshmallow", tmpdir=tmpdir)
        self.assertTrue(os.path.basename(tmpfile).startswith('marshmallow'))
        self.assertEqual(os.path.dirname(tmpfile), tmpdir)
        shutil.rmtree(tmpdir)


    def test_get_installdir(self):
        '''get install directory should return the base of where singularity
        is installed
        '''
        print("Testing utils.get_installdir")
        from containertree.utils import get_installdir
        whereami = get_installdir()
        print(whereami)
        self.assertTrue(whereami.endswith('containertree'))


    def test_terminal(self):
        print('Testing utils.run_command')
        from containertree.utils import run_command
        result = run_command(['echo', 'Las', 'Papas', 'Fritas'])
        self.assertEqual(result['message'], 'Las Papas Fritas\n')
        self.assertEqual(result['return_code'], 0)     

    def test_get_template(self):
        '''test that template names / files are correctly returned'''
        from containertree.utils import get_templates, get_template
        templates = get_templates()
        self.assertTrue("treemap" in templates)
        template = get_template("treemap")
        self.assertTrue("treemap.html" in template) 
        template = get_template("doesnt-exist")
        self.assertTrue(template == None)

    def test_parse_image_uri(self):
        from containertree.utils import parse_image_uri

        print('Testing utils.parse_image_uri.. defaults')
        names = parse_image_uri("ubuntu")
        
        # Compare expected to actual
        expected = {'fullUri': 'library/ubuntu:latest',
                    'namespace': 'library',
                    'nodeUri': 'library/ubuntu', 
                    'registry': None,
                    'repo_name': 'ubuntu',
                    'repo_tag': 'latest',
                    'version': None}

        for key, value in expected.items():
            self.assertTrue(key in names)
            self.assertTrue(names[key] == value) 

        print('Testing utils.parse_image_uri.. add tag')
        names = parse_image_uri("ubuntu:custom-tag")
        self.assertTrue(names['repo_tag'] == "custom-tag")

        print('Testing utils.parse_image_uri.. add registry')
        names = parse_image_uri("registry.io/ubuntu:custom-tag")
        self.assertTrue(names['registry'] == "registry.io")

        print('Testing utils.parse_image_uri.. add version')
        names = parse_image_uri("ubuntu@version")
        self.assertTrue(names['version'] == "version")

if __name__ == '__main__':
    unittest.main()
