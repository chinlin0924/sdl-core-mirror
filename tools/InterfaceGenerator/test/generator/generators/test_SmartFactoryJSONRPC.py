"""Test for JSONRPC SmartFactory generator.

Verifies format specific functions and produced source code.

"""
import codecs
import collections
import os
import unittest
import uuid
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import call

import sys

sys.path.append(Path(__file__).absolute().parents[3].as_posix())
sys.path.append(Path(__file__).absolute().parents[4].joinpath('rpc_spec/InterfaceParser').as_posix())
try:
    from generator.generators import SmartFactoryJSONRPC
    from model.array import Array
    from model.boolean import Boolean
    from model.float import Float
    from model.enum import Enum
    from model.enum_element import EnumElement
    from model.enum_subset import EnumSubset
    from model.function import Function
    from model.integer import Integer
    from model.interface import Interface
    from model.issue import Issue
    from model.param import Param
    from model.struct import Struct
except ModuleNotFoundError as error:
    print('{}.\nProbably you did not initialize submodule'.format(error))
    sys.exit(1)

EXPECTED_RESULT_REQUEST = (
    u"""params_members[ns_smart_device_link::ns_json_handler::"""
    u"""strings::S_FUNCTION_ID] = SMember("""
    u"""TEnumSchemaItem<FunctionID::eType>::create("""
    u"""function_id_items), true);\n"""
    u"""params_members[ns_smart_device_link::ns_json_handler::"""
    u"""strings::S_MESSAGE_TYPE] = SMember("""
    u"""TEnumSchemaItem<messageType::eType>::create("""
    u"""message_type_items), true);\n"""
    u"""params_members[ns_smart_device_link::ns_json_handler::"""
    u"""strings::S_PROTOCOL_VERSION] = SMember("""
    u"""TNumberSchemaItem<int>::create(), true);\n"""
    u"""params_members[ns_smart_device_link::ns_json_handler::"""
    u"""strings::S_PROTOCOL_TYPE] = SMember("""
    u"""TNumberSchemaItem<int>::create(), true);\n"""
    u"""params_members[ns_smart_device_link::ns_json_handler::"""
    u"""strings::S_CORRELATION_ID] = SMember("""
    u"""TNumberSchemaItem<int>::create(), true);\n"""
)

EXPECTED_RESULT_RESPONSE = (
    u"""params_members[ns_smart_device_link::ns_json_handler::"""
    u"""strings::S_FUNCTION_ID] = SMember("""
    u"""TEnumSchemaItem<FunctionID::eType>::create("""
    u"""function_id_items), true);\n"""
    u"""params_members[ns_smart_device_link::ns_json_handler::"""
    u"""strings::S_MESSAGE_TYPE] = SMember("""
    u"""TEnumSchemaItem<messageType::eType>::create("""
    u"""message_type_items), true);\n"""
    u"""params_members[ns_smart_device_link::ns_json_handler::"""
    u"""strings::S_PROTOCOL_VERSION] = SMember("""
    u"""TNumberSchemaItem<int>::create(), true);\n"""
    u"""params_members[ns_smart_device_link::ns_json_handler::"""
    u"""strings::S_PROTOCOL_TYPE] = SMember("""
    u"""TNumberSchemaItem<int>::create(), true);\n"""
    u"""params_members[ns_smart_device_link::ns_json_handler::"""
    u"""strings::S_CORRELATION_ID] = SMember("""
    u"""TNumberSchemaItem<int>::create(), true);\n"""
    u"""params_members[ns_smart_device_link::ns_json_handler::"""
    u"""strings::kCode] = SMember("""
    u"""TNumberSchemaItem<int>::create(), true);\n"""
)

EXPECTED_RESULT_NOTIFICATION = (
    u"""params_members[ns_smart_device_link::ns_json_handler::"""
    u"""strings::S_FUNCTION_ID] = SMember("""
    u"""TEnumSchemaItem<FunctionID::eType>::create("""
    u"""function_id_items), true);\n"""
    u"""params_members[ns_smart_device_link::ns_json_handler::"""
    u"""strings::S_MESSAGE_TYPE] = SMember("""
    u"""TEnumSchemaItem<messageType::eType>::create("""
    u"""message_type_items), true);\n"""
    u"""params_members[ns_smart_device_link::ns_json_handler::"""
    u"""strings::S_PROTOCOL_VERSION] = SMember("""
    u"""TNumberSchemaItem<int>::create(), true);\n"""
    u"""params_members[ns_smart_device_link::ns_json_handler::"""
    u"""strings::S_PROTOCOL_TYPE] = SMember("""
    u"""TNumberSchemaItem<int>::create(), true);\n"""
)

