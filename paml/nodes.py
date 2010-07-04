            
import cgi

class Base(object):
    
    def __init__(self):
        self.children = []
    
    def render_start(self, engine):
        return None
    
    def render_content(self, engine):
        return []
    
    def render_end(self, engine):
        return None
    
    def __repr__(self):
        return '<%s at 0x%x>' % (self.__class__.__name__, id(self))


class Document(Base):
    
    def render_start(self, engine):
        yield engine.start_document()


class Content(Base):
    
    def __init__(self, content):
        super(Content, self).__init__()
        self.content = content
    
    def render_start(self, engine):
        yield engine.indent()
        yield self.content
        yield engine.endl
    
    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.content)


class Expression(Content):
    
    def render_start(self, engine):
        yield engine.indent()
        yield '${%s}' % self.content.strip()
        yield engine.endl


class Tag(Base):
    
    self_closing_names = set('''
        br
        hr
        img
        input
        link
        meta
    '''.strip().split())
    
    def __init__(self, name, id, class_, kwargs_expr=None, self_closing=False,
        strip_inner=False, strip_outer=False):
        
        super(Tag, self).__init__()
        
        self.name = (name or 'div').lower()
        self.id = id
        self.class_ = (class_ or '').replace('.', ' ').strip()
        self.kwargs_expr = kwargs_expr
        self.self_closing = self_closing
        self.strip_inner = strip_inner
        self.strip_outer = strip_outer
        
        self.inline_child = None
    
    def render_start(self, engine):
        
        const_attrs = {}
        if self.id:
            const_attrs['id'] = self.id
        if self.class_:
            const_attrs['class'] = self.class_
        
        if not self.kwargs_expr:
            attr_str = ''.join(' %s="%s"' % (k, cgi.escape(v)) for k, v in const_attrs.items())
        elif not const_attrs:
            attr_str = '<%% __M_writer(__P_attrs(%s)) %%>' % self.kwargs_expr
        else:
            attr_str = '<%% __M_writer(__P_attrs(%r, %s)) %%>' % (const_attrs, self.kwargs_expr)
        
        if self.strip_outer:
            yield engine.lstrip
        else:
            yield engine.indent()
        
        if self.self_closing or self.name in self.self_closing_names:
            yield '<%s%s />' % (self.name, attr_str)
            if self.strip_outer:
                yield engine.rstrip
            else:
                yield engine.endl
        else:
            yield '<%s%s>' % (self.name, attr_str)
            if self.children:
                if self.strip_inner:
                    yield engine.rstrip
                else:
                    yield engine.endl
                    yield engine.inc_depth
        
        if self.inline_child:
            yield engine.no_whitespace
            for x in self.inline_child.render_start(engine):
                yield x
            yield engine.pop_whitespace
    
    def render_end(self, engine):
        if self.strip_inner:
            yield engine.lstrip
        if not (self.self_closing or self.name in self.self_closing_names):
            if self.children:
                yield engine.dec_depth
                yield engine.indent()
            yield '</%s>' % self.name
            if self.strip_outer:
                yield engine.rstrip
            else:
                yield engine.endl
        elif self.strip_outer:
            yield engine.rstrip
    
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__,
            ', '.join('%s=%r' % (k, getattr(self, k)) for k in (
                'name', 'id', 'class_', 'kwargs_expr', 'inline_child',
                'strip_inner', 'strip_outer'
            ) if getattr(self, k))
        )


class Comment(Base):
    
    def render_start(self, engine):
        yield '<!--'
    
    def render_end(self, engine):
        yield '-->'
    
    def __repr__(self):
        yield '%s()' % self.__class__.__name__


class Control(Base):
    
    def __init__(self, type, test):
        super(Control, self).__init__()
        self.type = type
        self.test = test
    
    def render_start(self, engine):
        yield engine.assert_newline
        yield engine.indent(-1)
        yield '%% %s %s: ' % (self.type, self.test)
        yield engine.endl
    
    def render_end(self, engine):
        yield engine.assert_newline
        yield engine.indent(-1)
        yield '%% end%s' % self.type
        yield engine.endl
    
    def __repr__(self):
        return '%s(type=%r, test=%r)' % (
            self.__class__.__name__,
            self.type,
            self.test
        )
    