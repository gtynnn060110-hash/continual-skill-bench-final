# XML Processing Skill

## Overview
This skill provides guidance on reading, parsing, and extracting data from XML
files using standard Python libraries.

## Parsing XML

### Using ElementTree (standard library)
```python
import xml.etree.ElementTree as ET

tree = ET.parse("filing.xml")
root = tree.getroot()
```

### Reading from a string
```python
import xml.etree.ElementTree as ET

xml_text = open("filing.xml", "r", encoding="utf-8").read()
root = ET.fromstring(xml_text)
```

## Extracting Fields

```python
# Example: extract all <section> titles and text
sections = []
for sec in root.findall(".//section"):
    title = (sec.findtext("title") or "").strip()
    body = (sec.findtext("body") or "").strip()
    if title or body:
        sections.append({"title": title, "body": body})
```

## Handling Namespaces

```python
# Example namespace map
ns = {"x": "http://example.com/schema"}

for item in root.findall(".//x:item", ns):
    value = item.get("value")
```

## Converting XML to JSON-like Structures

```python
def element_to_dict(elem):
    return {
        "tag": elem.tag,
        "attrib": dict(elem.attrib),
        "text": (elem.text or "").strip(),
        "children": [element_to_dict(c) for c in list(elem)],
    }

data = element_to_dict(root)
```

## Tips
- Always handle namespaces explicitly; otherwise queries may return nothing.
- Use `.findtext()` to avoid `None` errors for missing child elements.
- Strip whitespace aggressively to avoid formatting noise.
- If XML is huge, consider `iterparse` to stream and reduce memory usage.

## Error Handling
- Catch `ET.ParseError` for invalid XML.
- Validate required elements exist before accessing them.
- Log unexpected tag structures rather than failing silently.
