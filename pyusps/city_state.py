from collections import OrderedDict
from lxml import etree
import pyusps.urlutil

api_url = 'http://production.shippingapis.com/ShippingAPI.dll?API=CityStateLookup'


def _find_error(root):
    if root.tag == 'Error':
        num = root.find('Number')
        desc = root.find('Description')
        return num, desc


def _get_error(error):
    (num, desc) = error
    return ValueError(
        '{num}: {desc}'.format(
            num=num.text,
            desc=desc.text,
            )
        )


def _get_address_error(address):
    error = address.find('Error')
    if error is not None:
        error = _find_error(error)
        return _get_error(error)


def _parse_address(address):
    result = OrderedDict()
    for child in address.iterchildren():
        # elements are yielded in order
        name = child.tag.lower()
        # More user-friendly names for street
        # attributes
        if name == 'zip5':
            name = 'zip5'
        elif name == 'city':
            name = 'city'
        elif name == 'state':
            name = 'state'
        result[name] = child.text

    return result


def _process_one(address):
    # Raise address error if there's only one item
    error = _get_address_error(address)
    if error is not None:
        raise error
    return _parse_address(address)


def _parse_response(res):
    # General error, e.g., authorization
    error = _find_error(res.getroot())
    if error is not None:
        raise _get_error(error)

    results = res.findall('CityStateLookupResponse')
    length = len(results)
    if length == 0:
        raise TypeError(
            'Could not find any City that match that Zipcode or error information'
            )
    return _process_one(results.pop())


def _get_response(xml):
    params = OrderedDict([
            ('API', 'Verify'),
            ('XML', etree.tostring(xml)),
            ])
    url = '{api_url}?{params}'.format(
        api_url=api_url,
        params=pyusps.urlutil.urlencode(params),
        )

    res = pyusps.urlutil.urlopen(url)
    res = etree.parse(res)

    return res


def _create_xml(user_id, *args):
    root = etree.Element('CityStateLookupRequest', USERID=user_id)

    for i, arg in enumerate(args):
        city_el = etree.Element('ZipCode', ID=str(i))
        root.append(city_el)
        zip5_el = etree.Element('Zip5')
        city_el.append(zip5_el)

    return root


def verify(user_id, *args):
    xml = _create_xml(user_id, *args)
    res = _get_response(xml)
    res = _parse_response(res)
    return res
