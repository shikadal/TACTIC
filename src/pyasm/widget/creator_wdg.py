###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['CreateSelectWdg', 'CreateSelectAction']

from pyasm.common import UserException
from pyasm.web import *
from pyasm.search import Search
from pyasm.command import DatabaseAction
from input_wdg import *
from icon_wdg import IconWdg
from web_wdg import HintWdg


class CreateSelectWdg(AjaxWdg, BaseInputWdg):

    ID = "CreateSelectWdg"
    SELECT_NAME = "creator_select"
    SELECT_ITEMS = 'select_items'
    DELETE_MODE = "delete_mode"
    NEW_ITEM = 'new_item'
    NEW_ITEM_LABEL = 'new_item_label'
    EMPTY = "EMPTY"
    TYPE = "TYPE"

    def __init__(my,name=None, value=None ):
        my.items = []
        my.new_item = ''
        my.search_key = ''
        my.col_name = ''
        my.type_select_val = ''
        super(CreateSelectWdg, my).__init__()

    
    def init_cgi(my):
    
        my.search_key = my.get_search_key()

        col_name = my.web.get_form_value('col_name')
        items = my.web.get_form_value('%s|%s' %(col_name, my.SELECT_ITEMS))
        delimiter = my.get_delimiter()
        if items:
            my.items = items.split(delimiter)
        my.new_item = my.web.get_form_value(my.NEW_ITEM)

        my.type_select_val = my.web.get_form_value(my.TYPE)
        
    def init_setup(my):
       
        hidden = HiddenWdg(my.DELETE_MODE)
        my.add_ajax_input(hidden)
        hidden = HiddenWdg(my.NEW_ITEM)
        my.add_ajax_input(hidden)
        hidden = HiddenWdg(my.NEW_ITEM_LABEL)
        my.add_ajax_input(hidden)
        hidden = HiddenWdg('search_type')
        my.add_ajax_input(hidden)
        hidden = HiddenWdg('search_id')
        my.add_ajax_input(hidden)
       
        if my.is_from_ajax():
            col_name = my.web.get_form_value('col_name')
        else:
            col_name = my.get_name()
        my.col_name = HiddenWdg('col_name', col_name)
        my.add_ajax_input(my.col_name)
        
        my.select_items = HiddenWdg('%s|%s' %(col_name, my.SELECT_ITEMS))
        my.add_ajax_input(my.select_items)

    def get_search_key(my):
        search_key = '%s|%s' % (my.web.get_form_value('search_type'), \
            my.web.get_form_value('search_id'))
        return search_key

    def get_my_sobject(my):
        sobject = my.get_current_sobject()
        if not my.search_key:
            search_id = my.web.get_form_value('search_id')
            if search_id != '-1':
                my.search_key = my.get_search_key()
                sobject = Search.get_by_search_key(my.search_key)
        return sobject
        

    def get_delimiter(my):
        return '|'

    def get_display(my):
        delimiter = my.get_delimiter()

        my.init_setup()
        sobject = my.get_my_sobject()

        select_items_name = '%s|%s' %(my.col_name.get_value(), my.SELECT_ITEMS)
        my.set_ajax_top_id(my.ID)
        widget = DivWdg(id=my.ID)
        # mode select
        mode_cb = FilterCheckboxWdg('display_mode', label='simple view', css='small')
        
        

        # return simple widget if selected
        if mode_cb.is_checked(False):
            mode_cb.set_checked()

            type_select = SelectWdg(my.TYPE, label='Type: ')
            type_select.set_option('values','sequence|map|string')
            type = my.get_my_sobject().get_value('type')
            if type:
                type_select.set_value(type)
            widget.add(type_select)
            widget.add(HtmlElement.br(2))
            text = TextWdg(select_items_name)
            text.set_value(my.get_value())
            text.set_attr('size', '70')
            widget.add(text)
            widget.add(HtmlElement.br(2))
            widget.add(mode_cb)
            return widget

        if my.is_from_ajax():
            widget = Widget()
        else:
            widget.add_style('display', 'block')
        widget.add(my.col_name)
        widget.add(my.select_items) 

        items = []
        sobj_items= []
        prod_setting_type = 'sequence'

        if sobject:
            sobj_value = sobject.get_value(my.col_name.get_value())
            sobj_items = sobj_value.split(delimiter)
            prod_setting_type = sobject.get_value('type') 
       
        delete_widget = Widget()
        delete_mode = HiddenWdg('delete_mode')
        delete_mode.set_persist_on_submit()

        # only needs it for the first time
        # NOTE: this essentially prevents a sequence from having no value at all
        if not my.items and not delete_mode.get_value()=='true':
            items.extend(sobj_items)
        items.extend(my.items)
      
        my.type_select = my.get_type_select(prod_setting_type)
       
        my.select_items.set_value(delimiter.join(items)) 
       
        my.select = my.get_item_list(items)
        item_span = ''
        if my.type_select_val == 'map':
            item_span = my.get_map_wdg()
            my.select.add_empty_option( '-- Map items --', my.EMPTY)
        else:
            item_span = my.get_sequence_wdg()
            my.select.add_empty_option( '-- Sequence items --', my.EMPTY)


        # delete item button
        icon = IconWdg('Select an item to remove', icon=IconWdg.DELETE)
        icon.add_class('hand')
        drop_script = ["drop_item('%s')" %my.SELECT_NAME]
        drop_script.append(my.get_refresh_script())
        icon.add_event('onclick', ';'.join(drop_script) )
        delete_widget.add(delete_mode)
        delete_widget.add(icon)
       
        function_script = '''function append_item(select_name, new_item, new_item_extra)
            {
                var new_item_val = get_elements(new_item).get_value()
                if (new_item_extra != null)
                    new_item_val = new_item_val + ':' + get_elements(new_item_extra).get_value()
                
                var items = get_elements('%s')
                var items_arr = new Array()
                var delimiter = '%s'
                if (items.get_value())
                    items_arr = items.get_value().split(delimiter)
                for (var i=0; i < items_arr.length; i++)
                {
                    if (new_item_val == items_arr[i])
                        return
                }

                var idx = document.form.elements[select_name].selectedIndex
                // skip the title item
                if (idx < 0)
                    idx = 0
                if (idx == 0)
                    idx = items_arr.length
                else
                    idx = idx - 1
                
                items_arr.splice(idx, 0, new_item_val)
                items.set_value(items_arr.join(delimiter))
            }
                '''% (select_items_name, delimiter)
        widget.add(HtmlElement.script(function_script))

        function_script = '''function drop_item(select_name)
            {
               
                var items = get_elements('%s')
                var items_arr = new Array()
                var delimiter = '%s'
                if (items.get_value())
                    items_arr = items.get_value().split(delimiter)

                var idx = document.form.elements[select_name].selectedIndex
                if (idx == 0 || idx == -1)
                {
                    alert('You need to pick an item to remove')
                    return
                }
                alert("'"+ items_arr[idx-1] + "' removed.")
                items_arr.splice(idx-1, 1)
                items.set_value(items_arr.join(delimiter))

                var delete_mode = get_elements('delete_mode')
                delete_mode.set_value('true')
            }
                '''% (select_items_name, delimiter)
        widget.add(HtmlElement.script(function_script))

        my.draw_widgets(widget, delete_widget, item_span)
        
        widget.add(HtmlElement.br(2))
        widget.add(mode_cb)
        my.add(widget)
        return super(CreateSelectWdg, my).get_display()

    def draw_widgets(my, widget, delete_widget, item_span):
        '''actually drawing the widgets'''
        widget.add(my.type_select)
        widget.add(SpanWdg(my.select, css='med'))
        widget.add(delete_widget)
        widget.add(HtmlElement.br(2))
        widget.add(item_span)

    def get_item_list(my, items):
        my.select = SelectWdg(my.SELECT_NAME)
        my.select.set_attr("size", '%s' %(len(items)+1))
        my.select.set_option('values', items)
        return my.select
        
    def get_type_select(my, item_type):
        type_select = SelectWdg(my.TYPE, label='Type: ')
        type_select.set_option('values','sequence|map|string')
        
        my.add_ajax_input(type_select)

        if my.type_select_val:
            type_select.set_value(my.type_select_val)
        else:
            type_select.set_value(item_type)
            my.type_select_val = item_type

        type_select.add_event('onchange', my.get_refresh_script(show_progress=False))
        return type_select

    def get_sequence_wdg(my):
        text_span = SpanWdg('New item ')
        text_span.add(HtmlElement.br())
        text = TextWdg(my.NEW_ITEM)
        text_span.add(text)

        button = my.get_sequence_button()
        text_span.add(button)
        return text_span

    def get_sequence_button(my):
        # add button
        widget = Widget()
        from pyasm.prod.web import ProdIconButtonWdg
        add = ProdIconButtonWdg('Add')
        script = ["append_item('%s','%s')" % (my.SELECT_NAME, my.NEW_ITEM )]
        script.append( my.get_refresh_script() )
        add.add_event('onclick', ';'.join(script))
        widget.add(add)

        hint = HintWdg('New item will be inserted before the currently selected item. '\
                'Click on [Edit/Close] to confirm the final change.', title='Tip') 
        widget.add(hint)
        return widget

    def get_map_wdg(my):
        text_span = SpanWdg('New [value] : [label] pair ')
        text_span.add(HtmlElement.br())
        text = TextWdg(my.NEW_ITEM)
        text_span.add(text)
        text_span.add(SpanWdg(':', css='small'))
        text = TextWdg(my.NEW_ITEM_LABEL)
        text_span.add(text)
        
        text_span.add(my.get_map_button())
        return text_span

    def get_map_button(my):
        widget = Widget()
        # add button
        from pyasm.prod.web import ProdIconButtonWdg
        add = ProdIconButtonWdg('Add')
        script = ["append_item('%s','%s','%s')" \
            % (my.SELECT_NAME, my.NEW_ITEM, my.NEW_ITEM_LABEL)]
        script.append( my.get_refresh_script() )
        add.add_event('onclick', ';'.join(script))
        widget.add(add)

        hint = HintWdg('New value:label pair will be inserted after the currently selected item.\
                Click on [Edit/Close] to confirm the final change.') 
        widget.add(hint)
        return widget

class CreateSelectAction(DatabaseAction):

    def check(my):
        my.web = WebContainer.get_web()
        my.items = my.web.get_form_value('%s|%s' %(my.name, CreateSelectWdg.SELECT_ITEMS))
        my.type = my.web.get_form_value(CreateSelectWdg.TYPE)

        
        if my.type == 'map' and ':' not in my.items:
            raise UserException('The values in the drop-down does not appear to be a map.\
                    Please choose "sequence" for Type and retry.') 
        return True

    def execute(my):
        
        my.sobject.set_value(my.name, my.items)
        my.sobject.set_value('type', my.type)
        my.sobject.commit()
