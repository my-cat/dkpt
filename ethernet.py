"""Ethernet II, LLC (802.3+802.2), LLC/SNAP, and Novell raw 802.3,
with automatic 802.1q, MPLS, PPPoE, and Cisco ISL decapsulation."""

import struct
import dpkt, ethernet

ETH_CRC_LEN	= 4
ETH_HDR_LEN	= 14

ETH_LEN_MIN	= 64		# minimum frame length with CRC
ETH_LEN_MAX	= 1518		# maximum frame length with CRC

ETH_MTU		= (ETH_LEN_MAX - ETH_HDR_LEN - ETH_CRC_LEN)
ETH_MIN		= (ETH_LEN_MIN - ETH_HDR_LEN - ETH_CRC_LEN)

# Ethernet payload types - http://standards.ieee.org/regauth/ethertype
ETH_TYPE_PUP	= 0x0200		# PUP protocol
ETH_TYPE_IP	= 0x0800		# IP protocol
ETH_TYPE_ARP	= 0x0806		# address resolution protocol
ETH_TYPE_CDP	= 0x2000		# Cisco Discovery Protocol
ETH_TYPE_DTP	= 0x2004		# Cisco Dynamic Trunking Protocol
ETH_TYPE_REVARP	= 0x8035		# reverse addr resolution protocol
ETH_TYPE_8021Q	= 0x8100		# IEEE 802.1Q VLAN tagging
ETH_TYPE_IPX	= 0x8137		# Internetwork Packet Exchange
ETH_TYPE_IP6	= 0x86DD		# IPv6 protocol
ETH_TYPE_PPP	= 0x880B		# PPP
ETH_TYPE_MPLS	= 0x8847		# MPLS
ETH_TYPE_MPLS_MCAST	= 0x8848	# MPLS Multicast
ETH_TYPE_PPPoE_DISC	= 0x8863	# PPP Over Ethernet Discovery Stage
ETH_TYPE_PPPoE		= 0x8864	# PPP Over Ethernet Session Stage

# MPLS label stack fields
MPLS_LABEL_MASK	= 0xfffff000
MPLS_QOS_MASK	= 0x00000e00
MPLS_TTL_MASK	= 0x000000ff
MPLS_LABEL_SHIFT= 12
MPLS_QOS_SHIFT	= 9
MPLS_TTL_SHIFT	= 0
MPLS_STACK_BOTTOM=0x0100

class Ethernet(dpkt.Packet):
    __hdr__ = (
        ('dst', '6s', ''),
        ('src', '6s', ''),
        ('type', 'H', ETH_TYPE_IP)
        )
    _typesw = {}
    
    def _unpack_data(self, buf):
      #  print('----------------')
        if self.type == ETH_TYPE_8021Q:
            self.tag, self.type = struct.unpack('>HH', buf[:4])
         #   print('---------------------')
            buf = buf[4:]
        elif self.type == ETH_TYPE_MPLS or  self.type == ETH_TYPE_MPLS_MCAST:
         #   print('-------------------------------')
            # XXX - skip labels (max # of labels is undefined, just use 24)
            self.labels = []
            for i in range(24):
                entry = struct.unpack('>I', buf[i*4:i*4+4])[0]
                label = ((entry & MPLS_LABEL_MASK) >> MPLS_LABEL_SHIFT, \
                         (entry & MPLS_QOS_MASK) >> MPLS_QOS_SHIFT, \
                         (entry & MPLS_TTL_MASK) >> MPLS_TTL_SHIFT)
                self.labels.append(label)
                if entry & MPLS_STACK_BOTTOM:
                    break
            self.type = ETH_TYPE_IP
            buf = buf[(i + 1) * 4:]
        try:
            self.data = self._typesw[self.type](buf)
            setattr(self, self.data.__class__.__name__.lower(), self.data)
        except (KeyError, dpkt.UnpackError):
            self.data = buf
    
    def unpack(self, buf):
        dpkt.Packet.unpack(self, buf)
        if self.type > 1500:
        # Ethernet II
            self._unpack_data(self.data)
        elif self.dst.startswith('\x01\x00\x0c\x00\x00') or \
             self.dst.startswith('\x03\x00\x0c\x00\x00'):
            # Cisco ISL
            self.vlan = struct.unpack('>H', self.data[6:8])[0]
            self.unpack(self.data[12:])
        elif self.data.startswith('\xff\xff'):
            # Novell "raw" 802.3
            self.type = ETH_TYPE_IPX
            self.data = self.ipx = self._typesw[ETH_TYPE_IPX](self.data[2:])
        else:
            # 802.2 LLC
            self.dsap, self.ssap, self.ctl = struct.unpack('BBB', self.data[:3])
            if self.data.startswith('\xaa\xaa'):
                # SNAP
                self.type = struct.unpack('>H', self.data[6:8])[0]
                self._unpack_data(self.data[8:])
            else:
                # non-SNAP
                dsap = ord(self.data[0])
                if dsap == 0x06: # SAP_IP
                    self.data = self.ip = self._typesw[ETH_TYPE_IP](self.data[3:])
                elif dsap == 0x10 or dsap == 0xe0: # SAP_NETWARE{1,2}
                    self.data = self.ipx = self._typesw[ETH_TYPE_IPX](self.data[3:])
                elif dsap == 0x42: # SAP_STP
                    self.data = self.stp = stp.STP(self.data[3:])

    def set_type(cls, t, pktclass):
        cls._typesw[t] = pktclass
    set_type = classmethod(set_type)

    def get_type(cls, t):
        return cls._typesw[t]
    get_type = classmethod(get_type)

