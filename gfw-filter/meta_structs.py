import struct
import math
import enum
import logging
import os

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

class MetaStructParseError(Exception):
    pass

class Header:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields
        self.length = sum([f.length for f in fields])

    def pack(self, args):
        ret = b""
        for field, arg in zip(self.fields, args):
            val = field.pack(arg)
            ret += val
        return ret

    def format(self, values, depth):
        _, values = values
        print('\t' * depth, f"{self.name}")
        for field, val in zip(self.fields, values):
            field.format(val, depth + 1)

    def unpack(self, data):
        ret = []
        ind = 0
        for field in self.fields:
            value, length = field.unpack(data[ind:])
            ret.append(value)
            ind += length
        return (self.name, ret), ind

class Many():
    def __init__(self, name, field):
        self.name = name
        self.field = field

    def pack(self, args):
        raise NotImplementedError

    def format(self, values, depth):
        _, values = values
        for v in values:
            self.field.format(v, depth + 1)

    def unpack(self, data):
        res = []
        parsed_len = 0
        while parsed_len < len(data):
            ret, l = self.field.unpack(data[parsed_len:])
            parsed_len += l
            res.append(ret)
        r = (self.name, res), parsed_len
        return r

class OptionalFieldHeader(Header):
    def __init__(self, name, fields, len_pos):
        super().__init__(name, fields)
        self.len_pos = len_pos

    def unpack(self, data):
        ret = []
        ind = 0
        field_ind = 0

        for field in self.fields[:self.len_pos + 1]:
            value, length = field.unpack(data[ind:])
            ret.append(value)
            ind += length
            field_ind += 1
        length_total = ret[-1][1]

        while ind < length_total:
            value, length = self.fields[field_ind].unpack(data[ind:])
            ret.append(value)
            ind += length
            field_ind += 1
            if field_ind == len(self.fields):
                break

        return (self.name, ret), ind

class AlternativeTypeHeader():
    def __init__(self, selector, types):
        self.selector = selector
        self.types = types
        self.length = next(types.values().__iter__()).length

    def unpack(self, data):
        x, l = self.selector.unpack(data)
        decoded_type = self.types.get(x[1])
        if decoded_type is None:
            decoded_type = list(self.types.values())[0]
        return decoded_type.unpack(data)

    def format(self, values, depth):
        if values[0] is None:
            indent = "\t" * depth
            print(f"{indent}UNKNOWN TYPE")
            return
        return next(x for x in self.types.values() if x.name == values[0]).format(values, depth)

class VariableOrderHeader(Header):
    def __init__(self, name, fields, field_mapping, type_fmt, type_offset, type_len, type_ind, length):
        super().__init__(name, fields)
        self.field_mapping = field_mapping
        self.type_fmt = type_fmt
        self.type_offset = type_offset
        self.type_len = type_len
        self.type_ind = type_ind
        self.length = length

    def pack(self, args):
        ret = b""
        for field, arg in zip(self.fields, args):
            if arg:
                val = field.pack(arg)
                ret += val
        return ret

    def format(self, data, depth):
        _, data = data
        print('\t' * depth, f"{self.name}")
        for field in data:
            _, field_data = field
            try:
                header = self.fields[self.field_mapping[field_data[self.type_ind][1]]]
            except KeyError:
                log.warn(f"Unkown header type received: {hex(field_data[self.type_ind][1])} (while parsing {self.name})")
                return

            header.format(field, depth + 1)

    def unpack(self, data):
        ret = []
        hdrs = []
        ind = 0
        while ind < self.length:
            if ind > self.length - self.type_len:
                log.warn("Short trailing data", self.length, len(data), data[ind:])
                return (self.name, ret), ind
            hdr_type = struct.unpack(self.type_fmt, data[ind + self.type_offset:ind + self.type_offset + self.type_len])[0]
            try:
                header = self.fields[self.field_mapping[hdr_type]]
                #print(f"Parsed {self.fields[self.field_mapping[hdr_type]].name}")
            except KeyError:
                log.warn(f"Unkown header type received: {hex(hdr_type)} (while parsing {self.name}) Data: {data[ind:][:0x20].hex()}")
                return (self.name, ret), ind

            value, length = header.unpack(data[ind:])
            for i, el in enumerate(hdrs):
                if hdr_type < el:
                    hdrs.insert(i, hdr_type)
                    ret.insert(i, value)
                    break
            else:
                i = len(hdrs)
                hdrs.insert(i, hdr_type)
                ret.insert(i, value)
                
            ind += length

        return (self.name, ret), ind


