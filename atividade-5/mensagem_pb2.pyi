from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Ack(_message.Message):
    __slots__ = ("recebido",)
    RECEBIDO_FIELD_NUMBER: _ClassVar[int]
    recebido: bool
    def __init__(self, recebido: bool = ...) -> None: ...

class EnviarDadosParams(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: str
    def __init__(self, data: _Optional[str] = ...) -> None: ...

class EnviarDadosResult(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class ConsultarDadosParams(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConsultarDadosResult(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[Log]
    def __init__(self, entries: _Optional[_Iterable[_Union[Log, _Mapping]]] = ...) -> None: ...

class Log(_message.Message):
    __slots__ = ("epoch", "offset", "data")
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    epoch: int
    offset: int
    data: str
    def __init__(self, epoch: _Optional[int] = ..., offset: _Optional[int] = ..., data: _Optional[str] = ...) -> None: ...
