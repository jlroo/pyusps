from collections import OrderedDict
from lxml import etree
import pyusps.urlutil

api_url = 'https://secure.shippingapis.com/ShippingAPI.dll'
zipcode_max = 5


def _find_error( root ):
    if root.tag == 'Error':
        num = root.find('Number')
        desc = root.find('Description')
        return num , desc


def _get_error( error ):
    (num , desc) = error
    return ValueError(
        '{num}: {desc}'.format(
            num=num.text ,
            desc=desc.text ,
        )
    )


def _get_zipcode_error( zipcode ):
    error = zipcode.find('Error')
    if error is not None:
        error = _find_error(error)
        return _get_error(error)


def _parse_zipcode( zipcode ):
    result = OrderedDict()
    for child in zipcode.iterchildren():
        # elements are yielded in order
        name = child.tag.lower()
        result[name] = child.text
    return result


def _process_one( zipcode ):
    # Raise address error if there's only one item
    error = _get_zipcode_error(zipcode)
    if error is not None:
        raise error
    return _parse_zipcode(zipcode)


def _process_multiple( zipcodes ):
    results = []
    count = 0
    for zipcode in zipcodes:
        # Return error object if there are
        # multiple items
        error = _get_zipcode_error(zipcode)
        if error is not None:
            result = error
        else:
            result = _parse_zipcode(zipcode)
            if str(count) != zipcode.get('ID'):
                msg = ('The ZipCode returned are not in the same '
                       'order they were requested'
                       )
                raise IndexError(msg)
        results.append(result)
        count += 1
    return results


def _parse_response( res ):
    # General error, e.g., authorization
    error = _find_error(res.getroot())
    if error is not None:
        raise _get_error(error)

    results = res.findall('ZipCode')
    length = len(results)
    if length == 0:
        raise TypeError(
            'Could not find any address or error information'
        )
    if length == 1:
        return _process_one(results.pop())
    return _process_multiple(results)


def _get_response( xml ):
    params = OrderedDict([
        ('API' , 'CityStateLookup') ,
        ('XML' , etree.tostring(xml)) ,
    ])
    url = '{api_url}?{params}'.format(
        api_url=api_url ,
        params=pyusps.urlutil.urlencode(params) ,
    )

    res = pyusps.urlutil.urlopen(url)
    res = etree.parse(res)
    return res


def _create_xml( user_id, *args ):
    root = etree.Element('CityStateLookupRequest', USERID=user_id)

    if len(args) > zipcode_max:
        # Raise here. The Verify API will not return an error. It will
        # just return the first 5 results
        raise ValueError(
            'Only {address_max} addresses are allowed per '
            'request'.format(
                zipcode_max = zipcode_max,
                )
            )

    for i, arg in enumerate(args):
        zip_code = str(arg.get('zip_code', None))
        zipcode_el = etree.Element('ZipCode', ID=str(i))
        root.append(zipcode_el)

        if zip_code is not None:
            zip5 = zip_code[:5]

        zip5_el = etree.Element('Zip5')
        if zip5 is not None:
            zip5_el.text = zip5
        zipcode_el.append(zip5_el)
    return root


def verify(user_id, *args):
    xml = _create_xml(user_id, *args)
    res = _get_response(xml)
    res = _parse_response(res)
    return res
