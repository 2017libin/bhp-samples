print("嗨客网(www.haicoder.net)")
class Person(object):
    def __new__(cls, *args, **kwargs):
        print("call Person __new__()")
        instance = super().__new__(cls)
        return instance

class Student(object):
    def __new__(cls, *args, **kwargs):
        print("call Student __new__()")
        instance = object.__new__(Person, *args, **kwargs)
        return instance
stu = Student()
print("Type stu =", type(stu))