import struct,collections
class _MetaPacket(type):
    def __new__(cls, clsname, clsbases, clsdict):
        t = type.__new__(cls, clsname, clsbases, clsdict)
        st = getattr(t, '__hdr__', None)
        if st is not None:
            clsdict['__slots__'] = [ x[0] for x in st ] + [ 'data' ]
            t = type.__new__(cls, clsname, clsbases, clsdict)
            t.__hdr_fields__ = [ x[0] for x in st ]
            t.__hdr_fmt__ = getattr(t, '__byte_order__', '>') + ''.join([ x[1] for x in st ])
            t.__hdr_len__ = struct.calcsize(t.__hdr_fmt__)
            t.__hdr_defaults__ =collections.OrderedDict(zip(
                t.__hdr_fields__, [ x[2] for x in st ]))
        return t

class IP(metaclass=_MetaPacket):
    __hdr__ = (
        ('v_hl', 'B', (4 << 4) | (20 >> 2)),
        ('tos', 'B', 0),
        ('len', 'H', 20),
        ('id', 'H', 0),
        ('off', 'H', 0),
        ('ttl', 'B', 64),
        ('p', 'B', 0),
        ('sum', 'H', 0),
        ('src', '4s', '\x00' * 4),
        ('dst', '4s', '\x00' * 4)
        )

i=IP()
print(i.__hdr_fields__)
print(i.__hdr_defaults__)
for m,n in i.__hdr_defaults__.items():
    print(m,n)