# XXX - auto-load Ethernet dispatch table from ETH_TYPE_* definitions
def __load_types():
    g = globals()
    for k, v in g.items():
        if k.startswith('ETH_TYPE_'):
            name = k[9:]
            modname = name.lower()
            try:
                mod = __import__(modname, g)
            except ImportError:
                continue
            Ethernet.set_type(v, getattr(mod, name))
        

if not Ethernet._typesw:
    __load_types()

if __name__ == '__main__':
 
    import pcap
    import ip
    import io,http,oicq
    f = open('123.pcap','rb')

    pcap = pcap.Reader(f)
    n=0

    for  ts, buf in pcap:
      #  eth = ethernet.Ethernet(buf)
        '''   
        if eth.type == ETH_TYPE_IP :
            ip1=eth.data
          #  print( ip1)
            if ip1.p == 17:
                udp1=ip1.data
              #  print(ip1.len)
                if udp1.dport == 8000:
                   http1=oicq.OICQ(udp1.data)
                   print(http1)
                   print('>_< im the %d one '%n)
                   break
                   '''
                
        n=n+1
        if n==2351:
            eth = ethernet.Ethernet(buf)
            break
    ip1=eth.data
    udp1=ip1.data
    print(udp1.data)
   
    def decode_int(x, f):
        f += 1
        newf = x.index(b'e', f)
        n = int(x[f:newf])
        if x[f] == '-':
            if x[f + 1] == '0':
                raise ValueError
            elif x[f] == '0' and newf != f+1:
                raise ValueError
        return (n, newf+1)

    def decode_string(x, f):
        colon = x.index(':', f)
        n = int(x[f:colon])
        if x[f] == '0' and colon != f+1:
            raise ValueError
        colon += 1
        return (x[colon:colon+n], colon+n)

    def decode_list(x, f):
        r, f = [], f+1
        while x[f] != 'e':
            v, f = decode_func[x[f]](x, f)
            r.append(v)
        return (r, f + 1)

    def decode_dict(x, f):
        r, f = {}, f+1
        while x[f] != 'e':
            k, f = decode_string(x, f)
            r[k], f = decode_func[x[f]](x, f)
        return (r, f + 1)

    decode_func = {}
    decode_func['l'] = decode_list
    decode_func['d'] = decode_dict
    decode_func['i'] = decode_int
    decode_func['0'] = decode_string
    decode_func['1'] = decode_string
    decode_func['2'] = decode_string
    decode_func['3'] = decode_string
    decode_func['4'] = decode_string
    decode_func['5'] = decode_string
    decode_func['6'] = decode_string
    decode_func['7'] = decode_string
    decode_func['8'] = decode_string
    decode_func['9'] = decode_string

    def bdecode(x):
        try:
            r, l = decode_func[x[0]](x, 0)
        except (IndexError, KeyError, ValueError):
            pass # raise BTFailure("not a valid bencoded string")
        if l != len(x):
            pass # raise K("invalid bencoded value (data after valid prefix)")
        return r

    x= udp1.data
  #  print(x)
    a=bdecode(x.decode(encoding='ISO8859'))
  #  m=a['r']['nodes'].encode(encoding='ISO8859')
    print(a)
    
    print(0xdb)
