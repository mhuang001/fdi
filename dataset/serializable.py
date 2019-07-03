import json


class SerializableEncoder(json.JSONEncoder):
    """ can encode parameter and product etc such that they can be recovered
    with deserializeClassID
    """

    def default(self, obj):
        try:
            #print('%%%' + str(obj.__class__))
            # Let the base class default method raise the TypeError
            d = json.JSONEncoder.default(self, obj)
            #print('d=' + d)
        except TypeError as err:
            try:
                # logger.debug
                #print('&&&& %s %s' % (str(obj.__class__), str(obj)))
                if issubclass(obj.__class__, bytes):
                    return dict(hex=obj.hex(), classID='bytes', version='')
                return obj.serializable()
            except Exception:
                print('exc ' + str(err))
                raise err


#    obj = json.loads(jstring)

def serializeClassID(o):
    """ return JSON using special encoder SerializableEncoder """
    return json.dumps(o, cls=SerializableEncoder, indent=2)


class Serializable():
    """ mh: Can be serialized.
    Has a ClassID and version instance property to show its class
    and version information.
    """

    def __init__(self, **kwds):
        super().__init__(**kwds)
        sc = self.__class__
        #print('$$ ' + sc.__name__ + str(issubclass(sc, dict)))
        if issubclass(sc, dict):
            self['classID'] = sc.__qualname__
            self['version'] = ''
        else:
            self.classID = sc.__qualname__
            self.version = ''

    def serialized(self):
        return serializeClassID(self)

    def serializable(self):
        """ returns an odict that has all state info of this object.
        Subclasses should override this function.
        """
        return Dict(info='serializable function not implemented')
