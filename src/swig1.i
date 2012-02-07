%module FirstTest

%{
    class Foo {
        public:
        virtual ~Foo();
        virtual int Fn();
/*        virtual int Bar();*/
    };
%}

class Foo {
    public:
    virtual ~Foo();
    virtual int Fn();
/*    virtual int Bar();*/
};

