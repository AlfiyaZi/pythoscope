from pythoscope.astbuilder import parse
from pythoscope.code_trees_manager import CodeTreeNotFound
from pythoscope.store import Class, Function, Method, Module, CodeTree,\
    TestClass, TestMethod, code_of, module_of
from pythoscope.generator.adder import add_test_case

from assertions import *
from helper import CustomSeparator, EmptyProject


class TestModule:
    def setUp(self):
        self.project = EmptyProject()
        self.module = self.project.create_module("module.py", code=parse("# only comments"))
        self.test_class = TestClass(name="TestSomething", code=parse("# some test code"))

    def test_can_add_test_cases_to_empty_modules(self):
        add_test_case(self.module, self.test_class)
        # Make sure it doesn't raise any exceptions.

    def test_adding_a_test_case_adds_it_to_list_of_objects(self):
        add_test_case(self.module, self.test_class)

        assert_equal([self.test_class], self.module.objects)

    def test_test_cases_can_be_added_using_add_objects_method(self):
        test_class_1 = TestClass(name="TestSomethingElse")
        test_class_2 = TestClass(name="TestSomethingCompletelyDifferent")
        self.module.add_objects([test_class_1, test_class_2])

        assert_equal([test_class_1, test_class_2], self.module.objects)
        assert_equal([test_class_1, test_class_2], self.module.test_cases)

    def test_module_with_errors_doesnt_get_a_code_tree(self):
        module = self.project.create_module("module_with_errors.py", errors=[Exception()])
        assert_raises(CodeTreeNotFound, lambda: CodeTree.of(module))

class TestStoreWithCustomSeparator(CustomSeparator):
    def test_uses_system_specific_path_separator(self):
        module = Module(subpath="some#path.py", project=EmptyProject())
        assert_equal("some.path", module.locator)

class TestModuleOf:
    def setUp(self):
        project = EmptyProject()
        self.module = Module(project=project, subpath='module.py')
        self.klass = Class('Klass', module=self.module)
        self.tclass = TestClass('TClass', parent=self.module)

    def test_module_of_for_module(self):
        assert_equal(self.module, module_of(self.module))

    def test_module_of_for_function(self):
        fun = Function('fun', module=self.module)
        assert_equal(self.module, module_of(fun))

    def test_module_of_for_class(self):
        assert_equal(self.module, module_of(self.klass))

    def test_module_of_for_method(self):
        meth = Method('meth', klass=self.klass)
        assert_equal(self.module, module_of(meth))

    def test_module_of_for_test_classes(self):
        assert_equal(self.module, module_of(self.tclass))

    def test_module_of_for_test_methods(self):
        tmeth = TestMethod('tmeth', parent=self.tclass)
        assert_equal(self.module, module_of(tmeth))

class TestCodeOf:
    def setUp(self):
        project = EmptyProject()
        self.code = object() # A unique fake object.
        self.module = Module(project=project, subpath='module.py')
        self.code_tree = CodeTree(self.code)
        project.remember_code_tree(self.code_tree, self.module)

    def test_code_of_module(self):
        assert_equal(self.code, code_of(self.module))

    def test_code_of_function(self):
        function = Function('fun', module=self.module)
        function_code = object()
        self.code_tree.add_object(function, function_code)

        assert_equal(function_code, code_of(function))

    def test_code_of_class(self):
        klass = Class('Class', module=self.module)
        class_code = object()
        self.code_tree.add_object(klass, class_code)

        assert_equal(class_code, code_of(klass))

    def test_code_of_method(self):
        klass = Class('Class', module=self.module)
        method = Method('method', klass=klass)
        method_code = object()
        self.code_tree.add_object(method, method_code)

        assert_equal(method_code, code_of(method))

    def test_code_of_test_class(self):
        test_class = TestClass('TestClass', parent=self.module)
        test_class_code = object()
        self.code_tree.add_object(test_class, test_class_code)

        assert_equal(test_class_code, code_of(test_class))

    def test_code_of_test_method(self):
        test_class = TestClass('TestClass', parent=self.module)
        test_method = TestMethod('test_method', parent=test_class)
        test_method_code = object()
        self.code_tree.add_object(test_method, test_method_code)

        assert_equal(test_method_code, code_of(test_method))

class TestCodeTree:
    def test_instance_is_accesible_from_the_moment_it_is_created(self):
        project = EmptyProject()
        mod = Module(project=project, subpath='module.py')
        ct = CodeTree(None)
        project.remember_code_tree(ct, mod)

        assert_equal(ct, CodeTree.of(mod))

    def test_removal_of_a_module_removes_its_code_tree(self):
        project = EmptyProject()
        mod = project.create_module('module.py')
        ct = CodeTree(None)
        project.remember_code_tree(ct, mod)

        project.remove_module(mod.subpath)

        assert_raises(CodeTreeNotFound, lambda: CodeTree.of(mod))
