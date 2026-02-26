
import zipfile
import xml.etree.ElementTree as ET


import zipfile
import xml.etree.ElementTree as ET

def get_docx_text(path):
    document = zipfile.ZipFile(path)
    xml_content = document.read('word/document.xml')
    document.close()
    tree = ET.fromstring(xml_content)
    
    text_parts = []
    # Just iterate through everything and look for tags ending in 't'
    for element in tree.iter():
        if element.tag.endswith('}t') or element.tag == 't':
            if element.text:
                text_parts.append(element.text)
    
    return ' '.join(text_parts)

if __name__ == '__main__':
    try:
        text = get_docx_text('IEEE Research Paper Template-a4.docx')
        print(text)
    except Exception as e:
        import traceback
        traceback.print_exc()