EXPECTED_PRE_FUNCTION_CODE = (
    u"""  std::map<std::string, SMember> """
    u"""params_members;\n"""
    u"""  params_members[ns_smart_device_link::ns_json_handler::"""
    u"""strings::S_FUNCTION_ID] = SMember("""
    u"""TEnumSchemaItem<FunctionID::eType>::create("""
    u"""function_id_items), true);\n"""
    u"""  params_members[ns_smart_device_link::ns_json_handler::"""
    u"""strings::S_MESSAGE_TYPE] = SMember("""
    u"""TEnumSchemaItem<messageType::eType>::create("""
    u"""message_type_items), true);\n"""
    u"""  params_members[ns_smart_device_link::ns_json_handler::"""
    u"""strings::S_PROTOCOL_VERSION] = SMember("""
    u"""TNumberSchemaItem<int>::create(), true);\n"""
    u"""  params_members[ns_smart_device_link::ns_json_handler::"""
    u"""strings::S_PROTOCOL_TYPE] = SMember("""
    u"""TNumberSchemaItem<int>::create(), true);\n"""
    u"""  params_members[ns_smart_device_link::ns_json_handler::"""
    u"""strings::S_CORRELATION_ID] = SMember("""
    u"""TNumberSchemaItem<int>::create(), true);\n"""
    u"""  params_members[ns_smart_device_link::ns_json_handler"""
    u"""::strings::kCode] = SMember("""
    u"""TNumberSchemaItem<int>::create(), true);\n"""
    u"""  params_members[ns_smart_device_link::ns_json_handler::"""
    u"""strings::kMessage] = SMember("""
    u"""CStringSchemaItem::create(), true);\n"""
    u"""\n"""
    u"""  std::map<std::string, SMember> """
    u"""root_members_map;\n"""
    u"""  root_members_map[ns_smart_device_link::ns_json_handler::"""
    u"""strings::S_PARAMS] = SMember("""
    u"""CObjectSchemaItem::create(params_members), true);\n"""
    u"""\n"""
    u"""  CSmartSchema error_response_schema(CObjectSchemaItem::create("""
    u"""root_members_map));\n"""
    u"""\n"""
    u"""  functions_schemes_.insert(std::make_pair("""
    u"""ns_smart_device_link::ns_json_handler::SmartSchemaKey<"""
    u"""FunctionID::eType, messageType::eType>("""
    u"""FunctionID::request, messageType::error_response)"""
    u""", error_response_schema));\n"""
    u"""\n"""
)

DESCRIPTION = [u"Description Line1", u"Description Line2"]

DESIGN_DESCRIPTION = [u"Design Line1"]

ISSUES = [Issue(value=u"Issue1"),
          Issue(value=u"Issue2"),
          Issue(value=u"Issue3")]

TODOS = [u"Do1", u"Do2"]


