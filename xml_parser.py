import sys
import os
import xml.etree.ElementTree as ET

PERMISSION = '{http://schemas.android.com/apk/res/android}permission'
READ_PERMISSION = '{http://schemas.android.com/apk/res/android}readPermission'
WRITE_PERMISSION = '{http://schemas.android.com/apk/res/android}writePermission'
NAME = '{http://schemas.android.com/apk/res/android}name'
AUTHORITY = '{http://schemas.android.com/apk/res/android}authorities'
EXPORTED = '{http://schemas.android.com/apk/res/android}exported'

AOSP_SRC_DIR = sys.argv[0]
# execute 'find . -name "AndroidManifest.xml" > manifest_files.txt from within AOSP_SRC_DIR to generate the following file'
ANDROID_MANIFIST_LIST = sys.argv[1];

def main():
    result = {}
    unique_lines = []
    _, data = read_file(ANDROID_MANIFIST_LIST)
    lines = data.split("\n")
    for line in lines:
        if ".xml: " in line and './cts/' not in line:
            xml_file = line.split(": ")[0]
            if xml_file not in unique_lines:
                unique_lines.append(xml_file)

    for line in unique_lines:
        _, xml_content = read_file('{}/{}'.format(AOSP_SRC_DIR, line))
        myroot = ET.fromstring(xml_content)

        pkg_name = myroot.attrib['package']

        for a in myroot.find('application').attrib:
            if a == PERMISSION:
                name = "NA"
                if NAME in myroot.find('application').attrib:
                    name = myroot.find('application').attrib[NAME]
                permission = myroot.findall('application')[0].attrib[a]
                # print("application", name, "permission", permission)
                if permission not in result:
                    result[permission] = []
                result[permission].append(
                    {
                        'component': 'application',
                        'class_pkg': pkg_name,
                        'type': 'permission',
                        'authority': None,
                        'exported': None,
                        'actions': []
                    }
                )

        for component in myroot.findall('application')[0].getchildren():
            for a in component.attrib:
                if a in [PERMISSION, READ_PERMISSION, WRITE_PERMISSION]:
                    actions = []
                    try:
                        for c in component.find('intent-filter').getchildren():
                            if c.tag == 'action':
                                actions.append(c.attrib[NAME])
                    except:
                        pass
                    permission_usage = 'permission'
                    if a == READ_PERMISSION:
                        permission_usage = 'readPermission'
                    if a == WRITE_PERMISSION:
                        permission_usage = 'writePermission'
                    starts_with_package = component.attrib[NAME].startswith(pkg_name)
                    component.attrib[NAME] = ".{}".format(component.attrib[NAME]) \
                        if not component.attrib[NAME].startswith(".") else component.attrib[NAME]
                    clazz_name = component.attrib[NAME] if starts_with_package else "{}{}".format(pkg_name, component.attrib[NAME])
                    if component.attrib[a] not in result:
                        result[component.attrib[a]] = []
                    result[component.attrib[a]].append(
                        {
                            'component': component.tag,
                            'class_pkg': clazz_name,
                            'type': permission_usage,
                            'authority': None if AUTHORITY not in component.attrib else component.attrib[AUTHORITY],
                            'exported': True if EXPORTED not in component.attrib else True if component.attrib[EXPORTED] == 'true' else False,
                            'actions': actions
                        }
                    )

        write_json_file('./components_permission.json', result)


def file_exists(path):
    return os.path.isfile(path)

def write_json_file(path, json_content):
    try:
        file = open(path, 'w+')
        str_content = str(json.dumps(json_content, indent=2))
        file.write(str_content)
        file.close()
        return True, None
    except Exception as e:
        return False, str(e)

def read_file(path):
    try:
        if not file_exists(path):
            raise FileNotFoundError

        file = open(path, 'r')
        content = file.read()
        file.close()
        return True, content
    except Exception as e:
        return False, str(e)

if __name__ == '__main__':
    main()