class RepeatedFieldHeader(Header):
    def __init__(self, name, fields, indicator_map, padding_field=None):
        super().__init__(name, fields)
        self.indicator_map = indicator_map
        self.padding_field = padding_field

    def pack(self, args):
        # FIXME: padding_field option not considered here!
        ret = b""
        field_ind = 0
        arg_ind = 0
        repetitions_map = dict()
        while arg_ind < len(args):
            if field_ind in self.indicator_map:
                repetitions_map[self.indicator_map[field_ind]] = args[arg_ind]

            if field_ind in repetitions_map:
                for _ in range(repetitions_map[field_ind]):
                    val = self.fields[field_ind].pack(args[arg_ind])
                    ret += val
                    arg_ind += 1
            else:
                val = self.fields[field_ind].pack(args[arg_ind])
                ret += val
                arg_ind += 1
            field_ind += 1
        return ret

    def format(self, values, depth):
        _, values = values
        print('\t' * depth, f"{self.name}")
        field_ind = 0
        arg_ind = 0
        repetitions_map = dict()
        while arg_ind < len(values):
            if field_ind in self.indicator_map:
                repetitions_map[self.indicator_map[field_ind]] = values[arg_ind][1]

            if field_ind in repetitions_map:
                for _ in range(repetitions_map[field_ind]):
                    self.fields[field_ind].format(values[arg_ind], depth + 1)
                    arg_ind += 1
            else:
                self.fields[field_ind].format(values[arg_ind], depth + 1)
                arg_ind += 1
            field_ind += 1

    def unpack(self, data):
        ret = []
        ind = 0
        repetitions_map = dict()
        try:
            for field_ind, field in enumerate(self.fields):
                if field_ind in repetitions_map:
                    for _ in range(repetitions_map[field_ind]):
                        value, length = field.unpack(data[ind:])
                        ret.append(value)
                        ind += length
                    continue
                
                value, length = field.unpack(data[ind:])
                if field_ind in self.indicator_map:
                    repetitions_map[self.indicator_map[field_ind]] = value[1]

                if self.padding_field and self.padding_field[0] == field_ind:
                    if not self.padding_field[1](ret):
                        # call padding check function and skip
                        # padding if it is not present
                        continue 

                ret.append(value)
                ind += length
            return (self.name, ret), ind
        except Exception as e:
            raise MetaStructParseError(f"Failure while parsing {self.name}") from e

class VariableLengthHeader(Header):
    def __init__(self, name, fields, indicator_map, type_ind_map=None):
        super().__init__(name, fields)
        self.indicator_map = indicator_map
        if type_ind_map is None:
            self.type_ind_map = {}
        else:
            self.type_ind_map = type_ind_map

    def format(self, data, depth):
        _, data = data
        print('\t' * depth, f"{self.name}")
        type_map = {k:v for k,v in self.type_ind_map.values()}
        for field_ind, field in enumerate(data):
            name, field_data = field
            if field_ind in type_map:
                header = next((v for v in type_map[field_ind].values() if v.name == name), Field("Unknown Type Data", "", 0))
            else:
                header = self.fields[field_ind]
            header.format(field, depth + 1)

    def unpack(self, data):
        ret = []
        ind = 0
        length_map = dict()
        type_map = {}
        try:
            for field_ind, field in enumerate(self.fields):
                # Change Field if needed by type_map
                if field_ind in type_map:
                    field = type_map[field_ind]

                if field_ind in self.indicator_map:
                    value, length = field.unpack(data[ind:])
                    length_map[self.indicator_map[field_ind]] = value[1]
                elif field_ind in length_map:
                    length = length_map[field_ind]
                    # We will ignore the length of the actually parsed data
                    value, _ = field.unpack(data[ind:ind + length])
                elif field_ind in self.type_ind_map:
                    value, length = field.unpack(data[ind:])
                    type_f, decode_types = self.type_ind_map[field_ind]
                    try:
                        type_map[type_f] = decode_types[value[1]]
                    except KeyError:
                        log.warn(f"Unknown type {type_f} while parsing {self.name}! Data: {data[ind:][:0x20].hex()}")
                else:
                    value, length = field.unpack(data[ind:])

                ret.append(value)
                ind += length
            return (self.name, ret), ind
        except Exception as e:
            raise MetaStructParseError(f"Failure while parsing {self.name}") from e

class Field:
    def __init__(self, name, fmt, length, print_fmt=None):
        self.name = name
        self.fmt = fmt
        self.length = length
        self.print_fmt = print_fmt

    def pack(self, data):
        if not self.fmt:
            return data
        return struct.pack(self.fmt, data)

    def format(self, data, depth):
        _, data = data
        if self.print_fmt:
            print_data = self.print_fmt(data)
            if isinstance(print_data, list):
                print('\t' * depth, f"{self.name} {hex(print_data[0])}")
                for line in print_data[1:]:
                    print('\t' * (depth + 1), f"{self.name}: {line}")
            else:
                print('\t' * depth, f"{self.name}: {print_data}")
        else:
            print('\t' * depth, f"{self.name}: {data}")

    def unpack(self, data):
        if self.length == 0:
            return (self.name, data), len(data)
        if self.fmt == "":
            return (self.name, data[:self.length]), self.length
        try:
            return (self.name, struct.unpack(self.fmt, data[:self.length])[0]), self.length
        except Exception as e:
            raise MetaStructParseError(f"Failure while parsing {self.name}") from e


