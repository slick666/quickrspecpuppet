import os
import os.path
import regex

class ManifestParser(object):
    def __init__(self, directory=None):
        self.classes = []
        if directory is None:
            directory = os.getcwd()
	self._directory = directory
	self._manifests = self.find_manifests()

    def find_manifests(self):
        manifests = []
        print 
        for dirpath, dirnames, filenames in os.walk('{0}/{1}'.format(self._directory, 'manifests')):
            for filename in [f for f in filenames if f.endswith(".pp")]:
                manifests.append(os.path.join(dirpath, filename))
        return manifests

    def parse(self):
        for filepath in self._manifests:
            matches = self.search_file(filepath, r'class \K[a-zA-Z0-9_:]+(?= [{(])')
            resources = {}
            if any(matches):
                resources['classes'] = self.parse_resources('class', filepath)
                resources['files'] = self.parse_resources('file', filepath)
                self.classes.append(PuppetClass(matches[0], filepath, resources, self._directory))

    def parse_resources(self, resource_type, filepath):
        return self.search_file(filepath, r"{0} {{ ['\"]?\K[a-zA-Z0-9_:\{{\}}\./$]+(?=['\"]?:)".format(resource_type))

    def search_file(self, filepath, regex_string):
        matches = [regex.search(regex_string, line)
            for line in open(filepath)]
        if any(matches):
            matches = [x[0] for x in matches if x is not None]
        else:
            matches = []
        return matches

class PuppetClass(object):
    def __init__(self, name, manifest, resources, base_dir):
        self.base_dir = base_dir
        self.resources = resources
        self.name = name
        self.manifest = manifest
        self.test_filepath = self._generate_test_filepath()
    
    def _generate_test_filepath(self):
        parts = self.name.split('::')
        parts.pop(0)
        if len(parts) < 1:
            parts = ['init']
        return '{0}/{1}/{2}_spec.rb'.format(self.base_dir, 'spec/classes', '/'.join(parts))