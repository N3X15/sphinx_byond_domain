# -*- coding: utf-8 -*-
"""
    sphinx.domains.byond
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    A domain for BYOND .dm scripts. Mostly just a tweaked JavaScript
    domain.

    :copyright: Copyright 2007-2014 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from sphinx import addnodes
from sphinx.domains import Domain, ObjType
from sphinx.locale import l_, _
from sphinx.directives import ObjectDescription
from sphinx.roles import XRefRole
from sphinx.domains.python import _pseudo_parse_arglist
from sphinx.util.nodes import make_refnode
from sphinx.util.docfields import Field, GroupedField, TypedField


class DMObject(ObjectDescription):
    """
    Description of a BYOND datum.
    """
    # : If set to ``True`` this object is callable and a `desc_parameterlist` is
    # : added
    has_arguments = False

    # : what is displayed right before the documentation entry
    display_prefix = None

    def handle_signature(self, sig, signode):
        sig = sig.strip()
        if '(' in sig and sig[-1:] == ')':
            prefix, arglist = sig.split('(', 1)
            arglist = arglist[:-1].strip()
        else:
            prefix = sig
            arglist = None

        absolute = False
        if prefix.startswith('/'):
            prefix = prefix[1:]
            absolute = True
            
        if '/' in prefix:
            nameprefix, name = prefix.rsplit('/', 1)
        else:
            nameprefix = None
            name = prefix
            
        if absolute:
            if nameprefix is None:
                nameprefix = '/'
            else:
                nameprefix = '/' + nameprefix.strip('/')

        objectname = self.env.temp_data.get('dm:object')
        if nameprefix:
            if objectname:
                # someone documenting the method of an attribute of the current
                # object? shouldn't happen but who knows...
                nameprefix = objectname + '/' + nameprefix.lstrip('/')
            fullname = nameprefix + '/' + name
        elif objectname:
            fullname = objectname + '/' + name
        else:
            # just a function or constructor
            objectname = ''
            fullname = name

        # fullname = '/' + fullname
        
        signode['object'] = objectname
        signode['fullname'] = fullname

        if self.display_prefix:
            signode += addnodes.desc_annotation(self.display_prefix,
                                                self.display_prefix)
        if nameprefix:
            signode += addnodes.desc_addname(nameprefix, nameprefix)
        signode += addnodes.desc_name(name, name)
        if self.has_arguments:
            if not arglist:
                signode += addnodes.desc_parameterlist()
            else:
                _pseudo_parse_arglist(signode, arglist)
        return fullname, nameprefix

    def add_target_and_index(self, name_obj, sig, signode):
        objectname = self.options.get(
            'object', self.env.temp_data.get('dm:object'))
        fullname = '/' + name_obj[0].lstrip('/')
        if fullname not in self.state.document.ids:
            signode['names'].append(fullname)
            signode['ids'].append(fullname)
            signode['first'] = not self.names
            self.state.document.note_explicit_target(signode)
            objects = self.env.domaindata['dm']['objects']
            if fullname in objects:
                self.env.warn(
                    self.env.docname,
                    'duplicate object description of %s, ' % fullname + 
                    'other instance in ' + 
                    self.env.doc2path(objects[fullname][0]),
                    self.lineno)
            objects[fullname] = self.env.docname, self.objtype

        indextext = self.get_index_text(objectname, name_obj)
        if indextext:
            self.indexnode['entries'].append(('single', indextext,
                                              fullname,
                                              ''))

    def get_index_text(self, objectname, name_obj):
        name, obj = name_obj
        if self.objtype == 'proc':
            return _('%s() (%s proc)') % (name, obj)
        if self.objtype == 'verb':
            return _('%s() (%s verb)') % (name, obj)
        elif self.objtype == 'atom':
            return _('%s() (atom)') % name
        elif self.objtype == 'var':
            return _('%s (%s attribute)') % (name, obj)
        return ''


class DMCallable(DMObject):
    """Description of a DM proc or verb."""
    has_arguments = True

    doc_field_types = [
        TypedField('arguments', label=l_('Arguments'),
                   names=('argument', 'arg', 'parameter', 'param'),
                   typerolename='proc', typenames=('paramtype', 'type')),
        Field('returnvalue', label=l_('Returns'), has_arg=False,
              names=('returns', 'return')),
    ]

class DMProc(DMCallable):
    display_prefix = 'proc '
    
class DMVerb(DMCallable):
    display_prefix = 'verb '

class DMConstructor(DMCallable):
    """Like a callable but with a different prefix."""
    display_prefix = 'atom '


class DMXRefRole(XRefRole):
    def process_link(self, env, refnode, has_explicit_title, title, target):
        # basically what sphinx.domains.python.PyXRefRole does
        refnode['dm:object'] = env.temp_data.get('dm:object')
        if not has_explicit_title:
            title = '/' + title.lstrip('/')
            target = target.lstrip('~')
            if title[0:1] == '~':
                title = title[1:]
                dot = title.rfind('/')
                if dot != -1:
                    # title = title[dot+1:]
                    title = title[dot:]
        if target[0:1] == '/':
            # target = target[1:]
            refnode['refspecific'] = True
        return title, target


class BYONDDomain(Domain):
    """BYOND language domain."""
    name = 'dm'
    label = 'BYOND'
    # if you add a new object type make sure to edit JSObject.get_index_string
    object_types = {
        'proc': ObjType(l_('proc'), 'proc'),
        'verb': ObjType(l_('verb'), 'verb'),
        'atom': ObjType(l_('atom'), 'atom'),
        'var':  ObjType(l_('var'), 'var')
    }
    directives = {
        'proc': DMProc,
        'verb': DMVerb,
        'atom': DMConstructor,
        'var':  DMObject,
    }
    roles = {
        'p': DMXRefRole(fix_parens=True),
        # 'v': DMXRefRole(fix_parens=True),
        'a': DMXRefRole(fix_parens=True),
        'v':  DMXRefRole(),
    }
    initial_data = {
        'objects': {},  # fullname -> docname, objtype
    }

    def clear_doc(self, docname):
        for fullname, (fn, _) in self.data['objects'].items():
            if fn == docname:
                del self.data['objects'][fullname]

    def find_obj(self, env, obj, name, typ, searchorder=0):
        if name[-2:] == '()':
            name = name[:-2]
        objects = self.data['objects']
        newname = None
        if searchorder == 1:
            if obj and obj + '/' + name in objects:
                newname = obj + '/' + name
            else:
                newname = name
        else:
            if name in objects:
                newname = name
            elif obj and obj + '/' + name in objects:
                newname = obj + '/' + name
        #if newname:
        #    newname=newname.replace('//','/')
        return newname, objects.get(newname)

    def resolve_xref(self, env, fromdocname, builder, typ, target, node,
                     contnode):
        objectname = node.get('dm:object')
        searchorder = node.hasattr('refspecific') and 1 or 0
        name, obj = self.find_obj(env, objectname, target, typ, searchorder)
        if not obj:
            return None
        return make_refnode(builder, fromdocname, obj[0],
                            name, contnode, name)

    def get_objects(self):
        for refname, (docname, type) in self.data['objects'].iteritems():
            yield refname, refname, type, docname, refname, 1

def setup(app):
    app.add_domain(BYONDDomain)