class BERField(Field):
    def __init__(self, name, fmt, datatype, print_fmt=None, dynamic_fmt=False, explicit=False):
        super().__init__(name, fmt, 0, print_fmt)
        self.datatype = datatype
        self.length = 0
        self.dynamic_fmt = dynamic_fmt
        self.explicit = explicit

    def pack(self, data):
        if self.fmt:
            data = struct.pack(self.fmt, data)
        if self.datatype < 0xff:
            type_field = struct.pack("B", self.datatype)
        else:
            type_field = struct.pack(">H", self.datatype)
        if len(data) > 0x7f:
            len_bytelen = math.ceil(len(data).bit_length() / 8)
            len_spec = struct.pack("B", 0x80 + len_bytelen)
            len_bytes = len_spec + len(data).to_bytes(len_bytelen, "big")
        else:
            len_bytes = struct.pack("B", len(data))
        return type_field + len_bytes + data

    def unpack_header(self, data):
        ind = 0
        ind += 2 if data[0] & 0x1f == 0x1f else 1

        if data[ind] & 0x80:
            bytelen = data[ind] - 0x80
            datalen = int.from_bytes(data[ind + 1: ind + bytelen + 1], "big")
            ind += bytelen + 1
        else:
            datalen = data[ind]
            ind += 1
        return ind, datalen

    def unpack(self, data):
        try:
            ind, datalen = self.unpack_header(data)
            if self.explicit:
                ind_inner, datalen = self.unpack_header(data[ind:ind + datalen])
                ind += ind_inner
            if self.dynamic_fmt:
                return (self.name, int.from_bytes(data[ind:ind + datalen], "little" if "<" in self.fmt else "big")), datalen + ind
            if self.fmt:
                return (self.name, struct.unpack(self.fmt, data[ind:ind + datalen])[0]), datalen + ind
            return (self.name, data[ind:ind + datalen]), datalen + ind
        except Exception as e:
            raise MetaStructParseError(f"Failure while parsing {self.name}") from e

    
class BERSequence(BERField):
    def __init__(self, name, datatype, fields, explicit=False):
        super().__init__(name, "", datatype, explicit=explicit)
        self.fields = fields
        self.length = 0

    def pack(self, args):
        ret = b""
        for field, arg in zip(self.fields, args):
            val = field.pack(arg)
            ret += val
        return super().pack(ret)

    def format(self, data, depth):
        _, data = data
        print('\t' * depth, f"{self.name}")
        for field, value in zip(self.fields, data):
            field.format(value, depth + 1)

    def unpack(self, data):
        try:
            ind, datalen = self.unpack_header(data)
            if self.explicit:
                ind_inner, datalen = self.unpack_header(data[ind:ind + datalen])
                ind += ind_inner
            end = ind + datalen
            ret = []
            for field in self.fields:
                n, l = field.unpack(data[ind:])
                ret.append(n)
                ind += l
            return (self.name, ret), ind
        except Exception as e:
            raise MetaStructParseError(f"Parse Error while parsing {self.name}") from e


class TerminatedField(Field):
    def __init__(self, name, sequence):
        super().__init__(name, "", 0)
        self.sequence = sequence

    def pack(self, data):
        return data + self.sequence

    def unpack(self, data):
        seq_ind = data.find(self.sequence)
        return (self.name, data[:seq_ind]), seq_ind + len(self.sequence)


def strip_zeroes(data):
    return data.strip(b"\x00")

def deinterlace_zeroes(data):
    return data[::2].strip(b"\x00")

def interlace_zeroes(data, fill):
    return "".join([c + "\x00" for c in data]).ljust(fill, "\x00").encode()

def lookup_format(dct):
    def fmt(x):
        if isinstance(dct, type) and issubclass(dct, enum.Enum):
            try: 
                name = dct(x).name
            except ValueError:
                name = "Unknown"
            return f"{name} ({hex(x)})" 
        else:
            return f"{dct[x]} ({hex(x)})" if x in dct else f"Unknown ({hex(x)})"
    return fmt 

def format_flags_inner(data, dct):
    ret = []
    for key in dct:
        if data & key:
            ret.append(f"{hex(key)} - {dct[key]}")
    ret = [data] + ret if ret else (0 if data == 0 else hex(data))
    return ret

def format_flags(dct):
    return lambda x: format_flags_inner(x, dct)