class Test(unittest.TestCase):
    """Test for JSONRPC SmartFactory generator.

    This class holds set of test cases for the JSONRPC SmartFactory generator.

    """

    def test_gen_schema_params_fill(self):
        """Test feature that allows to create format specific PARAMS.

        Verifies JSONRPC implementation of the _gen_schema_params_fill
        method.

        """
        generator = SmartFactoryJSONRPC.CodeGenerator()

        self.assertEqual(generator._gen_schema_params_fill("request"),
                         EXPECTED_RESULT_REQUEST,
                         "Invalid code generation for request")

        self.assertEqual(generator._gen_schema_params_fill(u"request"),
                         EXPECTED_RESULT_REQUEST,
                         "Invalid code generation for request")

        self.assertEqual(generator._gen_schema_params_fill("response"),
                         EXPECTED_RESULT_RESPONSE,
                         "Invalid code generation for response")

        self.assertEqual(generator._gen_schema_params_fill(u"response"),
                         EXPECTED_RESULT_RESPONSE,
                         "Invalid code generation for response")

        self.assertEqual(generator._gen_schema_params_fill("notification"),
                         EXPECTED_RESULT_NOTIFICATION,
                         "Invalid code generation for notification")

        self.assertEqual(generator._gen_schema_params_fill(u"notification"),
                         EXPECTED_RESULT_NOTIFICATION,
                         "Invalid code generation for notification")

    def test_preprocess_message_type(self):
        """Test preprocessing of the message_type enum.

        Verifies JSONPRC implementation of the _preprocess_message_type
        function.

        """

        generator = SmartFactoryJSONRPC.CodeGenerator()

        message_type_elements = collections.OrderedDict()
        message_type_elements[u"request"] = EnumElement(name=u"request")
        message_type_elements[u"response"] = EnumElement(
            name=u"response")
        message_type_elements[u"notification"] = EnumElement(
            name=u"notification")

        message_type = Enum(name=u"messageType",
                            elements=message_type_elements)

        result_enum = generator._preprocess_message_type(message_type)

        self.assertIn("error_response", result_enum.elements)
        self.assertEqual("error_response",
                         result_enum.elements["error_response"].primary_name)

        message_type_elements = collections.OrderedDict()
        message_type_elements[u"request"] = EnumElement(name=u"request")
        message_type_elements[u"notification"] = EnumElement(
            name=u"notification")

        message_type = Enum(name=u"messageType",
                            elements=message_type_elements)

        result_enum = generator._preprocess_message_type(message_type)

        self.assertNotIn("error_response", result_enum.elements)

    def test_gen_pre_function_schemas(self):
        """Test code that goes before schema initialization.

        Verifies JSONPRC implementation of the _gen_pre_function_schemas
        function.

        """
        self.maxDiff = None

        generator = SmartFactoryJSONRPC.CodeGenerator()

        self.assertEqual(u"",
                         generator._gen_pre_function_schemas([]),
                         "Invalid code for empty functions list")

        message_type_elements = collections.OrderedDict()
        message_type_elements[u"request"] = EnumElement(name=u"request")
        message_type_elements[u"response"] = EnumElement(
            name=u"response")
        message_type_elements[u"notification"] = EnumElement(
            name=u"notification")

        message_type = Enum(name=u"messageType",
                            elements=message_type_elements)

        function1 = Function(
            "func1", function_id=message_type.elements[u"request"],
            message_type=message_type.elements[u"request"])

        self.assertEqual(u"",
                         generator._gen_pre_function_schemas([function1]),
                         "Invalid code for empty functions list")

        function2 = Function(
            "func2", function_id=message_type.elements[u"request"],
            message_type=message_type.elements[u"response"])
        try:
            self.assertEqual(EXPECTED_PRE_FUNCTION_CODE,
                             generator._gen_pre_function_schemas([function2]),
                             "Invalid code for single response function")

            self.assertEqual(EXPECTED_PRE_FUNCTION_CODE,
                             generator._gen_pre_function_schemas([function1,
                                                                  function2]),
                             "Invalid code for mixed function list")
        except AssertionError as message:
            print(message)

    def test_full_generation(self):
        """Test full generation using JSONRPC SmartSchema generator.

        Creates output files which is captured by the mock and compare them
        with sample files with correct code. This test requires valid
        test_expected_jsonrpc.h and test_expected_jsonrpc.cc in the same
        directory as this module.

        """
        self.maxDiff = None
        expected_h_file_content = Path(__file__).parents[0].joinpath("test_expected_jsonrpc.h").read_text()
        expected_cc_file_content = Path(__file__).parents[0].joinpath("test_expected_jsonrpc.cc").read_text()

        generator = SmartFactoryJSONRPC.CodeGenerator()

        message_type_elements = collections.OrderedDict()
        message_type_elements[u"request"] = EnumElement(name=u"request")
        message_type_elements[u"response"] = EnumElement(
            name=u"response")
        message_type_elements[u"notification"] = EnumElement(
            name=u"notification")

        message_type = Enum(name=u"messageType",
                            elements=message_type_elements)

        elements1 = collections.OrderedDict()
        elements1[u"name1"] = EnumElement(
            name=u"name1",
            design_description=DESIGN_DESCRIPTION,
            todos=TODOS,
            value=u"1")
        elements1[u"name2"] = EnumElement(
            name="name2",
            description=DESCRIPTION,
            issues=ISSUES,
            internal_name=u"internal_name2")

        enum1 = Enum(name=u"Enum1",
                     todos=TODOS,
                     elements=elements1)

        elements2 = collections.OrderedDict()
        elements2[u"xxx"] = EnumElement(name=u"xxx",
                                        internal_name=u"val_1")
        elements2[u"yyy"] = EnumElement(name=u"yyy",
                                        internal_name=u"val_2",
                                        value=u"100")
        elements2[u"zzz"] = EnumElement(name=u"val_3")

        enum2 = Enum(name=u"E2",
                     elements=elements2)

        elements3 = collections.OrderedDict()
        elements3["1"] = EnumElement(name="xxx",
                                     internal_name="_1")
        elements3["2"] = EnumElement(name="xxx",
                                     internal_name="_2")
        elements3["3"] = EnumElement(name="xxx",
                                     internal_name="_3")
        enum3 = Enum(name="Enum_new2",
                     elements=elements3)

        elements4 = collections.OrderedDict()
        elements4["name1"] = EnumElement(name="xxx",
                                         internal_name="_11")
        elements4["name2"] = EnumElement(name="xxx",
                                         internal_name="_22")
        enum4 = Enum(name="Enum_new4",
                     elements=elements4)

        enums = collections.OrderedDict()
        enums["Enum1"] = enum1
        enums["Enum2"] = enum2
        enums["Enum3"] = enum3
        enums["Enum4"] = enum4
        enums["messageType"] = message_type

        params1 = collections.OrderedDict()
        params1["1"] = Param(
            name="param1",
            design_description=DESIGN_DESCRIPTION,
            description=DESCRIPTION,
            issues=ISSUES,
            todos=TODOS,
            param_type=enum4,
            default_value=elements4["name1"])
        params1["2"] = Param(
            name="param2",
            param_type=EnumSubset(
                name="sub1",
                enum=enum1,
                allowed_elements={"e1": elements1["name1"]}),
            default_value=elements1["name1"])

        functions = collections.OrderedDict()
        functions["Function1"] = Function(
            name="Function1",
            function_id=elements1["name1"],
            message_type=message_type_elements["request"],
            params=params1)
        functions["Function2"] = Function(
            name="Function2",
            function_id=elements2["xxx"],
            message_type=message_type_elements["response"])
        functions["Function3"] = Function(
            name="Function2",
            function_id=elements2["yyy"],
            message_type=message_type_elements["notification"])

        members1 = collections.OrderedDict()
        members1["m1"] = Param(name="intParam",
                               param_type=Integer(max_value=2))
        members1["m11"] = Param(name="doubleParam",
                                param_type=Float(min_value=0.333),
                                is_mandatory=False)
        members1["m222"] = Param(name="boolParam",
                                 param_type=Boolean())
        members1["m2"] = Param(name="structParam",
                               param_type=Struct(name="Struct2"))
        members1["aaa"] = Param(name="enumParam",
                                param_type=enum1)
        members1["bbb"] = Param(name="enumParam1",
                                param_type=enum1)
        members1["xxx"] = Param(
            name="enumSubset1",
            param_type=EnumSubset(
                name="sub",
                enum=enum1,
                allowed_elements={"e1": elements1["name1"]}),
            is_mandatory=False)
        members1["1"] = Param(
            name="arrayOfInt",
            param_type=Array(min_size=0,
                             max_size=20,
                             element_type=Boolean()),
            is_mandatory=False)
        members1["2"] = Param(
            name="arrayOfEnum1",
            param_type=Array(min_size=0,
                             max_size=20,
                             element_type=enum1),
            is_mandatory=False)
        members1["3"] = Param(
            name="arrayOfEnum3",
            param_type=Array(min_size=10,
                             max_size=40,
                             element_type=enum3),
            is_mandatory=True)
        members1["4"] = Param(
            name="arrayOfEnum4",
            param_type=Array(
                min_size=10,
                max_size=41,
                element_type=EnumSubset(
                    name="sub1",
                    enum=enum1,
                    allowed_elements={"e1": elements1["name1"]})))
        members1["5"] = Param(
            name="arrayOfEnum5",
            param_type=Array(
                min_size=10,
                max_size=42,
                element_type=EnumSubset(
                    name="sub2",
                    enum=enum1,
                    allowed_elements={"e1": elements1["name2"]})))
        members1["6"] = Param(
            name="arrayOfEnum6",
            param_type=Array(
                min_size=10,
                max_size=43,
                element_type=EnumSubset(
                    name="sub3",
                    enum=enum4,
                    allowed_elements={"e1": elements4["name2"]})))

        structs = collections.OrderedDict()
        structs["Struct1"] = Struct(
            name="Struct1",
            design_description=DESIGN_DESCRIPTION,
            issues=ISSUES,
            members=members1)
        structs["Struct2"] = Struct(name="Struct2",
                                    issues=ISSUES)

        interface = Interface(enums=enums,
                              structs=structs,
                              functions=functions,
                              params={"param1": "value1",
                                      "param2": "value2"})

        os.path.exists = MagicMock(return_value=True)
        uuid.uuid1 = MagicMock(
            return_value=uuid.UUID("12345678123456781234567812345678"))
        codecs.open = MagicMock()

        generator.generate(interface=interface,
                           filename="Test.xml",
                           namespace="XXX::YYY::ZZZ",
                           destination_dir="/some/test/dir")

        os.path.exists.assert_has_calls([call('/some/test/dir')])

        open_result = codecs.open
        mock_calls = open_result.mock_calls

        self.assertEqual(mock_calls[0],
                         call('/some/test/dir/Test.h',
                              mode='w',
                              encoding='utf-8'),
                         "Invalid header file creation")

        self.assertEqual(mock_calls[4],
                         call('/some/test/dir/Test_schema.h',
                              mode='w',
                              encoding='utf-8'),
                         "Invalid source file creation")
        try:
            self.assertSequenceEqual(str(mock_calls[2])[27:-2].replace("\\n", "\n"),
                                     expected_h_file_content,
                                     "Invalid header file content")

            self.assertSequenceEqual(str(mock_calls[6])[27:-2].replace("\\n", "\n"),
                                     expected_cc_file_content,
                                     "Invalid source file content")
        except AssertionError as message:
            print(message)


if __name__ == '__main__':
    unittest.main()
