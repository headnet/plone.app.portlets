from zope.interface import implements
from zope.component import getUtility, getMultiAdapter

from Acquisition import aq_inner

from plone.app.kss.interfaces import IPloneKSSView
from plone.app.kss.plonekssview import PloneKSSView as base

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletManagerRenderer

from plone.portlets.utils import unhashPortletInfo
from plone.app.portlets.utils import assignment_mapping_from_key

from plone.app.portlets.interfaces import IPortletPermissionChecker


class PortletManagerKSS(base):
    """Opertions on portlets done using KSS
    """
    implements(IPloneKSSView)

    def move_portlet_up(self, portlethash, viewname):
        info = unhashPortletInfo(portlethash)    
        assignments = assignment_mapping_from_key(self.context, 
                        info['manager'], info['category'], info['key'])
        
        IPortletPermissionChecker(assignments.__of__(aq_inner(self.context)))()
        
        keys = list(assignments.keys())
        name = info['name']
        idx = keys.index(name)
        del keys[idx]
        keys.insert(idx-1, name)
        assignments.updateOrder(keys)
        
        return self._render_column(info, viewname)
        
        
    def move_portlet_down(self, portlethash, viewname):
        info = unhashPortletInfo(portlethash)
        assignments = assignment_mapping_from_key(self.context, 
                        info['manager'], info['category'], info['key'])
        
        IPortletPermissionChecker(assignments.__of__(aq_inner(self.context)))()
        
        keys = list(assignments.keys())
        name = info['name']
        idx = keys.index(name)
        del keys[idx]
        keys.insert(idx+1, name)
        assignments.updateOrder(keys)
        
        return self._render_column(info, viewname)
        
    def delete_portlet(self, portlethash, viewname):
        info = unhashPortletInfo(portlethash)
        assignments = assignment_mapping_from_key(self.context, 
                        info['manager'], info['category'], info['key'])
                        
        IPortletPermissionChecker(assignments.__of__(aq_inner(self.context)))()
        
        del assignments[info['name']]
        return self._render_column(info, viewname)
        
                
    def _render_column(self, info, view_name):
        ksscore = self.getCommandSet('core')
        selector = ksscore.getCssSelector('div#portletmanager-' + info['manager'].replace('.', '-'))
        
        context = aq_inner(self.context)
        request = aq_inner(self.request)
        view = getMultiAdapter((context, request), name=view_name)
        manager = getUtility(IPortletManager, name=info['manager'])
        
        request['key'] = info['key']
        
        request['viewname'] = view_name
        renderer = getMultiAdapter((context, request, view, manager,),
                                   IPortletManagerRenderer)
        renderer.update()
        ksscore.replaceInnerHTML(selector, renderer.__of__(context).render())
        return self.render()


class DragDropManagerKSS(base):
    """Opertions on portlets done using KSS
    """
    implements(IPloneKSSView)
    
    def drop_portlet(self, portlethash, dropContainer, dropIndex=None):
        if dropIndex is not None:
            dropIndex = int(dropIndex)
        info = unhashPortletInfo(portlethash)
        context = aq_inner(self.context)
        request = aq_inner(self.request)        
        # Dropping a portlet can happen in two cases:
        if info['manager'] != dropContainer:
            # 1. The portlet is moved from one portletmanager to another
            colmover = getMultiAdapter((context, request),
                                       name='move-portlet-to-column')
            colmover.move_portlet_to_column(portlethash, dropContainer,
                                            after=dropIndex)
            
        elif info['manager'] == dropContainer:
            # 2. The portlet is moved ordering within one portletmager
            sorter = getMultiAdapter((context, request),
                                     name='update-portlet-order')
            sorter.update_portlet_order(info['name'], dropIndex)
        else:
            raise AttributeError
        return self.render()