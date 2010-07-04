
from unittest import TestCase, main

from mako.template import Template
import paml


class TestTheTester(TestCase):
    
    def test_pass(self):
        self.assertTrue(True, 'It works!')

class Base(TestCase):
    
    def assertMako(self, source, expected, *args):
        node = paml.parse_string(source)
        mako = paml.generate_mako(node).replace('<%! from paml.codegen import mako_build_attr_str as __P_attrs %>\\\n', '')
        self.assertEqual(mako, expected.replace('    ', '\t'), *args)
        
    def assertHTML(self, source, expected, *args, **kwargs):
        node = paml.parse_string(source)
        mako = paml.generate_mako(node)
        html = Template(mako).render_unicode(**kwargs)
        self.assertEqual(html, expected.replace('    ', '\t'), *args)




class TestHamlTutorial(Base):
    
    """Testing all of the examples from http://haml-lang.com/tutorial.html"""
    
    def test_1(self):
        self.assertMako(
            '%strong= item.title',
            '<strong>${item.title}</strong>\n'
        )
    
    def test_2(self):
        self.assertHTML(
            '%strong(class_="code", id="message") Hello, World!',
            '<strong id="message" class="code">Hello, World!</strong>\n'
        )

    def test_2b(self):
        self.assertHTML(
            '%strong.code#message Hello, World!',
            '<strong id="message" class="code">Hello, World!</strong>\n'
        )
            
    def test_3(self):
        self.assertHTML(
            '.content Hello, World!',
            '<div class="content">Hello, World!</div>\n'
        )

    def test_4(self):
        class obj(object):
            pass
        item = obj()
        item.id = 123
        item.body = 'Hello, World!'
        self.assertHTML(
            '.item(id="item-%d" % item.id)= item.body',
            '<div id="item-123" class="item">Hello, World!</div>\n',
            item=item
        )

    def test_5(self):
        self.assertHTML(
            '''
#content
  .left.column
    %h2 Welcome to our site!
    %p Info.
  .right.column
    Right content.
            '''.strip(),
            '''
<div id="content">
    <div class="left column">
        <h2>Welcome to our site!</h2>
        <p>Info.</p>
    </div>
    <div class="right column">
        Right content.
    </div>
</div>
            '''.strip() + '\n')


class TestHamlReference(Base):
    
    def test_plain_text_escaping(self):
        """See: http://haml-lang.com/docs/yardoc/file.HAML_REFERENCE.html#escaping_"""
        self.assertHTML(
            '''
%title
  = title
  \= title
            '''.strip(),
            '''
<title>
    MyPage
    = title
</title>
            '''.strip() + '\n', title='MyPage')

    def test_element_name(self):
        """See: http://haml-lang.com/docs/yardoc/file.HAML_REFERENCE.html#element_name_"""
        self.assertHTML(
            '''
%one
  %two
    %three Hey there
            '''.strip(),
            '''
<one>
    <two>
        <three>Hey there</three>
    </two>
</one>
            '''.strip() + '\n')

    def test_self_closing_tags(self):
        """See: http://haml-lang.com/docs/yardoc/file.HAML_REFERENCE.html#selfclosing_tags_"""
        self.assertHTML(
            '''
%br/
%meta(**{'http-equiv': 'Content-Type', 'content': 'text/html'})/
            '''.strip(),
            '''
<br />
<meta http-equiv="Content-Type" content="text/html" />
            '''.strip() + '\n')
        self.assertHTML(
            '''
%br
%meta(**{'http-equiv': 'Content-Type', 'content': 'text/html'})
            '''.strip(),
            '''
<br />
<meta http-equiv="Content-Type" content="text/html" />
            '''.strip() + '\n')

    def test_whitespace_removal_1(self):
        """See: http://haml-lang.com/docs/yardoc/file.HAML_REFERENCE.html#whitespace_removal__and_"""
        self.assertHTML(
            '''
%blockquote<
    %div
        Foo!
            '''.strip(),
            '''
<blockquote><div>
    Foo!
</div></blockquote>
            '''.strip() + '\n')

    def test_whitespace_removal_2(self):
        """See: http://haml-lang.com/docs/yardoc/file.HAML_REFERENCE.html#whitespace_removal__and_"""
        self.assertHTML(
            '''
%img
%img>
%img
            '''.strip(),
            '''
<img /><img /><img />
            '''.strip() + '\n')

#     def test_whitespace_removal_3(self):
#         """See: http://haml-lang.com/docs/yardoc/file.HAML_REFERENCE.html#whitespace_removal__and_"""
#         self.assertHTML(
#             '''
# %p<= "Foo\nBar"
#             '''.strip(),
#             '''
# <p>Foo
# Bar</p>
#             '''.strip() + '\n')

    def test_whitespace_removal_4(self):
        """See: http://haml-lang.com/docs/yardoc/file.HAML_REFERENCE.html#whitespace_removal__and_"""
        self.assertHTML(
            '''
%img
%pre><
    foo
    bar
%img
            '''.strip(),
            '''
<img /><pre>foo
bar</pre><img />
            '''.strip() + '\n')

    def test_html_comments_1(self):
        """See: http://haml-lang.com/docs/yardoc/file.HAML_REFERENCE.html#html_comments_"""
        self.assertHTML(
            '''
%peanutbutterjelly
  / This is the peanutbutterjelly element
  I like sandwiches!
            '''.strip(),
            '''
<peanutbutterjelly>
    <!-- This is the peanutbutterjelly element -->
    I like sandwiches!
</peanutbutterjelly>
            '''.strip() + '\n')
            
    def test_html_comments_2(self):
        """See: http://haml-lang.com/docs/yardoc/file.HAML_REFERENCE.html#html_comments_"""
        self.assertHTML(
            '''
/
  %p This doesn't render...
  %div
    %h1 Because it's commented out!
            '''.strip(),
            '''
<!--
    <p>This doesn't render...</p>
    <div>
        <h1>Because it's commented out!</h1>
    </div>
-->
            '''.strip() + '\n')
    
    def test_html_conditional_comments(self):
        """See: http://haml-lang.com/docs/yardoc/file.HAML_REFERENCE.html#html_comments_"""
        self.assertHTML(
            '''
/[if IE]
  %a(href='http://www.mozilla.com/en-US/firefox/')
    %h1 Get Firefox
            '''.strip(),
            '''
<!--[if IE]>
    <a href="http://www.mozilla.com/en-US/firefox/">
        <h1>Get Firefox</h1>
    </a>
<![endif]-->
            '''.strip() + '\n')    
    
    
                
if __name__ == '__main__':
    main()