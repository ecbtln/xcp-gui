class InvalidRPCCall(Exception):
    pass


class InvalidRPCMethod(InvalidRPCCall):
    pass


class InvalidRPCArguments(InvalidRPCCall):
    pass


class RPCError(Exception):
    pass

