# -*- coding: utf-8 -*-

from construct import *

class ControlChain():
    def __init__(self):
        connection = Struct("connection",
            CString("name"),
            Byte("channel")
        )

        device_descriptor = Struct("dev_desc",
            Byte("channels_count"),
            Enum(Byte("mask_prop_size"), UI08 = 1, UI16 = 2, UI32 = 4),
            Byte("actuators_count"),
            Array(lambda ctx: ctx.actuators_count,
                Struct("actuator",
                    CString("name"),
                    Byte("masks_props_count"),
                    Array(lambda ctx: ctx.masks_props_count,
                        Struct("mask",
                            Switch("prop", lambda ctx: ctx._._.mask_prop_size,
                               {"UI08": ULInt8("spam"), "UI16": ULInt16("spam"), "UI32": ULInt32("spam")}),
                            CString("label")
                        )
                    ),
                    Byte("type"),
                    Byte("steps_count"),
                    Array(lambda ctx: ctx.steps_count, ULInt16("steps"))
                )
            )
        )

        control_addressing = Struct("control_addressing",
            ULInt16("resp_status")
        )

        control_unaddressing = Struct("control_unaddressing",
            ULInt16("resp_status")
        )

        data_request = Struct("data_request",
            Byte("channel"),
            Byte("actuators_count"),
                Array(lambda ctx: ctx.actuators_count,
                    Struct("actuator",
                        Byte("id"),
                        LFloat32("value")
                    )
                )
        )

        self._parser = Struct("parser",
            Byte("sync"),
            Byte("destination"),
            Byte("origin"),
            Byte("function"),
            ULInt16("data_size"),
            If(lambda ctx: ctx["function"] == 1, connection),
            If(lambda ctx: ctx["function"] == 2, device_descriptor),
            If(lambda ctx: ctx["function"] == 3, control_addressing),
            If(lambda ctx: ctx["function"] == 4, data_request),
            If(lambda ctx: ctx["function"] == 5, control_unaddressing),
            Byte("checksum"),
            Byte("end")
        )

    def __checksum(self, buffer, size):
        check = 0
        for i in range(size):
            check += ord(buffer[i])
            check &= 0xFF

        if check == 0x00 or check == 0xAA:
            return (~check & 0xFF)

        return check

    def build(self, obj):
        return self._parser.build(obj)

    def connection(self, destination, origin, name, channel):
        pass

    def device_descriptor(self):
        def encoder(obj, ctx):
            return Container()

        def decoder(obj, ctx):
            pass

    def parse(self, buffer):
        buffer+="\x00"
        buffer = buffer.replace("\x1b\xff", "\x00")
        buffer = buffer.replace("\x1b\x55", "\xaa")
        buffer = buffer.replace("\x1b\x1b", "\x1b")

        return self._parser.parse(buffer)