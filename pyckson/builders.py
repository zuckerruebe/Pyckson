from inspect import Parameter, getmembers, signature

from pyckson.const import PYCKSON_TYPEINFO
from pyckson.helpers import get_name_rule
from pyckson.model import PycksonAttribute, PycksonModel
from pyckson.parser import get_parser
from pyckson.serializer import get_serializer


class PycksonModelBuilder:
    def __init__(self, cls):
        self.cls = cls
        self.type_info = getattr(cls, PYCKSON_TYPEINFO, dict())
        self.name_rule = get_name_rule(cls)

    def find_constructor(self):
        for member in getmembers(self.cls):
            if member[0] == '__init__':
                return member[1]
        else:
            raise ValueError('no constructor_found')

    def build_model(self) -> PycksonModel:
        constructor = self.find_constructor()
        attributes = []
        for name, parameter in signature(constructor).parameters.items():
            if name != 'self':
                attribute = self.build_attribute(parameter)
                attributes.append(attribute)
        return PycksonModel(attributes)

    def build_attribute(self, parameter: Parameter) -> PycksonAttribute:
        python_name = parameter.name
        json_name = self.name_rule(parameter.name)
        optional = parameter.default is not Parameter.empty
        if parameter.annotation is Parameter.empty:
            raise TypeError('parameter {} in class {} has no type'.format(parameter.name, self.cls.__name__))
        if parameter.kind != Parameter.POSITIONAL_OR_KEYWORD:
            raise TypeError('pyckson only handle named parameters')
        return PycksonAttribute(python_name, json_name, parameter.annotation, optional,
                                get_serializer(parameter.annotation, self.cls, python_name),
                                get_parser(parameter.annotation, self.cls, python_name))
