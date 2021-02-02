# XMLPermissionMapper

Simple python-utility for mapping XML-based components to the required permissions from AOSP.

## How to run
- Download Google AOSP source code (follow instructions: https://source.android.com/setup/build/downloading)
- Extract a list of AndroidManifest.xml files from the source tree and store that list in a file, name it `manifest_files.txt`
- Run the script `xml_parser.py {path_to_aosp_src_tree} {path_to_manifest_files.txt}`
- Read the mapping from `components_permission.json`